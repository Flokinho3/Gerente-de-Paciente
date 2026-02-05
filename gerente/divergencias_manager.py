"""
Gerenciador de Divergências entre VPS e Banco Local
Detecta, armazena e gerencia divergências para notificação ao usuário
"""
import threading
from typing import Dict, List, Optional
from datetime import datetime


class DivergenciasManager:
    """Gerencia divergências detectadas entre VPS e banco local"""
    
    def __init__(self):
        self.divergencias_pendentes: Dict[str, List[Dict]] = {
            'novos_vps': [],           # Dados novos no VPS
            'atualizados_vps': [],     # Dados mais recentes no VPS
            'apenas_local': []          # Dados apenas locais
        }
        self.ignorados_temporarios: Dict[str, datetime] = {}  # ID -> timestamp
        self.ja_notificados: set = set()  # IDs já notificados (evita spam)
        self.lock = threading.Lock()
        
    def adicionar_divergencia(self, tipo: str, item: Dict):
        """Adiciona uma divergência detectada"""
        with self.lock:
            if tipo in self.divergencias_pendentes:
                # Verificar se já existe
                item_id = item.get('id')
                if item_id and item_id not in self.ignorados_temporarios:
                    # Remover duplicatas
                    self.divergencias_pendentes[tipo] = [
                        d for d in self.divergencias_pendentes[tipo] 
                        if d.get('id') != item_id
                    ]
                    self.divergencias_pendentes[tipo].append(item)
    
    def obter_divergencias(self) -> Dict[str, List[Dict]]:
        """Retorna todas as divergências pendentes"""
        with self.lock:
            return {
                'novos_vps': self.divergencias_pendentes['novos_vps'].copy(),
                'atualizados_vps': self.divergencias_pendentes['atualizados_vps'].copy(),
                'apenas_local': self.divergencias_pendentes['apenas_local'].copy(),
                'total': sum(len(v) for v in self.divergencias_pendentes.values())
            }
    
    def obter_divergencias_nao_notificadas(self) -> Dict[str, List[Dict]]:
        """Retorna apenas divergências que ainda não foram notificadas"""
        with self.lock:
            result = {
                'novos_vps': [],
                'atualizados_vps': [],
                'apenas_local': [],
                'total': 0
            }
            for tipo in ['novos_vps', 'atualizados_vps', 'apenas_local']:
                for item in self.divergencias_pendentes[tipo]:
                    item_id = item.get('id')
                    if item_id and item_id not in self.ja_notificados:
                        result[tipo].append(item)
                        result['total'] += 1
            return result
    
    def marcar_como_notificado(self, item_id: str):
        """Marca uma divergência como já notificada"""
        with self.lock:
            if item_id:
                self.ja_notificados.add(item_id)
    
    def marcar_todos_como_vistos(self):
        """Marca todas as divergências atuais como já notificadas/visualizadas"""
        with self.lock:
            for tipo in self.divergencias_pendentes:
                for item in self.divergencias_pendentes[tipo]:
                    item_id = item.get('id')
                    if item_id:
                        self.ja_notificados.add(item_id)
    
    def tem_divergencias_novas(self) -> bool:
        """Verifica se há divergências pendentes que ainda não foram notificadas"""
        with self.lock:
            for tipo in self.divergencias_pendentes:
                for item in self.divergencias_pendentes[tipo]:
                    item_id = item.get('id')
                    if item_id and item_id not in self.ja_notificados:
                        return True
            return False
    
    def ignorar_temporario(self, item_id: str):
        """Marca um item para ser ignorado até a próxima sincronização"""
        with self.lock:
            self.ignorados_temporarios[item_id] = datetime.now()
            # Remover das divergências pendentes
            for tipo in self.divergencias_pendentes:
                self.divergencias_pendentes[tipo] = [
                    d for d in self.divergencias_pendentes[tipo] 
                    if d.get('id') != item_id
                ]
    
    def remover_permanente(self, item_id: str):
        """Remove um item permanentemente (não será mais notificado)"""
        with self.lock:
            # Adicionar a uma lista de ignorados permanentes se necessário
            for tipo in self.divergencias_pendentes:
                self.divergencias_pendentes[tipo] = [
                    d for d in self.divergencias_pendentes[tipo] 
                    if d.get('id') != item_id
                ]
    
    def resolver_divergencia(self, item_id: str):
        """Remove uma divergência após ser resolvida"""
        with self.lock:
            for tipo in self.divergencias_pendentes:
                self.divergencias_pendentes[tipo] = [
                    d for d in self.divergencias_pendentes[tipo] 
                    if d.get('id') != item_id
                ]
            # Remover dos ignorados temporários também
            if item_id in self.ignorados_temporarios:
                del self.ignorados_temporarios[item_id]
            # Remover dos já notificados também (libera para notificar novamente se voltar)
            self.ja_notificados.discard(item_id)

    def tem_divergencias(self) -> bool:
        """Verifica se há divergências pendentes"""
        with self.lock:
            return any(len(v) > 0 for v in self.divergencias_pendentes.values())
    
    def limpar_ignorados_temporarios(self):
        """Limpa a lista de ignorados temporários (chamado a cada nova sincronização)"""
        with self.lock:
            self.ignorados_temporarios.clear()
    
    def limpar_todas(self):
        """Limpa todas as divergências"""
        with self.lock:
            for tipo in self.divergencias_pendentes:
                self.divergencias_pendentes[tipo].clear()
            self.ignorados_temporarios.clear()
            self.ja_notificados.clear()


# Singleton global
_divergencias_manager: Optional[DivergenciasManager] = None
_manager_lock = threading.Lock()


def get_divergencias_manager() -> DivergenciasManager:
    """Retorna a instância singleton do gerenciador de divergências"""
    global _divergencias_manager
    if _divergencias_manager is None:
        with _manager_lock:
            if _divergencias_manager is None:
                _divergencias_manager = DivergenciasManager()
    return _divergencias_manager
