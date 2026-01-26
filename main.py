"""
Sistema de Gestão de Pacientes - Inicialização
Gerencia a inicialização do sistema (tray icon, modo executável, etc.)
"""
import os
import sys

from env_loader import get_env_path, load_env


def _carregar_env():
    """
    Carrega o .env (pasta do .exe ou raiz do projeto) e aplica default
    FLASK_HOST=0.0.0.0 no .exe quando ausente.
    """
    carregou = load_env()
    if getattr(sys, "frozen", False) and not os.getenv("FLASK_HOST"):
        os.environ["FLASK_HOST"] = "0.0.0.0"
    return carregou, get_env_path()


# Carregar .env ANTES de importar flask_app/database (eles usam os.getenv na importação)
_env_carregou, _env_caminho = _carregar_env()

from flask_app import cleanup_flask

from inicio.utils import _log_debug, exibir_erro
from inicio.opcoes import (
    deve_exibir_console,
    deve_usar_tray,
    mostrar_informacoes_sistema,
    obter_configuracoes,
    registrar_handlers_sinal,
)
from inicio.rede import porta_acessivel, verificar_e_liberar_porta
from inicio.servidores import (
    iniciar_com_tray_icon,
    iniciar_modo_desenvolvimento,
    iniciar_modo_executavel_sem_tray,
    iniciar_modo_silencioso,
    iniciar_servidores_duplos,
)


def main():
    """Função principal - coordena toda a inicialização do sistema"""
    config = obter_configuracoes()

    # Verificação do .env (apenas em modo debug)
    if config.get('debug_mode') and deve_exibir_console(config):
        status = 'encontrado' if _env_carregou else 'não encontrado (usando padrões)'
        print(f"[ENV] .env: {status} | Procurado em: {_env_caminho}")

    try:
        registrar_handlers_sinal()
        mostrar_informacoes_sistema(config)

        if config['iniciar_duplo']:
            iniciar_servidores_duplos(config)
            return

        porta = config['porta']

        _log_debug("main:main", "Iniciando main", {"porta": porta}, "D")

        if deve_exibir_console(config):
            print(f"Verificando porta {porta}...")
        if not verificar_e_liberar_porta(porta):
            exibir_erro(
                "Erro ao Iniciar Sistema",
                f"Não foi possível liberar a porta {porta}.\n\nPossíveis causas:\n- Porta já está em uso\n- Permissões insuficientes\n- Firewall bloqueando",
                None
            )
            sys.exit(1)
        host = os.getenv("FLASK_HOST", "127.0.0.1")
        if not porta_acessivel(host=host, port=porta):
            exibir_erro(
                "Erro ao Iniciar Sistema",
                f"Não foi possível usar a porta {porta} em {host} (bind falhou).\n\nPossíveis causas:\n- Permissões insuficientes\n- Firewall ou antivírus bloqueando",
                None
            )
            sys.exit(1)
        if deve_exibir_console(config):
            print(f"Porta {porta} está livre e pronta para uso.")

        use_tray = deve_usar_tray(config)

        if use_tray and not config['no_tray']:
            iniciar_com_tray_icon(porta, config)
        elif config['is_executable']:
            iniciar_modo_executavel_sem_tray(porta, config)
        elif config['is_silent']:
            iniciar_modo_silencioso(config)
        else:
            iniciar_modo_desenvolvimento(porta, config)

    except KeyboardInterrupt:
        if deve_exibir_console(config):
            print("\nInterrompido pelo usuário")
        cleanup_flask()
        sys.exit(0)
    except Exception as e:
        exibir_erro(
            "Erro Fatal",
            "Ocorreu um erro ao iniciar o sistema de gestão de pacientes.",
            e
        )
        cleanup_flask()
        sys.exit(1)


if __name__ == '__main__':
    main()
