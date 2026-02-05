import json
from datetime import datetime
from typing import Optional, Dict, List

class SyncMixin:
    def listar_conflitos(self) -> Dict:
        """Lista todos os registros com status='conflito'"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM pacientes WHERE status = 'conflito'")
            pacientes_conflito = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT * FROM agendamentos WHERE status = 'conflito'")
            agendamentos_conflito = []
            for row in cursor.fetchall():
                agendamento = {
                    'id': row['id'],
                    'paciente_id': row['paciente_id'],
                    'data_consulta': row['data_consulta'],
                    'hora_consulta': row['hora_consulta'],
                    'tipo_consulta': row['tipo_consulta'],
                    'observacoes': row['observacoes'],
                    'status': row['status'],
                    'data_criacao': row['data_criacao'],
                    'data_atualizacao': row['data_atualizacao'],
                    'pc_id': row.get('pc_id') if 'pc_id' in row.keys() else None,
                    'ultima_modificacao': row.get('ultima_modificacao') if 'ultima_modificacao' in row.keys() else None,
                    'versao': row.get('versao') if 'versao' in row.keys() else None
                }
                agendamentos_conflito.append(agendamento)
            
            return {
                'success': True,
                'pacientes': pacientes_conflito,
                'agendamentos': agendamentos_conflito,
                'total': len(pacientes_conflito) + len(agendamentos_conflito)
            }
        except Exception as e:
            return {'success': False, 'message': f'Erro ao listar conflitos: {str(e)}', 'pacientes': [], 'agendamentos': [], 'total': 0}

    def resolver_conflito(self, registro_id: str, tipo: str, acao: str, dados_remotos: Optional[Dict] = None) -> Dict:
        try:
            if tipo == 'paciente':
                registro_existente = self.buscar_paciente(registro_id)
                if not registro_existente: return {'success': False, 'message': 'Paciente não encontrado'}
                if acao == 'manter_local':
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        UPDATE pacientes SET status = 'ativo', ultima_modificacao = ?, versao = versao + 1
                        WHERE id = ?
                    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), registro_id))
                    self.conn.commit()
                    return {'success': True, 'message': 'Conflito resolvido mantendo versão local'}
                elif acao == 'aceitar_remoto' and dados_remotos:
                    return self.inserir_registro(registro_id, dados_remotos, pc_id=dados_remotos.get('pc_id'),
                        ultima_modificacao=dados_remotos.get('ultima_modificacao'),
                        versao=dados_remotos.get('versao', registro_existente.get('versao', 1) + 1),
                        status='ativo')
            elif tipo == 'agendamento':
                registro_existente = self.obter_agendamento(registro_id)
                if not registro_existente: return {'success': False, 'message': 'Agendamento não encontrado'}
                if acao == 'manter_local':
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        UPDATE agendamentos SET status = CASE WHEN status = 'conflito' THEN 'agendado' ELSE status END,
                        ultima_modificacao = ?, versao = versao + 1 WHERE id = ?
                    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), registro_id))
                    self.conn.commit()
                    return {'success': True, 'message': 'Conflito resolvido mantendo versão local'}
                elif acao == 'aceitar_remoto' and dados_remotos:
                    return self.atualizar_agendamento(registro_id, paciente_id=dados_remotos.get('paciente_id'),
                        data_consulta=dados_remotos.get('data_consulta'), hora_consulta=dados_remotos.get('hora_consulta'),
                        tipo_consulta=dados_remotos.get('tipo_consulta'), observacoes=dados_remotos.get('observacoes'),
                        status=dados_remotos.get('status', 'agendado'), pc_id=dados_remotos.get('pc_id'),
                        ultima_modificacao=dados_remotos.get('ultima_modificacao'))
            return {'success': False, 'message': 'Ação inválida ou dados insuficientes'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao resolver conflito: {str(e)}'}

    def comparar_com_banco_remoto(self, pacientes_remotos: List[Dict]) -> Dict:
        pacientes_locais = self.obter_todos_pacientes()
        pacientes_locais_ids = {p['id'] for p in pacientes_locais}
        pacientes_remotos_ids = {p['id'] for p in pacientes_remotos}
        return {
            'pacientes_removidos_no_remoto': [p for p in pacientes_locais if p['id'] not in pacientes_remotos_ids],
            'pacientes_novos': [p for p in pacientes_remotos if p['id'] not in pacientes_locais_ids],
            'pacientes_em_ambos': [p for p in pacientes_remotos if p['id'] in pacientes_locais_ids],
            'total_local': len(pacientes_locais), 'total_remoto': len(pacientes_remotos)
        }

    def salvar_conflitos_pendentes(self, conflitos: Dict) -> Dict:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            payload = json.dumps(conflitos, ensure_ascii=False)
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO conflitos (payload, timestamp, origem) VALUES (?, ?, ?)", (payload, timestamp, 'vps_sync'))
            self.conn.commit()
            return {'success': True, 'message': 'Conflitos salvos no BD'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao salvar conflitos: {str(e)}'}

    def limpar_conflitos_pendentes(self) -> Dict:
        try:
            self.conn.execute("DELETE FROM conflitos WHERE origem = 'vps_sync'")
            self.conn.commit()
            return {'success': True, 'message': 'Conflitos limpos do BD'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao limpar conflitos: {str(e)}'}

    def obter_conflitos_pendentes(self) -> Optional[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT payload FROM conflitos WHERE origem = 'vps_sync' ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            return json.loads(row['payload']) if row else None
        except Exception:
            return None
