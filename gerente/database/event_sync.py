"""
Sincronização baseada em eventos e identidade lógica
Substitui o sistema atual de IDs por eventos de estado
"""
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from gerente.database.identity import IdentityManager, IdentityMap


class EventBasedSync:
    """Implementa sincronização baseada em eventos, não IDs"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        self.identity_map = IdentityMap(db_connection)
        self.identity_manager = IdentityManager()
    
    def sync_pacientes_by_events(self, local_pacientes: List[Dict], 
                                vps_pacientes: List[Dict] = None) -> Dict:
        """Sincroniza pacientes usando eventos em vez de comparação direta"""
        results = {
            'success': True,
            'novos_identidades': 0,
            'eventos_criados': 0,
            'conflitos_resolvidos': 0,
            'detalhes': []
        }
        
        try:
            # Processar cada paciente local como evento
            for paciente in local_pacientes:
                # 1. Gerar identidade lógica
                identity_fingerprint = self.identity_manager.generate_identity_fingerprint(paciente)
                id_local = paciente.get('id')
                
                # 2. Verificar se identidade já existe
                identity_existente = self.identity_map.get_identity_by_local_id(id_local)
                
                if not identity_existente:
                    # Nova identidade - registrar
                    self.identity_map.register_identity(
                        identity_fingerprint=identity_fingerprint,
                        id_local=id_local,
                        origem='local'
                    )
                    results['novos_identidades'] += 1
                
                # 3. Criar evento de sincronização
                evento = self.identity_map.create_sync_event(
                    identity_fingerprint=identity_fingerprint,
                    entity_type='paciente',
                    payload=paciente,
                    source='local',
                    version=paciente.get('versao', 1)
                )
                
                results['eventos_criados'] += 1
                results['detalhes'].append({
                    'id_local': id_local,
                    'identity_fingerprint': identity_fingerprint,
                    'event_id': evento['event_id'],
                    'acao': 'evento_criado'
                })
            
            # 4. Processar pacientes da VPS se fornecidos
            if vps_pacientes:
                vps_results = self._process_vps_events(vps_pacientes)
                results.update(vps_results)
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'detalhes': results.get('detalhes', [])
            }
    
    def _process_vps_events(self, vps_pacientes: List[Dict]) -> Dict:
        """Processa pacientes vindos da VPS como eventos"""
        results = {
            'vps_eventos_criados': 0,
            'vps_conflitos_resolvidos': 0,
            'mapeamentos_atualizados': 0
        }
        
        for paciente_vps in vps_pacientes:
            identity_fingerprint = self.identity_manager.generate_identity_fingerprint(paciente_vps)
            id_vps = paciente_vps.get('id')
            
            # Verificar se já existe identidade
            identity_existente = self.identity_map.get_identity_by_vps_id(id_vps)
            
            if not identity_existente:
                # Tentar encontrar por fingerprint
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM identity_map WHERE identity_fingerprint = ?
                """, (identity_fingerprint,))
                row = cursor.fetchone()
                
                if row:
                    # Identidade existe, mas sem mapeamento VPS
                    self.identity_map.update_mapping(
                        identity_fingerprint=identity_fingerprint,
                        id_vps=id_vps
                    )
                    results['mapeamentos_atualizados'] += 1
                else:
                    # Registrar nova identidade da VPS
                    self.identity_map.register_identity(
                        identity_fingerprint=identity_fingerprint,
                        id_vps=id_vps,
                        origem='vps'
                    )
                    results['novos_identidades'] = results.get('novos_identidades', 0) + 1
            
            # Criar evento da VPS
            self.identity_map.create_sync_event(
                identity_fingerprint=identity_fingerprint,
                entity_type='paciente',
                payload=paciente_vps,
                source='vps',
                version=paciente_vps.get('versao', 1)
            )
            
            results['vps_eventos_criados'] += 1
        
        return results
    
    def resolve_all_conflicts(self) -> Dict:
        """Resolve todos os conflitos pendentes usando last-write-wins"""
        cursor = self.conn.cursor()
        
        # Encontrar identidades com múltiplos eventos não aplicados
        cursor.execute("""
            SELECT identity_fingerprint, COUNT(*) as event_count
            FROM sync_events 
            WHERE applied = 0
            GROUP BY identity_fingerprint
            HAVING event_count > 1
        """)
        
        conflitos = cursor.fetchall()
        results = {
            'conflitos_encontrados': len(conflitos),
            'conflitos_resolvidos': 0,
            'detalhes': []
        }
        
        for row in conflitos:
            identity_fingerprint = row['identity_fingerprint']
            
            # Resolver conflito (last-write-wins)
            evento_vencedor = self.identity_map.resolve_conflict_last_write_wins(identity_fingerprint)
            
            if evento_vencedor:
                # Aplicar evento vencedor
                self._apply_event_to_database(evento_vencedor)
                
                # Marcar todos os eventos como aplicados
                cursor.execute("""
                    UPDATE sync_events SET applied = 1 
                    WHERE identity_fingerprint = ?
                """, (identity_fingerprint,))
                
                results['conflitos_resolvidos'] += 1
                results['detalhes'].append({
                    'identity_fingerprint': identity_fingerprint,
                    'evento_vencedor': evento_vencedor['event_id'],
                    'timestamp': evento_vencedor['timestamp']
                })
        
        self.conn.commit()
        return results
    
    def _apply_event_to_database(self, evento: Dict) -> Dict:
        """Aplica um evento ao banco de dados local"""
        try:
            payload = evento['payload']
            entity_type = evento['entity_type']
            
            if entity_type == 'paciente':
                return self._apply_paciente_event(payload)
            elif entity_type == 'agendamento':
                return self._apply_agendamento_event(payload)
            
            return {'success': False, 'message': f'Tipo de entidade desconhecido: {entity_type}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _apply_paciente_event(self, paciente_data: Dict) -> Dict:
        """Aplica evento de paciente ao banco local"""
        cursor = self.conn.cursor()
        
        # Verificar se paciente existe pelo ID técnico
        id_tecnico = paciente_data.get('id')
        if id_tecnico:
            cursor.execute("SELECT id FROM pacientes WHERE id = ?", (id_tecnico,))
            existe = cursor.fetchone()
            
            if existe:
                # Atualizar existente
                # Aqui você usaria o método atualizar_paciente existente
                # Por ora, fazemos update direto
                self._update_paciente_direct(paciente_data)
                return {'success': True, 'action': 'updated', 'id': id_tecnico}
            else:
                # Inserir novo
                self._insert_paciente_direct(paciente_data)
                return {'success': True, 'action': 'inserted', 'id': id_tecnico}
        
        return {'success': False, 'message': 'ID técnico não fornecido'}
    
    def _insert_paciente_direct(self, paciente_data: Dict):
        """Inserção direta de paciente (compatibilidade com código existente)"""
        # Implementação similar ao método inserir_registro existente
        # Simplificado para exemplo
        cursor = self.conn.cursor()
        
        identificacao = paciente_data.get('identificacao', {})
        avaliacao = paciente_data.get('avaliacao', {})
        
        cursor.execute("""
            INSERT OR REPLACE INTO pacientes (
                id, nome_gestante, unidade_saude, data_salvamento,
                pc_id, ultima_modificacao, versao, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paciente_data.get('id'),
            identificacao.get('nome_gestante', '').strip(),
            identificacao.get('unidade_saude', '').strip(),
            paciente_data.get('data_salvamento'),
            paciente_data.get('pc_id'),
            paciente_data.get('ultima_modificacao'),
            paciente_data.get('versao', 1),
            paciente_data.get('status', 'ativo')
        ))
        
        self.conn.commit()
    
    def _update_paciente_direct(self, paciente_data: Dict):
        """Atualização direta de paciente"""
        cursor = self.conn.cursor()
        
        identificacao = paciente_data.get('identificacao', {})
        avaliacao = paciente_data.get('avaliacao', {})
        
        cursor.execute("""
            UPDATE pacientes SET
                nome_gestante = ?,
                unidade_saude = ?,
                pc_id = ?,
                ultima_modificacao = ?,
                versao = ?,
                status = ?
            WHERE id = ?
        """, (
            identificacao.get('nome_gestante', '').strip(),
            identificacao.get('unidade_saude', '').strip(),
            paciente_data.get('pc_id'),
            paciente_data.get('ultima_modificacao'),
            paciente_data.get('versao', 1),
            paciente_data.get('status', 'ativo'),
            paciente_data.get('id')
        ))
        
        self.conn.commit()
    
    def get_sync_status(self) -> Dict:
        """Retorna status completo da sincronização baseada em eventos"""
        cursor = self.conn.cursor()
        
        # Contagem de identidades
        cursor.execute("SELECT COUNT(*) as total FROM identity_map")
        total_identidades = cursor.fetchone()['total']
        
        # Contagem de eventos pendentes
        cursor.execute("SELECT COUNT(*) as total FROM sync_events WHERE applied = 0")
        eventos_pendentes = cursor.fetchone()['total']
        
        # Contagem de conflitos
        cursor.execute("""
            SELECT COUNT(*) as total FROM (
                SELECT identity_fingerprint, COUNT(*) as cnt
                FROM sync_events WHERE applied = 0
                GROUP BY identity_fingerprint HAVING cnt > 1
            )
        """)
        conflitos_ativos = cursor.fetchone()['total']
        
        # Última sincronização
        cursor.execute("""
            SELECT MAX(timestamp) as ultima_sync FROM sync_events WHERE applied = 1
        """)
        ultima_sync = cursor.fetchone()['ultima_sync']
        
        return {
            'total_identidades': total_identidades,
            'eventos_pendentes': eventos_pendentes,
            'conflitos_ativos': conflitos_ativos,
            'ultima_sync': ultima_sync,
            'sistema_estavel': conflitos_ativos == 0
        }
    
    def sync_by_timestamp(self, since_timestamp: str = None) -> Dict:
        """Sincroniza eventos desde um timestamp específico"""
        eventos_pendentes = self.identity_map.get_pending_events(since_timestamp)
        
        results = {
            'eventos_processados': 0,
            'eventos_aplicados': 0,
            'detalhes': []
        }
        
        for evento in eventos_pendentes:
            try:
                # Aplicar evento
                resultado = self._apply_event_to_database(evento)
                
                if resultado.get('success'):
                    # Marcar como aplicado
                    self.identity_map.mark_event_applied(evento['event_id'])
                    results['eventos_aplicados'] += 1
                
                results['eventos_processados'] += 1
                results['detalhes'].append({
                    'event_id': evento['event_id'],
                    'identity_fingerprint': evento['identity_fingerprint'],
                    'aplicado': resultado.get('success', False)
                })
                
            except Exception as e:
                results['detalhes'].append({
                    'event_id': evento['event_id'],
                    'erro': str(e)
                })
        
        return results