import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class BackupMixin:
    def limpar_todos_dados(self) -> Dict:
        # Excluir agendamentos primeiro (devido à foreign key)
        self.conn.execute("DELETE FROM agendamentos")
        # Excluir pacientes
        self.conn.execute("DELETE FROM pacientes")
        self.conn.commit()
        return {'success': True, 'message': 'Todos os dados foram excluídos com sucesso'}

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
            if not nome: continue
            paciente_id = registro.get('id') or self.gerar_id(nome)
            resultado = self.inserir_registro(paciente_id, registro,
                arquivo_origem=registro.get('arquivo_origem'),
                data_salvamento=registro.get('data_salvamento', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            if resultado['success']: inseridos += 1
        return {'success': True, 'message': f'Backup restaurado com sucesso ({inseridos} registros)', 'total_pacientes': inseridos}

    def comparar_backup(self, backup_data: List[Dict]) -> Dict:
        try:
            if not isinstance(backup_data, list):
                return {'success': False, 'message': 'Estrutura do backup inválida', 'comparison': None}
            
            pacientes_atuais = self.obter_todos_pacientes()
            db_pacientes_dict = {p['id']: p for p in pacientes_atuais}
            
            novos, modificados, identicos, removidos = [], [], [], []
            backup_ids = set()
            
            for backup_record in backup_data:
                paciente_id = backup_record.get('id')
                if not paciente_id: continue
                backup_ids.add(paciente_id)
                
                if paciente_id not in db_pacientes_dict:
                    novos.append({'id': paciente_id, 'nome_gestante': backup_record.get('identificacao', {}).get('nome_gestante', ''), 'backup_data': backup_record})
                else:
                    dif = self._comparar_registros_detalhado(db_pacientes_dict[paciente_id], backup_record)
                    if dif: modificados.append({'id': paciente_id, 'nome_gestante': backup_record.get('identificacao', {}).get('nome_gestante', ''), 'diferencas': dif, 'db_data': db_pacientes_dict[paciente_id], 'backup_data': backup_record})
                    else: identicos.append({'id': paciente_id, 'nome_gestante': backup_record.get('identificacao', {}).get('nome_gestante', '')})
            
            for pid, db_rec in db_pacientes_dict.items():
                if pid not in backup_ids:
                    removidos.append({'id': pid, 'nome_gestante': db_rec.get('identificacao', {}).get('nome_gestante', ''), 'db_data': db_rec})
            
            return {'success': True, 'comparison': {'novos': novos, 'modificados': modificados, 'identicos': identicos, 'removidos': removidos,
                'resumo': {'total_backup': len(backup_data), 'total_db': len(pacientes_atuais), 'total_novos': len(novos), 'total_modificados': len(modificados), 'total_identicos': len(identicos), 'total_removidos': len(removidos)}}}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao comparar backup: {str(e)}', 'comparison': None}

    def adicionar_item_ignorado(self, paciente_id: str, dados_backup: Dict, origem_backup: str, motivo: Optional[str] = None) -> Dict:
        try:
            item_id = str(uuid.uuid4())
            data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_expiracao = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
            payload = json.dumps(dados_backup, ensure_ascii=False)
            self.conn.execute("INSERT INTO itens_ignorados (id, paciente_id, dados_backup, tipo_acao, data_criacao, data_expiracao, motivo, origem_backup) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (item_id, paciente_id, payload, 'ignorado', data_criacao, data_expiracao, motivo, origem_backup))
            self.conn.commit()
            return {'success': True, 'id': item_id, 'data_expiracao': data_expiracao}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def listar_itens_ignorados(self, apenas_nao_expirados: bool = True, origem_backup: Optional[str] = None) -> List[Dict]:
        try:
            query = "SELECT * FROM itens_ignorados WHERE 1=1"
            params = []
            if apenas_nao_expirados:
                query += " AND data_expiracao > ?"
                params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if origem_backup:
                query += " AND origem_backup = ?"
                params.append(origem_backup)
            query += " ORDER BY data_criacao DESC"
            rows = self.conn.execute(query, params).fetchall()
            itens, now = [], datetime.now()
            for row in rows:
                exp_dt = datetime.strptime(row['data_expiracao'], '%Y-%m-%d %H:%M:%S')
                itens.append({'id': row['id'], 'paciente_id': row['paciente_id'], 'dados_backup': json.loads(row['dados_backup']) if row['dados_backup'] else {},
                    'tipo_acao': row['tipo_acao'], 'data_criacao': row['data_criacao'], 'data_expiracao': row['data_expiracao'], 'motivo': row['motivo'],
                    'origem_backup': row['origem_backup'], 'expirado': now > exp_dt, 'dias_restantes': max(0, (exp_dt - now).days)})
            return itens
        except Exception: return []

    def remover_item_ignorado(self, item_id: str) -> Dict:
        try:
            cursor = self.conn.execute("DELETE FROM itens_ignorados WHERE id = ?", (item_id,))
            self.conn.commit()
            return {'success': cursor.rowcount > 0}
        except Exception: return {'success': False}

    def limpar_itens_ignorados_expirados(self) -> Dict:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.execute("DELETE FROM itens_ignorados WHERE data_expiracao <= ?", (now,))
            self.conn.commit()
            return {'success': True, 'removidos': cursor.rowcount}
        except Exception: return {'success': False, 'removidos': 0}

    def restaurar_item_ignorado(self, item_id: str) -> Dict:
        try:
            row = self.conn.execute("SELECT * FROM itens_ignorados WHERE id = ?", (item_id,)).fetchone()
            if not row: return {'success': False}
            self.conn.execute("DELETE FROM itens_ignorados WHERE id = ?", (item_id,))
            self.conn.commit()
            return {'success': True, 'dados_backup': json.loads(row['dados_backup']) if row['dados_backup'] else {}}
        except Exception: return {'success': False}
