"""
Gestão de identidade lógica para sincronização robusta
Implementa as 3 camadas: lógica (fingerprint), técnica (IDs mutáveis) e temporal (eventos)
"""
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime


class IdentityManager:
    """Gerencia identidades lógicas independentes de IDs técnicos"""
    
    @staticmethod
    def generate_identity_fingerprint(paciente_data: Dict) -> str:
        """Gera hash imutável da identidade lógica do paciente"""
        # Campos-chave para identificação única
        identificacao = paciente_data.get('identificacao', {})
        
        # Normalização de dados
        nome = identificacao.get('nome_gestante', '').strip().lower()
        unidade = identificacao.get('unidade_saude', '').strip().lower()
        
        # Data de nascimento se disponível (campo importante para distinguir homônimos)
        data_nasc = paciente_data.get('data_nascimento', '')
        
        # CPF se disponível (identificador forte)
        cpf = identificacao.get('cpf', '').strip().replace('.', '').replace('-', '')
        
        # Criar string canonical para hash
        identity_data = {
            'nome_gestante': nome,
            'unidade_saude': unidade,
            'data_nascimento': data_nasc,
            'cpf': cpf
        }
        
        # Remover campos vazios
        identity_data = {k: v for k, v in identity_data.items() if v}
        
        # Gerar SHA-256 como fingerprint
        identity_str = json.dumps(identity_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(identity_str.encode('utf-8')).hexdigest()[:16]
    
    @staticmethod
    def generate_fingerprint_for_agendamento(agendamento_data: Dict) -> str:
        """Gera fingerprint para agendamentos"""
        paciente_id = agendamento_data.get('paciente_id', '')
        data = agendamento_data.get('data_consulta', '')
        hora = agendamento_data.get('hora_consulta', '')
        tipo = agendamento_data.get('tipo_consulta', '')
        
        identity_str = f"{paciente_id}_{data}_{hora}_{tipo}"
        return hashlib.sha256(identity_str.encode('utf-8')).hexdigest()[:16]
    
    @staticmethod
    def compare_identity_similarity(data1: Dict, data2: Dict) -> float:
        """Compara similaridade entre dois pacientes (0.0 a 1.0)"""
        id1 = data1.get('identificacao', {})
        id2 = data2.get('identificacao', {})
        
        # Nome mais importante
        nome1 = id1.get('nome_gestante', '').strip().lower()
        nome2 = id2.get('nome_gestante', '').strip().lower()
        
        if nome1 and nome2:
            # Similaridade simples de nomes
            nome_similarity = 1.0 if nome1 == nome2 else 0.0
            
            # Bônus se mesma unidade
            unidade1 = id1.get('unidade_saude', '').strip().lower()
            unidade2 = id2.get('unidade_saude', '').strip().lower()
            unidade_bonus = 0.2 if (unidade1 and unidade2 and unidade1 == unidade2) else 0.0
            
            return min(1.0, nome_similarity + unidade_bonus)
        
        return 0.0


class IdentityMap:
    """Mapeamento entre identidades lógicas e IDs técnicos"""
    
    def __init__(self, db_connection):
        self.conn = db_connection
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Cria tabelas de gerenciamento de identidade"""
        ddl_identity_map = """
        CREATE TABLE IF NOT EXISTS identity_map (
            identity_fingerprint TEXT PRIMARY KEY,
            id_local TEXT,
            id_vps TEXT,
            origem TEXT DEFAULT 'local',
            data_criacao TEXT,
            ultima_atualizacao TEXT,
            metadata TEXT
        )
        """
        self.conn.execute(ddl_identity_map)
        
        ddl_sync_events = """
        CREATE TABLE IF NOT EXISTS sync_events (
            event_id TEXT PRIMARY KEY,
            identity_fingerprint TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            applied INTEGER DEFAULT 0,
            version INTEGER,
            FOREIGN KEY (identity_fingerprint) REFERENCES identity_map(identity_fingerprint)
        )
        """
        self.conn.execute(ddl_sync_events)
        
        # Índices
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_identity_fingerprint ON identity_map(identity_fingerprint)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_identity_local ON identity_map(id_local)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_identity_vps ON identity_map(id_vps)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_identity ON sync_events(identity_fingerprint)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON sync_events(timestamp)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_events_applied ON sync_events(applied)")
        
        self.conn.commit()
    
    def register_identity(self, identity_fingerprint: str, id_local: str = None, 
                         id_vps: str = None, origem: str = 'local') -> Dict:
        """Registra nova identidade ou atualiza existente"""
        cursor = self.conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        metadata = {
            'origem': origem,
            'data_registro': now
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO identity_map 
            (identity_fingerprint, id_local, id_vps, origem, data_criacao, ultima_atualizacao, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            identity_fingerprint,
            id_local,
            id_vps,
            origem,
            now,
            now,
            json.dumps(metadata)
        ))
        
        self.conn.commit()
        
        return {
            'success': True,
            'identity_fingerprint': identity_fingerprint,
            'id_local': id_local,
            'id_vps': id_vps
        }
    
    def get_identity_by_local_id(self, id_local: str) -> Optional[Dict]:
        """Busca identidade pelo ID local"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM identity_map WHERE id_local = ?
        """, (id_local,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            if result.get('metadata'):
                try:
                    result['metadata'] = json.loads(result['metadata'])
                except:
                    result['metadata'] = {}
            return result
        return None
    
    def get_identity_by_vps_id(self, id_vps: str) -> Optional[Dict]:
        """Busca identidade pelo ID da VPS"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM identity_map WHERE id_vps = ?
        """, (id_vps,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            if result.get('metadata'):
                try:
                    result['metadata'] = json.loads(result['metadata'])
                except:
                    result['metadata'] = {}
            return result
        return None
    
    def update_mapping(self, identity_fingerprint: str, id_local: str = None, 
                      id_vps: str = None) -> Dict:
        """Atualiza mapeamento de IDs para identidade existente"""
        cursor = self.conn.cursor()
        
        updates = []
        params = []
        
        if id_local:
            updates.append("id_local = ?")
            params.append(id_local)
        
        if id_vps:
            updates.append("id_vps = ?")
            params.append(id_vps)
        
        if updates:
            updates.append("ultima_atualizacao = ?")
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            params.append(identity_fingerprint)
            
            query = f"UPDATE identity_map SET {', '.join(updates)} WHERE identity_fingerprint = ?"
            cursor.execute(query, params)
            self.conn.commit()
            
            return {'success': True, 'updated': cursor.rowcount > 0}
        
        return {'success': False, 'message': 'Nenhuma atualização fornecida'}
    
    def find_duplicate_candidates(self, paciente_data: Dict) -> List[Dict]:
        """Encontra candidatos a duplicados baseado na identidade lógica"""
        fingerprint = IdentityManager.generate_identity_fingerprint(paciente_data)
        
        cursor = self.conn.cursor()
        
        # Busca exata pelo fingerprint
        cursor.execute("""
            SELECT * FROM identity_map WHERE identity_fingerprint = ?
        """, (fingerprint,))
        
        exact_match = cursor.fetchone()
        results = []
        
        if exact_match:
            results.append(dict(exact_match))
        
        # Busca por similaridade (nomes parecidos)
        nome = paciente_data.get('identificacao', {}).get('nome_gestante', '').strip().lower()
        
        if nome:
            cursor.execute("""
                SELECT im.* FROM identity_map im
                JOIN pacientes p ON p.id = im.id_local
                WHERE LOWER(p.nome_gestante) LIKE ?
                AND im.identity_fingerprint != ?
            """, (f"%{nome}%", fingerprint))
            
            similar_matches = cursor.fetchall()
            for match in similar_matches:
                results.append(dict(match))
        
        return results
    
    def create_sync_event(self, identity_fingerprint: str, entity_type: str, 
                         payload: Dict, source: str, version: int = 1) -> Dict:
        """Cria evento de sincronização"""
        cursor = self.conn.cursor()
        
        event_id = f"{entity_type}_{identity_fingerprint}_{int(datetime.now().timestamp())}"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO sync_events 
            (event_id, identity_fingerprint, entity_type, payload, timestamp, source, applied, version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            identity_fingerprint,
            entity_type,
            json.dumps(payload, ensure_ascii=False, default=str),
            timestamp,
            source,
            0,  # Não aplicado ainda
            version
        ))
        
        self.conn.commit()
        
        return {
            'success': True,
            'event_id': event_id,
            'identity_fingerprint': identity_fingerprint,
            'timestamp': timestamp
        }
    
    def get_pending_events(self, since_timestamp: str = None) -> List[Dict]:
        """Retorna eventos pendentes de aplicação"""
        cursor = self.conn.cursor()
        
        if since_timestamp:
            cursor.execute("""
                SELECT * FROM sync_events 
                WHERE applied = 0 AND timestamp > ?
                ORDER BY timestamp ASC
            """, (since_timestamp,))
        else:
            cursor.execute("""
                SELECT * FROM sync_events 
                WHERE applied = 0
                ORDER BY timestamp ASC
            """)
        
        events = []
        for row in cursor.fetchall():
            event = dict(row)
            if event.get('payload'):
                try:
                    event['payload'] = json.loads(event['payload'])
                except:
                    pass
            events.append(event)
        
        return events
    
    def mark_event_applied(self, event_id: str) -> Dict:
        """Marca evento como aplicado"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sync_events SET applied = 1 WHERE event_id = ?
        """, (event_id,))
        
        self.conn.commit()
        
        return {'success': True, 'updated': cursor.rowcount > 0}
    
    def resolve_conflict_last_write_wins(self, identity_fingerprint: str) -> Optional[Dict]:
        """Resolve conflito usando última escrita (last-write-wins)"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sync_events 
            WHERE identity_fingerprint = ?
            ORDER BY timestamp DESC, version DESC
            LIMIT 1
        """, (identity_fingerprint,))
        
        row = cursor.fetchone()
        
        if row:
            event = dict(row)
            if event.get('payload'):
                try:
                    event['payload'] = json.loads(event['payload'])
                except:
                    pass
            return event
        
        return None