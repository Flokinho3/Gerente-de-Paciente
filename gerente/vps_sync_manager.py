"""
Sincronização automática com VPS
Verifica periodicamente alterações e sincroniza com o servidor central
"""
import threading
import time
from datetime import datetime
from typing import Dict, Any, List
from gerente.database import Database
from gerente.vps_client import get_vps_client
from gerente.flask_app.event_logger import log_event


class VpsSyncManager:
    """Gerencia sincronização automática entre SQLite local e VPS"""

    def __init__(self, intervalo_minutos: int = 10):
        self.intervalo = intervalo_minutos * 60
        self.db_local = Database()
        self.vps_client = None
        self.timer = None
        self.rodando = False
        self.ultima_sync = None

    def iniciar(self):
        """Inicia o agendador de sincronização automática"""
        if self.rodando:
            return

        try:
            self.vps_client = get_vps_client()
            if not self.vps_client:
                return

            status: Dict[str, Any] = self.vps_client.get_status()
            if not status.get('success', False):
                return

            self.rodando = True
            self._executar_sync()
            self._agendar_proxima()

        except Exception as e:
            pass

    def parar(self):
        """Para o agendador"""
        self.rodando = False
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def _agendar_proxima(self):
        """Agenda a próxima sincronização"""
        if not self.rodando:
            return
        self.timer = threading.Timer(self.intervalo, self._executar_sync)
        self.timer.daemon = True
        self.timer.start()

    def _executar_sync(self):
        """Executa uma sincronização completa com detecção de divergências"""
        try:
            from gerente.divergencias_manager import get_divergencias_manager
            
            log_event("Iniciando sincronização com VPS...", "working")
            divergencias_mgr = get_divergencias_manager()
            
            # Limpar ignorados temporários da sincronização anterior
            divergencias_mgr.limpar_ignorados_temporarios()
            
            # 1. Buscar dados do VPS
            pacientes_vps = self.vps_client.get_pacientes_from_vps()
            agendamentos_vps = self.vps_client.get_agendamentos_from_vps()
            
            # 2. Buscar dados locais
            pacientes_local = self.db_local.buscar_pacientes()
            agendamentos_local = self.db_local.listar_agendamentos()
            
            # 3. Comparar e detectar divergências
            self._detectar_divergencias_pacientes(pacientes_vps, pacientes_local, divergencias_mgr)
            self._detectar_divergencias_agendamentos(agendamentos_vps, agendamentos_local, divergencias_mgr)
            
            # 4. Sincronizar dados locais para VPS (envio automático)
            if pacientes_local:
                result = self.vps_client.sync_pacientes(pacientes_local)
                log_event(f"Enviados {len(pacientes_local)} pacientes para VPS", "success")
            
            if agendamentos_local:
                result = self.vps_client.sync_agendamentos(agendamentos_local)
                log_event(f"Enviados {len(agendamentos_local)} agendamentos para VPS", "success")
            
            self.ultima_sync = datetime.now()
            
            # 5. Notificar se há NOVAS divergências (ainda não notificadas)
            if divergencias_mgr.tem_divergencias_novas():
                div_info = divergencias_mgr.obter_divergencias_nao_notificadas()
                log_event(f"⚠️ {div_info['total']} nova(s) divergência(s) detectada(s)! Verifique a página de conflitos.", "warning")
            else:
                log_event("Sincronização VPS concluída sem novas divergências", "success")

        except Exception as e:
            log_event(f"Erro na sincronização VPS: {str(e)}", "error")

        finally:
            self._agendar_proxima()
    
    def _detectar_divergencias_pacientes(self, pacientes_vps: List, pacientes_local: List, divergencias_mgr):
        """Detecta divergências entre pacientes VPS e locais"""
        # Criar dicionários para comparação rápida
        local_dict = {p['id']: p for p in pacientes_local}
        vps_dict = {p.get('id'): p for p in pacientes_vps}
        
        # Novos no VPS (não existem localmente)
        for p_vps in pacientes_vps:
            p_id = p_vps.get('id')
            if p_id and p_id not in local_dict:
                divergencias_mgr.adicionar_divergencia('novos_vps', {
                    'tipo': 'paciente',
                    'id': p_id,
                    'dados': p_vps,
                    'nome': p_vps.get('nome_gestante', 'N/A'),
                    'unidade': p_vps.get('unidade_saude', 'N/A')
                })
        
        # Atualizados no VPS (versão mais recente)
        for p_id, p_local in local_dict.items():
            if p_id in vps_dict:
                p_vps = vps_dict[p_id]
                vps_mod = p_vps.get('ultima_modificacao', '')
                local_mod = p_local.get('ultima_modificacao', '')
                
                if vps_mod > local_mod:
                    divergencias_mgr.adicionar_divergencia('atualizados_vps', {
                        'tipo': 'paciente',
                        'id': p_id,
                        'dados_vps': p_vps,
                        'dados_local': p_local,
                        'nome': p_vps.get('nome_gestante', 'N/A')
                    })
        
        # Apenas locais (não existem no VPS) - já são enviados automaticamente
        # Não precisamos notificar, pois o envio automático já cuida disso
    
    def _detectar_divergencias_agendamentos(self, agendamentos_vps: List, agendamentos_local: List, divergencias_mgr):
        """Detecta divergências entre agendamentos VPS e locais"""
        local_dict = {a['id']: a for a in agendamentos_local}
        vps_dict = {a.get('id'): a for a in agendamentos_vps}
        
        # Novos no VPS
        for a_vps in agendamentos_vps:
            a_id = a_vps.get('id')
            if a_id and a_id not in local_dict:
                divergencias_mgr.adicionar_divergencia('novos_vps', {
                    'tipo': 'agendamento',
                    'id': a_id,
                    'dados': a_vps,
                    'data': a_vps.get('data_consulta', 'N/A'),
                    'hora': a_vps.get('hora_consulta', 'N/A')
                })
        
        # Atualizados no VPS
        for a_id, a_local in local_dict.items():
            if a_id in vps_dict:
                a_vps = vps_dict[a_id]
                vps_mod = a_vps.get('ultima_modificacao', '')
                local_mod = a_local.get('ultima_modificacao', '')
                
                if vps_mod > local_mod:
                    divergencias_mgr.adicionar_divergencia('atualizados_vps', {
                        'tipo': 'agendamento',
                        'id': a_id,
                        'dados_vps': a_vps,
                        'dados_local': a_local,
                        'data': a_vps.get('data_consulta', 'N/A')
                    })

    def sincronizar_manual(self) -> Dict:
        """Executa sincronização manual"""
        try:
            if not self.vps_client:
                self.vps_client = get_vps_client()
                if not self.vps_client:
                    return {"success": False, "message": "VPS não disponível"}

            status = self.vps_client.get_status()
            if not status.get('success', False):
                return {"success": False, "message": "VPS não está respondendo"}

            pacientes_local = self.db_local.obter_todos_pacientes()
            agendamentos_local = self.db_local.listar_agendamentos()

            resultados = []
            if pacientes_local:
                result = self.vps_client.sync_pacientes(pacientes_local)
                resultados.append(result)

            if agendamentos_local:
                result = self.vps_client.sync_agendamentos(agendamentos_local)
                resultados.append(result)

            return {
                "success": True,
                "message": "Sincronização concluída",
                "resultados": resultados
            }

        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

    def sincronizar_com_confirmacao(self, confirmar: bool = False) -> Dict:
        """Sincroniza com confirmação do usuário"""
        try:
            if not self.vps_client:
                self.vps_client = get_vps_client()
                if not self.vps_client:
                    return {"success": False, "message": "VPS não disponível"}

            pacientes_local = self.db_local.obter_todos_pacientes()
            agendamentos_local = self.db_local.listar_agendamentos()

            pendentes = self.vps_client.verificar_pendentes(pacientes_local, agendamentos_local)
            if not pendentes.get('success'):
                return {"success": False, "message": pendentes.get('message')}

            total_pendentes = pendentes.get('pacientes', {}).get('pendentes', 0)
            total_pendentes += pendentes.get('agendamentos', {}).get('pendentes', 0)

            if not confirmar:
                return {
                    "success": True,
                    "precisa_confirmacao": True,
                    "total_pendentes": total_pendentes,
                    "detalhes": pendentes,
                    "message": f"{total_pendentes} registros aguardando sincronização"
                }

            return self.sincronizar_manual()

        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

    def sincronizar_seletivo(self, pacientes_ids: List[str] = None, agendamentos_ids: List[str] = None) -> Dict:
        """Sincroniza apenas registros específicos"""
        try:
            if not self.vps_client:
                self.vps_client = get_vps_client()
                if not self.vps_client:
                    return {"success": False, "message": "VPS não disponível"}

            resultados = []

            if pacientes_ids:
                pacientes_local = self.db_local.obter_todos_pacientes()
                pacientes_selecionados = [p for p in pacientes_local if p.get('id') in pacientes_ids]
                if pacientes_selecionados:
                    result = self.vps_client.sync_pacientes(pacientes_selecionados)
                    resultados.append(result)

            if agendamentos_ids:
                agendamentos_local = self.db_local.listar_agendamentos()
                agendamentos_selecionados = [a for a in agendamentos_local if a.get('id') in agendamentos_ids]
                if agendamentos_selecionados:
                    result = self.vps_client.sync_agendamentos(agendamentos_selecionados)
                    resultados.append(result)

            return {
                "success": True,
                "message": "Sincronização seletiva concluída",
                "resultados": resultados
            }

        except Exception as e:
            return {"success": False, "message": f"Erro: {str(e)}"}

    def get_status_sync(self) -> Dict:
        """Retorna status completo da sincronização"""
        try:
            # Tentar obter cliente VPS se não existir
            if not self.vps_client:
                try:
                    self.vps_client = get_vps_client()
                except Exception:
                    pass  # VPS não configurado ou indisponível
            
            vps_status = {}
            vps_disponivel = False
            
            if self.vps_client:
                try:
                    vps_status = self.vps_client.get_status()
                    vps_disponivel = vps_status.get('success', False)
                except Exception:
                    vps_disponivel = False
            
            pacientes_local = []
            agendamentos_local = []
            
            try:
                pacientes_local = self.db_local.obter_todos_pacientes()
                agendamentos_local = self.db_local.listar_agendamentos()
            except Exception:
                pass  # Banco local pode não estar disponível
            
            pendentes = {}
            if vps_disponivel and self.vps_client:
                try:
                    pendentes = self.vps_client.verificar_pendentes(pacientes_local, agendamentos_local)
                except Exception:
                    pass  # Erro ao verificar pendentes
            
            pendentes_count = 0
            if pendentes:
                pendentes_count = pendentes.get('pacientes', {}).get('pendentes', 0) + pendentes.get('agendamentos', {}).get('pendentes', 0)
            
            return {
                "vps_disponivel": vps_disponivel,
                "vps_status": vps_status,
                "sync_ativa": self.rodando,
                "ultima_sync": self.ultima_sync.isoformat() if self.ultima_sync else None,
                "dados_locais": {
                    "pacientes": len(pacientes_local),
                    "agendamentos": len(agendamentos_local)
                },
                "pendentes": pendentes_count
            }

        except Exception as e:
            return {
                "erro": str(e),
                "sync_ativa": self.rodando,
                "ultima_sync": self.ultima_sync.isoformat() if self.ultima_sync else None
            }


_sync_manager = None
def get_sync_manager(intervalo_minutos: int = 10) -> VpsSyncManager:
    """Retorna a instância singleton de VpsSyncManager, criando-a se necessário."""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = VpsSyncManager(intervalo_minutos)
    return _sync_manager


def iniciar_sync_vps(intervalo_minutos: int = 10):
    """Inicia sincronização VPS automática"""
    global _sync_manager
    _sm = get_sync_manager(intervalo_minutos)
    _sm.iniciar()
    return _sm


def parar_sync_vps():
    """Para sincronização VPS"""
    global _sync_manager
    if _sync_manager:
        _sync_manager.parar()


def sincronizar_vps_agora() -> Dict:
    """Executa sincronização manual imediata"""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = VpsSyncManager()
    return _sync_manager.sincronizar_manual()


if __name__ == "__main__":
    print("=" * 50)
    print("TESTE DE SINCRONIZAÇÃO VPS")
    print("=" * 50)

    manager = VpsSyncManager(intervalo_minutos=1)
    manager.iniciar()

    print("\nSincronização rodando. Aguardando 30 segundos...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nInterrompido")

    manager.parar()
    print("\nTeste concluído!")
