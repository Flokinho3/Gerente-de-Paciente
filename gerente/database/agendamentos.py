from datetime import datetime
from typing import Optional, Dict, List

class AgendamentoMixin:
    def criar_agendamento(self, agendamento_id: str, paciente_id: Optional[str], data_consulta: str,
                          hora_consulta: str, tipo_consulta: str = None, observacoes: str = None,
                          status: str = 'agendado', data_criacao: str = None, data_atualizacao: str = None,
                          pc_id: str = None, ultima_modificacao: str = None, versao: int = None) -> Dict:
        """Cria um novo agendamento"""
        try:
            if not data_criacao:
                data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not data_atualizacao:
                data_atualizacao = data_criacao
            if not ultima_modificacao:
                ultima_modificacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not pc_id:
                pc_id = self.pc_id
            if versao is None:
                versao = 1
            
            self.conn.execute("""
                INSERT INTO agendamentos 
                (id, paciente_id, data_consulta, hora_consulta, tipo_consulta, observacoes, status, data_criacao, data_atualizacao,
                 pc_id, ultima_modificacao, versao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (agendamento_id, paciente_id, data_consulta, hora_consulta, tipo_consulta, observacoes, status, data_criacao, data_atualizacao,
                  pc_id, ultima_modificacao, versao))
            self.conn.commit()
            return {'success': True, 'message': 'Agendamento criado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar agendamento: {str(e)}'}

    def listar_agendamentos(self, paciente_id: str = None, data_inicio: str = None, 
                           data_fim: str = None, status: str = None) -> List[Dict]:
        """Lista agendamentos com filtros opcionais"""
        try:
            query = """
                SELECT a.*, p.nome_gestante, p.unidade_saude
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                WHERE 1=1
            """
            params = []
            
            if paciente_id:
                query += " AND a.paciente_id = ?"
                params.append(paciente_id)
            
            if data_inicio:
                query += " AND a.data_consulta >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND a.data_consulta <= ?"
                params.append(data_fim)
            
            if status:
                query += " AND a.status = ?"
                params.append(status)
            
            if status != 'removido':
                query += " AND (a.status IS NULL OR a.status != 'removido')"
            
            query += " ORDER BY a.data_consulta ASC, a.hora_consulta ASC"
            
            cursor = self.conn.execute(query, params)
            rows = cursor.fetchall()
            
            agendamentos = []
            for row in rows:
                agendamento = {
                    'id': row['id'],
                    'paciente_id': row['paciente_id'],
                    'nome_gestante': row['nome_gestante'],
                    'unidade_saude': row['unidade_saude'],
                    'data_consulta': row['data_consulta'],
                    'hora_consulta': row['hora_consulta'],
                    'tipo_consulta': row['tipo_consulta'],
                    'observacoes': row['observacoes'],
                    'status': row['status'],
                    'data_criacao': row['data_criacao'],
                    'data_atualizacao': row['data_atualizacao']
                }
                sync_fields = ['pc_id', 'ultima_modificacao', 'versao', 'removido_em', 'removido_por']
                for field in sync_fields:
                    try:
                        if field in row.keys():
                            agendamento[field] = row[field]
                    except (KeyError, IndexError):
                        pass
                agendamentos.append(agendamento)
            
            return agendamentos
        except Exception:
            return []

    def obter_agendamento(self, agendamento_id: str) -> Optional[Dict]:
        """Obtém um agendamento específico"""
        try:
            cursor = self.conn.execute("""
                SELECT a.*, p.nome_gestante, p.unidade_saude
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                WHERE a.id = ?
            """, (agendamento_id,))
            row = cursor.fetchone()
            
            if row:
                agendamento = {
                    'id': row['id'],
                    'paciente_id': row['paciente_id'],
                    'nome_gestante': row['nome_gestante'],
                    'unidade_saude': row['unidade_saude'],
                    'data_consulta': row['data_consulta'],
                    'hora_consulta': row['hora_consulta'],
                    'tipo_consulta': row['tipo_consulta'],
                    'observacoes': row['observacoes'],
                    'status': row['status'],
                    'data_criacao': row['data_criacao'],
                    'data_atualizacao': row['data_atualizacao']
                }
                sync_fields = ['pc_id', 'ultima_modificacao', 'versao', 'removido_em', 'removido_por']
                for field in sync_fields:
                    try:
                        if field in row.keys():
                            agendamento[field] = row[field]
                    except (KeyError, IndexError):
                        pass
                return agendamento
            return None
        except Exception:
            return None

    def atualizar_agendamento(self, agendamento_id: str, paciente_id: str = None, data_consulta: str = None,
                               hora_consulta: str = None, tipo_consulta: str = None,
                               observacoes: str = None, status: str = None, data_atualizacao: str = None,
                               pc_id: str = None, ultima_modificacao: str = None) -> Dict:
        """Atualiza um agendamento existente"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT versao, status FROM agendamentos WHERE id = ?", (agendamento_id,))
            row = cursor.fetchone()
            
            if not row:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            versao_atual = row['versao'] if row['versao'] else 1
            nova_versao = versao_atual + 1
            status_atual = row['status'] if row['status'] else 'agendado'
            
            if status is not None and status_atual != 'conflito':
                novo_status = status
            else:
                novo_status = status_atual
            
            if not data_atualizacao:
                data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not ultima_modificacao:
                ultima_modificacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not pc_id:
                pc_id = self.pc_id
            
            updates = []
            params = []
            
            fields = {
                'paciente_id': paciente_id,
                'data_consulta': data_consulta,
                'hora_consulta': hora_consulta,
                'tipo_consulta': tipo_consulta,
                'observacoes': observacoes,
                'status': novo_status,
                'data_atualizacao': data_atualizacao,
                'pc_id': pc_id,
                'ultima_modificacao': ultima_modificacao,
                'versao': nova_versao
            }
            
            for field, value in fields.items():
                if value is not None:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            params.append(agendamento_id)
            query = f"UPDATE agendamentos SET {', '.join(updates)} WHERE id = ?"
            self.conn.execute(query, params)
            self.conn.commit()
            
            return {'success': True, 'message': 'Agendamento atualizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar agendamento: {str(e)}'}

    def excluir_agendamento(self, agendamento_id: str) -> Dict:
        try:
            self.conn.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
            self.conn.commit()
            return {'success': True, 'message': 'Agendamento excluído com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao excluir agendamento: {str(e)}'}

    def remover_agendamento_soft(self, agendamento_id: str) -> Dict:
        try:
            agendamento_existente = self.obter_agendamento(agendamento_id)
            if not agendamento_existente:
                return {'success': False, 'message': 'Agendamento não encontrado'}
            
            removido_em = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE agendamentos 
                SET status = 'removido', removido_em = ?, removido_por = ?,
                    ultima_modificacao = ?, versao = versao + 1
                WHERE id = ?
            """, (removido_em, self.pc_id, removido_em, agendamento_id))
            self.conn.commit()
            return {'success': True, 'message': 'Agendamento marcado como removido'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao remover agendamento: {str(e)}'}
