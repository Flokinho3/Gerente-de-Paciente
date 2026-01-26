"""
Configurações de inicialização: obter opções, tray, console, handlers de sinal.
"""
import os
import signal
import sys

from flask_app import VERSION, BUILD_DATE, cleanup_flask


def obter_configuracoes():
    """Obtém todas as configurações do sistema"""
    return {
        'is_executable': getattr(sys, 'frozen', False),
        'debug_mode': os.getenv('FLASK_DEBUG', 'false').lower() == 'true',
        'is_silent': '--silent' in sys.argv or os.getenv('SILENT_MODE', '0') == '1',
        'no_tray': '--no-tray' in sys.argv,
        'force_tray': '--tray' in sys.argv,
        'use_tray_env': os.getenv('USE_TRAY', '1') == '1',
        'iniciar_duplo': '--duplo' in sys.argv or os.getenv('DUPLO_SERVIDOR', '0') == '1',
        'porta': int(os.getenv('PORT', 5000)),
        'porta2': int(os.getenv('PORT2', 5001)),
    }


def deve_usar_tray(config):
    """Determina se deve usar tray icon"""
    return (not config['no_tray'] and
            (config['force_tray'] or config['use_tray_env'] or
             config['is_executable'] or config['is_silent']))


def deve_exibir_console(config):
    """Determina se deve exibir mensagens no console"""
    return not config['is_executable'] or config['debug_mode']


def mostrar_informacoes_sistema(config):
    """Mostra informações do sistema no console"""
    if deve_exibir_console(config):
        print("=" * 60)
        print("Sistema de Gestao de Pacientes")
        print(f"Versao: {VERSION}")
        print(f"Build: {BUILD_DATE}")
        print("=" * 60)


def _signal_handler(signum, frame):
    """Handler para sinais de encerramento"""
    print(f"\nRecebido sinal {signum}, encerrando aplicação...")
    cleanup_flask()
    sys.exit(0)


def registrar_handlers_sinal():
    """Registra handlers de sinal para sistemas Unix"""
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)
