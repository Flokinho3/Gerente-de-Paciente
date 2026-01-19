"""
SQLite-based database layer for managing paciente data.
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def bool_to_int(value: Optional[bool]) -> int:
    return 1 if value else 0


def int_to_bool(value: Optional[int]) -> bool:
    return bool(value)


class Database:
    def __init__(self, db_path: Optional[str] = None):
        # Detecta se está rodando como executável PyInstaller
        import sys
        if getattr(sys, 'frozen', False):
            # Executável: usa diretório do executável
            base_dir = os.path.dirname(sys.executable)
        else:
            # Modo desenvolvimento: usa diretório do script
            base_dir = os.path.dirname(__file__)
        
        self.db_path = db_path or os.path.join(base_dir, 'data', 'pacientes.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        ddl = """
        CREATE TABLE IF NOT EXISTS pacientes (
            id TEXT PRIMARY KEY,
            nome_gestante TEXT NOT NULL,
            unidade_saude TEXT,
            data_salvamento TEXT,
            inicio_pre_natal_antes_12s INTEGER,
            consultas_pre_natal INTEGER,
            vacinas_completas TEXT,
            plano_parto INTEGER,
            participou_grupos INTEGER,
            avaliacao_odontologica INTEGER,
            estratificacao INTEGER,
            cartao_pre_natal_completo INTEGER,
            arquivo_origem TEXT
        )
        """
        self.conn.execute(ddl)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nome ON pacientes(nome_gestante)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_unidade ON pacientes(unidade_saude)")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        return {
            'id': row['id'],
            'data_salvamento': row['data_salvamento'],
            'identificacao': {
                'nome_gestante': row['nome_gestante'],
                'unidade_saude': row['unidade_saude']
            },
            'avaliacao': {
                'inicio_pre_natal_antes_12s': int_to_bool(row['inicio_pre_natal_antes_12s']),
                'consultas_pre_natal': row['consultas_pre_natal'],
                'vacinas_completas': row['vacinas_completas'] or '',
                'plano_parto': int_to_bool(row['plano_parto']),
                'participou_grupos': int_to_bool(row['participou_grupos']),
                'avaliacao_odontologica': int_to_bool(row['avaliacao_odontologica']),
                'estratificacao': int_to_bool(row['estratificacao']),
                'cartao_pre_natal_completo': int_to_bool(row['cartao_pre_natal_completo'])
            },
            'arquivo_origem': row['arquivo_origem']
        }

    def gerar_id(self, nome: str, data_salvamento: Optional[str] = None) -> str:
        if not data_salvamento:
            data_salvamento = datetime.now().strftime('%Y%m%d_%H%M%S')
        else:
            data_salvamento = data_salvamento.replace(' ', '_').replace(':', '').replace('-', '')
        nome_formatado = nome.strip().replace(' ', '_')
        return f"{nome_formatado}_{data_salvamento}"

    def inserir_registro(
        self,
        paciente_id: str,
        paciente_data: Dict,
        arquivo_origem: Optional[str] = None,
        data_salvamento: Optional[str] = None
    ) -> Dict:
        if not data_salvamento:
            data_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        identificacao = paciente_data.get('identificacao', {})
        avaliacao = paciente_data.get('avaliacao', {})
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO pacientes (
                id, nome_gestante, unidade_saude, data_salvamento,
                inicio_pre_natal_antes_12s, consultas_pre_natal, vacinas_completas,
                plano_parto, participou_grupos, avaliacao_odontologica,
                estratificacao, cartao_pre_natal_completo, arquivo_origem
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                paciente_id,
                identificacao.get('nome_gestante', '').strip(),
                identificacao.get('unidade_saude', '').strip(),
                data_salvamento,
                bool_to_int(avaliacao.get('inicio_pre_natal_antes_12s')),
                avaliacao.get('consultas_pre_natal', 0),
                avaliacao.get('vacinas_completas', ''),
                bool_to_int(avaliacao.get('plano_parto')),
                bool_to_int(avaliacao.get('participou_grupos')),
                bool_to_int(avaliacao.get('avaliacao_odontologica')),
                bool_to_int(avaliacao.get('estratificacao')),
                bool_to_int(avaliacao.get('cartao_pre_natal_completo')),
                arquivo_origem
            )
        )
        self.conn.commit()
        return {
            'success': True,
            'message': 'Paciente registrado com sucesso',
            'id': paciente_id
        }

    def adicionar_paciente(self, paciente_data: Dict) -> Dict:
        nome = paciente_data.get('identificacao', {}).get('nome_gestante', '').strip()
        data_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        paciente_id = self.gerar_id(nome, data_salvamento)
        resultado = self.inserir_registro(paciente_id, paciente_data, data_salvamento=data_salvamento)
        return resultado

    def buscar_paciente(self, paciente_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def buscar_pacientes(self, filtro: Optional[Dict] = None) -> List[Dict]:
        query = "SELECT * FROM pacientes"
        params: Tuple[str, ...] = ()
        if filtro:
            clauses = []
            if 'nome' in filtro:
                clauses.append("LOWER(nome_gestante) LIKE ?")
                params += (f"%{filtro['nome'].lower()}%",)
            if 'unidade_saude' in filtro:
                clauses.append("LOWER(unidade_saude) LIKE ?")
                params += (f"%{filtro['unidade_saude'].lower()}%",)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def atualizar_paciente(self, paciente_id: str, paciente_data: Dict) -> Dict:
        if not self.buscar_paciente(paciente_id):
            return {'success': False, 'message': 'Paciente não encontrado'}
        return self.inserir_registro(paciente_id, paciente_data)

    def obter_todos_pacientes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes ORDER BY data_salvamento DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def obter_estatisticas(self) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes")
        rows = cursor.fetchall()
        stats = {
            'total_pacientes': len(rows),
            'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
            'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
            'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
            'plano_parto': {'sim': 0, 'nao': 0},
            'participou_grupos': {'sim': 0, 'nao': 0}
        }
        for row in rows:
            inicio = row['inicio_pre_natal_antes_12s']
            stats['inicio_pre_natal_antes_12s']['sim'] += 1 if inicio == 1 else 0
            stats['inicio_pre_natal_antes_12s']['nao'] += 1 if inicio == 0 else 0
            num_consultas = row['consultas_pre_natal'] or 0
            stats['consultas_pre_natal']['mais_6'] += 1 if num_consultas >= 6 else 0
            stats['consultas_pre_natal']['ate_6'] += 1 if num_consultas < 6 else 0
            vacinas = (row['vacinas_completas'] or '').lower()
            if 'completa' in vacinas:
                stats['vacinas_completas']['completa'] += 1
            elif 'incompleta' in vacinas:
                stats['vacinas_completas']['incompleta'] += 1
            else:
                stats['vacinas_completas']['nao_avaliado'] += 1
            stats['plano_parto']['sim'] += 1 if row['plano_parto'] == 1 else 0
            stats['plano_parto']['nao'] += 1 if row['plano_parto'] == 0 else 0
            stats['participou_grupos']['sim'] += 1 if row['participou_grupos'] == 1 else 0
            stats['participou_grupos']['nao'] += 1 if row['participou_grupos'] == 0 else 0
        return stats

    def limpar_todos_dados(self) -> None:
        self.conn.execute("DELETE FROM pacientes")
        self.conn.commit()
        return {'success': True, 'message': 'Todos os dados foram excluídos com sucesso'}

    def deletar_paciente(self, paciente_id: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            return {'success': False, 'message': 'Paciente não encontrado'}
        return {'success': True, 'message': 'Paciente deletado com sucesso'}

    def criar_backup(self) -> Dict:
        pacientes = self.obter_todos_pacientes()
        return {
            'success': True,
            'backup': pacientes,
            'data_backup': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def restaurar_backup(self, backup_data: List[Dict]) -> Dict:
        if not isinstance(backup_data, list):
            return {'success': False, 'message': 'Estrutura do backup inválida'}
        self.conn.execute("DELETE FROM pacientes")
        self.conn.commit()
        inseridos = 0
        for registro in backup_data:
            nome = registro.get('identificacao', {}).get('nome_gestante', '').strip()
            if not nome:
                continue
            paciente_id = registro.get('id') or self.gerar_id(nome)
            data_salvamento = registro.get('data_salvamento', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            resultado = self.inserir_registro(
                paciente_id,
                registro,
                arquivo_origem=registro.get('arquivo_origem'),
                data_salvamento=data_salvamento
            )
            if resultado['success']:
                inseridos += 1
        return {
            'success': True,
            'message': f'Backup restaurado com sucesso ({inseridos} registros)',
            'total_pacientes': inseridos
        }


# Instância global do banco de dados
db = Database()
