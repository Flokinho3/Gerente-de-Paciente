"""
Cliente para sincronização com VPS
Permite upload, download e sincronização de dados com o servidor VPS central
"""
import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from gerente.env_loader import load_env

load_env()


def _flatten_record(record: Dict) -> Dict:
    """Converte campos aninhados (dict) para JSON strings para compatibilidade com SQLite"""
    flattened = {}
    for key, value in record.items():
        if isinstance(value, dict):
            flattened[key] = json.dumps(value, ensure_ascii=False, default=str)
        elif isinstance(value, list):
            flattened[key] = json.dumps(value, ensure_ascii=False, default=str)
        else:
            flattened[key] = value
    return flattened


def _unflatten_record(record: Dict) -> Dict:
    """Restaura campos JSON strings para dicionários aninhados"""
    unflattened = {}
    for key, value in record.items():
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    unflattened[key] = parsed
                else:
                    unflattened[key] = value
            except (json.JSONDecodeError, TypeError):
                unflattened[key] = value
        else:
            unflattened[key] = value
    return unflattened


class VPSClient:
    """Cliente para sincronização com servidor VPS"""

    def __init__(self, vps_url: str = None, password: str = None):
        self.vps_url = vps_url or os.getenv('VPS_URL', '').strip()
        self.password = password or os.getenv('VPS_PASSWORD', '').strip()
        if not self.vps_url:
            raise ValueError('VPS_URL não configurado')
        if not self.password:
            raise ValueError('VPS_PASSWORD não configurado')
        self.session = requests.Session()
        self.session.headers.update({'X-API-Password': self.password})

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Executa requisição para a VPS"""
        url = f"{self.vps_url.rstrip('/')}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            
            # Normalização da resposta
            data = response.json() if response.content else {}
            
            # Se for uma lista, retornamos diretamente (ex: /api/data/<tabela>)
            if isinstance(data, list):
                return data
            
            # Se for um dicionário, garantimos a presença da chave 'success'
            if isinstance(data, dict):
                # Se já tem success, respeita
                if 'success' in data:
                    return data
                
                # Injeta success=True se o status for 'ok' ou 'success' ou se o HTTP for 2xx
                if data.get('status') in ['ok', 'success'] or response.status_code < 300:
                    data['success'] = True
            
            return data
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Timeout na conexão com VPS"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Não foi possível conectar à VPS"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "message": f"Erro HTTP: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

    def get_status(self) -> Dict:
        """Obtém status da VPS"""
        return self._request('GET', '/api/vps/status')

    def compare_tables(self, tables: List[str] = None) -> Dict:
        """Compara contagem de tabelas locais vs VPS"""
        if tables is None:
            tables = ['pacientes', 'agendamentos']
        return self._request('POST', '/api/vps/compare', json={"tables": tables})

    def upload_database(self, db_path: str) -> Dict:
        """Envia arquivo do banco de dados para VPS"""
        if not os.path.exists(db_path):
            return {"success": False, "message": "Arquivo de banco não encontrado"}

        try:
            with open(db_path, 'rb') as f:
                files = {'file': (os.path.basename(db_path), f, 'application/octet-stream')}
                url = f"{self.vps_url.rstrip('/')}/api/vps/upload"
                response = self.session.post(url, files=files, timeout=60)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"success": False, "message": f"Erro no upload: {str(e)}"}

    def download_database(self, output_path: str = None) -> Dict:
        """Baixa banco de dados da VPS"""
        try:
            url = f"{self.vps_url.rstrip('/')}/api/vps/download"
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            if output_path is None:
                output_path = os.path.join(os.path.dirname(__file__), 'data', 'pacientes.db')

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

            return {"success": True, "path": output_path, "size": len(response.content)}
        except Exception as e:
            return {"success": False, "message": f"Erro no download: {str(e)}"}

    def sync_table(self, table: str, data: List[Dict]) -> Dict:
        """Sincroniza múltiplos registros para uma tabela"""
        flattened_data = [_flatten_record(record) for record in data]
        return self._request('POST', '/api/vps/sync', json={
            "table": table,
            "data": flattened_data
        })

    def get_table_data(self, table: str) -> List[Dict]:
        """Obtém dados de uma tabela"""
        result = self._request('GET', f'/api/data/{table}')
        return result if isinstance(result, list) else []

    def add_or_update_record(self, table: str, record: Dict) -> Dict:
        """Adiciona ou modifica um registro"""
        return self._request('POST', f'/api/data/{table}', json=record)

    def delete_record(self, table: str, record_id: str) -> Dict:
        """Exclui um registro"""
        return self._request('DELETE', f'/api/data/{table}/{record_id}')

    def sync_pacientes(self, pacientes: List[Dict]) -> Dict:
        """Sincroniza lista de pacientes"""
        return self.sync_table('pacientes', pacientes)

    def sync_agendamentos(self, agendamentos: List[Dict]) -> Dict:
        """Sincroniza lista de agendamentos"""
        return self.sync_table('agendamentos', agendamentos)

    def get_pacientes_from_vps(self) -> List[Dict]:
        """Obtém todos os pacientes da VPS"""
        data = self.get_table_data('pacientes')
        return [_unflatten_record(record) for record in data]

    def get_agendamentos_from_vps(self) -> List[Dict]:
        """Obtém todos os agendamentos da VPS"""
        data = self.get_table_data('agendamentos')
        return [_unflatten_record(record) for record in data]

    def verificar_pendentes(self, pacientes_locais: List[Dict], agendamentos_locais: List[Dict] = None) -> Dict:
        """Verifica quais dados locais ainda não estão na VPS"""
        compare = self.compare_tables()
        if not compare.get('success', False):
            return {"success": False, "message": compare.get('message')}

        pacientes_cloud = compare.get('pacientes', {}).get('count', 0)
        agendamentos_cloud = compare.get('agendamentos', {}).get('count', 0)

        pacientes_ids_cloud = set()
        agendamentos_ids_cloud = set()

        if pacientes_cloud > 0:
            for p in self.get_pacientes_from_vps():
                if 'id' in p:
                    pacientes_ids_cloud.add(p['id'])

        if agendamentos_cloud is None or agendamentos_cloud > 0:
            if agendamentos_locais is not None:
                for a in self.get_agendamentos_from_vps():
                    if 'id' in a:
                        agendamentos_ids_cloud.add(a['id'])

        pacientes_locais_ids = {p.get('id') for p in pacientes_locais}
        agendamentos_locais_ids = {a.get('id') for a in (agendamentos_locais or [])}

        pacientes_pendentes = pacientes_locais_ids - pacientes_ids_cloud
        agendamentos_pendentes = agendamentos_locais_ids - agendamentos_ids_cloud

        return {
            "success": True,
            "pacientes": {
                "locais": len(pacientes_locais),
                "cloud": pacientes_cloud,
                "pendentes": len(pacientes_pendentes),
                "ids_pendentes": list(pacientes_pendentes)[:50]
            },
            "agendamentos": {
                "locais": len(agendamentos_locais or []),
                "cloud": agendamentos_cloud,
                "pendentes": len(agendamentos_pendentes),
                "ids_pendentes": list(agendamentos_pendentes)[:50]
            }
        }


_vps_client = None


def get_vps_client() -> Optional[VPSClient]:
    """Retorna instância única do cliente VPS"""
    global _vps_client
    if _vps_client is None:
        try:
            _vps_client = VPSClient()
        except Exception:
            return None
    return _vps_client


if __name__ == "__main__":
    client = get_vps_client()
    if client:
        status = client.get_status()
        print("Status VPS:", status)
    else:
        print("Erro ao conectar com VPS")
