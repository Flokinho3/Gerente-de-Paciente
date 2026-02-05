"""
VPS Sync Manager refatorado para usar eventos e identidade lógica
Substitui comparação por IDs por sistema robusto de eventos
"""
import threading
import time
from datetime import datetime
from typing import Dict, Optional, List
from gerente.database import Database
from gerente.vps_client import get_vps_client
from gerente.flask_app.event_logger import log_event
from gerente.database.event_sync import EventBasedSync
from gerente.database.identity import IdentityManager


class VpsEventSyncManager:
    """Gerente de sincronização baseado em eventos (não mais IDs)"""

    def __init__(self, intervalo_minutos: int = 10):
        self.intervalo = intervalo_minutos * 60
        self.db_local = Database()
        self.vps_client = None
        self.timer = None
        self.rodando = False
        self.ultima_sync = None
        
        # Nova arquitetura: sync por eventos
        self.event_sync = EventBasedSync(self.db_local.conn)
        self.identity_manager = IdentityManager()

    def iniciar(self):
        """Inicia sincronização automática baseada em eventos"""
        if self.rodando:
            return

        try:
            self.vps_client = get_vps_client()
            if not self.vps_client:
                return

            status = self.vps_client.get_status()
            if not status.get('success', False):
                return

            self.rodando = True
            self._executar_sync_eventos()
            self._agendar_proxima()

        except Exception as e:
            log_event(f"Erro ao iniciar sync de eventos: {str(e)}", "error")

    def parar(self):
        """Para o agendador"""
        self.rodando = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _agendar_proxima(self):
        """Agenda próxima sincronização"""
        if not self.rodando:
            return
        self.timer = threading.Timer(self.intervalo, self._executar_sync_eventos)
        self.timer.daemon = True
        self.timer.start()

    def _executar_sync_eventos(self):
        """Executa sincronização baseada em eventos"""
        try:
            log_event("Iniciando sincronização por eventos...", "working")
            
            # 1. Obter dados locais
            pacientes_local = self.db_local.obter_todos_pacientes()
            agendamentos_local = self.db_local.listar_agendamentos()
            
            # 2. Obter dados da VPS
            pacientes_vps = self.vps_client.get_pacientes_from_vps()
            agendamentos_vps = self.vps_client.get_agendamentos_from_vps()
            
            # 3. Processar como eventos (não mais comparação direta)
            resultado_pacientes = self.event_sync.sync_pacientes_by_events(
                pacientes_local, pacientes_vps
            )
            
            # TODO: Implementar sync de agendamentos por eventos
            # resultado_agendamentos = self.event_sync.sync_agendamentos_by_events(
            #     agendamentos_local, agendamentos_vps
            # )
            
            # 4. Resolver conflitos automaticamente (last-write-wins)
            conflitos_resolvidos = self.event_sync.resolve_all_conflicts()
            
            # 5. Aplicar eventos pendentes
            eventos_aplicados = self.event_sync.sync_by_timestamp(self.ultima_sync)
            
            # 6. Log de resultados
            self._log_resultados_sync(resultado_pacientes, conflitos_resolvidos, eventos_aplicados)
            
            self.ultima_sync = datetime.now()
            log_event("Sincronização por eventos concluída", "success")

        except Exception as e:
            log_event(f"Erro na sincronização por eventos: {str(e)}", "error")

        finally:
            self._agendar_proxima()

    def _log_resultados_sync(self, resultado_pacientes: Dict, conflitos: Dict, eventos: Dict):
        """Registra resultados da sincronização"""
        if resultado_pacientes.get('success'):
            log_event(f"✅ {resultado_pacientes.get('novos_identidades', 0)} novas identidades", "success")
            log_event(f"📝 {resultado_pacientes.get('eventos_criados', 0)} eventos criados", "info")
        
        if conflitos.get('conflitos_resolvidos', 0) > 0:
            log_event(f"🔧 {conflitos['conflitos_resolvidos']} conflitos resolvidos", "warning")
        
        if eventos.get('eventos_aplicados', 0) > 0:
            log_event(f"✅ {eventos['eventos_aplicados']} eventos aplicados", "success")

    def sincronizar_manual_eventos(self) -> Dict:
        """Sincronização manual baseada em eventos"""
        try:
            if not self.vps_client:
                self.vps_client = get_vps_client()
                if not self.vps_client:
                    return {"success": False, "message": "VPS não disponível"}

            # Executar sincronização por eventos
            self._executar_sync_eventos()
            
            # Retornar status completo
            return {
                "success": True,
                "message": "Sincronização por eventos executada",
                "status": self.event_sync.get_sync_status()
            }

        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

    def get_status_event_sync(self) -> Dict:
        """Retorna status da sincronização por eventos"""
        try:
            vps_status = {}
            if self.vps_client:
                vps_status = self.vps_client.get_status()

            # Status da sincronização por eventos
            event_status = self.event_sync.get_sync_status()
            
            # Status do VPS client
            vps_disponivel = vps_status.get('success', False)

            return {
                "vps_disponivel": vps_disponivel,
                "sync_ativa": self.rodando,
                "ultima_sync": self.ultima_sync.isoformat() if self.ultima_sync else None,
                "event_sync_status": event_status,
                "sistema_estavel": event_status.get('sistema_estavel', False)
            }

        except Exception as e:
            return {"erro": str(e)}

    def detectar_potenciais_duplicatas(self) -> Dict:
        """Detecta potenciais duplicatas baseado na identidade lógica"""
        try:
            cursor = self.db_local.conn.cursor()
            duplicatas = []
            
            # Buscar pacientes com fingerprints duplicados
            cursor.execute("""
                SELECT p.id, p.nome_gestante, p.unidade_saude
                FROM pacientes p
                WHERE EXISTS (
                    SELECT 1 FROM pacientes p2 
                    WHERE p2.nome_gestante = p.nome_gestante 
                    AND p2.id != p.id
                )
                ORDER BY p.nome_gestante
            """)
            
            rows = cursor.fetchall()
            for row in rows:
                paciente_data = {
                    'id': row['id'],
                    'identificacao': {
                        'nome_gestante': row['nome_gestante'],
                        'unidade_saude': row['unidade_saude']
                    }
                }
                
                # Encontrar candidatos similares
                similares = self.event_sync.identity_map.find_duplicate_candidates(paciente_data)
                if len(similares) > 1:
                    duplicatas.append({
                        'paciente_id': row['id'],
                        'nome': row['nome_gestante'],
                        'unidade': row['unidade_saude'],
                        'identidades_similares': len(similares)
                    })
            
            return {
                'success': True,
                'potenciais_duplicatas': len(duplicatas),
                'detalhes': duplicatas[:20]  # Limitar para não sobrecarregar
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def migrar_registros_existentes(self) -> Dict:
        """Migra registros existentes para o novo sistema de identidade"""
        try:
            log_event("Iniciando migração de registros para sistema de identidade...", "working")
            
            # Obter todos os pacientes existentes
            pacientes_existentes = self.db_local.obter_todos_pacientes()
            
            migrados = 0
            erros = []
            
            for paciente in pacientes_existentes:
                try:
                    # Gerar fingerprint
                    fingerprint = self.identity_manager.generate_identity_fingerprint(paciente)
                    id_local = paciente.get('id')
                    
                    # Registrar no mapa de identidade
                    self.event_sync.identity_map.register_identity(
                        identity_fingerprint=fingerprint,
                        id_local=id_local,
                        origem='migracao'
                    )
                    
                    migrados += 1
                    
                except Exception as e:
                    erros.append(f"Erro migrando paciente {paciente.get('id')}: {str(e)}")
            
            log_event(f"✅ {migrados} pacientes migrados com sucesso", "success")
            
            if erros:
                log_event(f"⚠️ {len(erros)} erros durante migração", "warning")
            
            return {
                'success': True,
                'migrados': migrados,
                'erros': len(erros),
                'detalhes_erros': erros[:5]  # Primeiros 5 erros
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


# Funções de compatibilidade para manter interface existente
def get_event_sync_manager(intervalo_minutos: int = 10) -> VpsEventSyncManager:
    """Retorna instância do gerente de sincronização por eventos"""
    return VpsEventSyncManager(intervalo_minutos)


def iniciar_sync_eventos(intervalo_minutos: int = 10):
    """Inicia sincronização automática por eventos"""
    manager = get_event_sync_manager(intervalo_minutos)
    manager.iniciar()
    return manager


def sincronizar_eventos_agora() -> Dict:
    """Executa sincronização manual por eventos"""
    manager = get_event_sync_manager()
    return manager.sincronizar_manual_eventos()