"""Rede, portas, sincronização, descoberta Zeroconf e (quando DISCOVERY=scan) liderança."""
from .porta import porta_acessivel, verificar_e_liberar_porta
from .sync import sincronizar_servidores
from .leader import get_local_ip, run_one_cycle, run_scan_loop, scan_local_24
from .zeroconf_discovery import start_zeroconf, get_discovered_servers, stop_zeroconf

__all__ = [
    'porta_acessivel', 'verificar_e_liberar_porta', 'sincronizar_servidores',
    'get_local_ip', 'run_one_cycle', 'run_scan_loop', 'scan_local_24',
    'start_zeroconf', 'get_discovered_servers', 'stop_zeroconf',
]
