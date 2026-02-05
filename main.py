import os
import sys
from datetime import datetime
from typing import Any, cast

from gerente.env_loader import get_env_path, load_env
from gerente.flask_app import cleanup_flask
from gerente.inicio.utils import _log_debug, exibir_erro                                                        # type: ignore
from gerente.inicio.opcoes import (                                                                             # type: ignore
    deve_exibir_console,                                                                                        # type: ignore                  
    deve_usar_tray,                                                                                             # type: ignore
    mostrar_informacoes_sistema,                                                                                # type: ignore
    obter_configuracoes,                                                                                        # type: ignore
    registrar_handlers_sinal,                                                                                   # type: ignore
)
from gerente.inicio.rede import porta_acessivel, verificar_e_liberar_porta# type: ignore
from gerente.inicio.servidores import (
    iniciar_com_tray_icon,                                                                                      # type: ignore
    iniciar_modo_desenvolvimento,                                                                               # type: ignore
    iniciar_modo_executavel_sem_tray,                                                                           # type: ignore
    iniciar_modo_silencioso,                                                                                    # type: ignore
    iniciar_servidores_duplos,                                                                                  # type: ignore
)


_env_carregou = load_env()
_env_caminho = get_env_path()


def _ensure_version_file():
    """Garante que version.json existe no diretório de dados"""
    from pathlib import Path
    from gerente.config import get_version_file_path
    
    vf = Path(get_version_file_path())
    if not vf.exists():
        try:
            # Garantir pasta data/
            vf.parent.mkdir(parents=True, exist_ok=True)
            vf.write_text('{"version": "0.0.0", "asset_template": "GerenteApp_{version}.zip"}', encoding="utf-8")
        except Exception:
            pass


def main():
    """Função principal - coordena toda a inicialização do sistema"""
    # Garantir que version.json existe (necessário para o launcher/atualizador)
    _ensure_version_file()
    
    config = cast(dict[str, Any], obter_configuracoes())

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
        # Tentar usar 0.0.0.0 por padrão para evitar problemas de resolução localhost/::1 no Windows
        host = os.getenv("FLASK_HOST", "0.0.0.0")
        if not porta_acessivel(host=host, port=porta):
            # Fallback para 127.0.0.1 se 0.0.0.0 falhar por permissão
            host = "127.0.0.1"
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
        import traceback
        from gerente.config import get_data_dir
        
        # Logar erro em arquivo para depuração do executável
        try:
            log_path = os.path.join(get_data_dir(), "crash_report.log")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now().isoformat()}] ERRO FATAL:\n")
                f.write(traceback.format_exc())
                f.write("-" * 50 + "\n")
        except:
            pass

        exibir_erro(
            "Erro Fatal",
            f"Ocorreu um erro ao iniciar o sistema.\nConfira o log em: {os.path.join('data', 'crash_report.log')}",
            e
        )
        cleanup_flask()
        sys.exit(1)


if __name__ == '__main__':
    main()
