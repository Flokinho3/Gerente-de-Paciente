"""
Aplicação Flask - Sistema de Gestão de Pacientes.
Módulos: db, paginas, api_version, discovery, pacientes, agendamentos,
sync, backup, indicadores, tema, exportar, ajuda.
"""
import atexit
import os
import sys

from env_loader import load_env

load_env()

from flask import Flask

from . import constants
from .agendamentos import bp as agendamentos_bp
from .ajuda import bp as ajuda_bp
from .api_version import bp as api_version_bp
from .backup import bp as backup_bp
from .db import _get_db_for_port, atualizar_discovery_peers, db, get_db
from .discovery import bp as discovery_bp
from .exportar import bp as exportar_bp
from .indicadores import bp as indicadores_bp
from .paginas import bp as paginas_bp
from .pacientes import bp as pacientes_bp
from .sync import create_sync_blueprint
from .tema import bp as tema_bp

VERSION = constants.VERSION
BUILD_DATE = constants.BUILD_DATE

_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_app = Flask(
    __name__,
    template_folder=os.path.join(_base, "templates"),
    static_folder=os.path.join(_base, "static"),
)


@_app.context_processor
def _inject_version():
    return {"version": VERSION, "build_date": BUILD_DATE}


_app.register_blueprint(paginas_bp)
_app.register_blueprint(api_version_bp)
_app.register_blueprint(discovery_bp)
_app.register_blueprint(pacientes_bp)
_app.register_blueprint(agendamentos_bp)
_app.register_blueprint(create_sync_blueprint())
_app.register_blueprint(backup_bp)
_app.register_blueprint(indicadores_bp)
_app.register_blueprint(tema_bp)
_app.register_blueprint(exportar_bp)
_app.register_blueprint(ajuda_bp)

# Compatibilidade: nome usado externamente
app = _app

_flask_server = None
_flask_servers = {}


def run_flask(debug=False, use_reloader=False, silent=False, port=None):
    from . import db as _db_mod

    try:
        _tl = _db_mod._thread_local
    except Exception:
        _tl = None
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    if port is None:
        port = int(os.getenv("PORT", 5000))
    db_instance = _get_db_for_port(port)
    if _tl is not None:
        _tl.db_instance = db_instance
    if debug is False:
        debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    is_executable = getattr(sys, "frozen", False)
    if silent or (is_executable and not debug):
        import logging

        logging.getLogger("werkzeug").setLevel(logging.ERROR)
    threads = int(os.getenv("WAITRESS_THREADS", "8"))
    discovery = (os.getenv("DISCOVERY") or "zeroconf").strip().lower()
    try:
        if discovery == "scan":
            from inicio.rede import run_scan_loop

            run_scan_loop(port=port)
        else:
            from inicio.rede.zeroconf_discovery import start_zeroconf

            start_zeroconf(port)
    except Exception:
        pass
    if use_reloader:
        _app.run(host=host, port=port, debug=debug, use_reloader=use_reloader)
    else:
        from waitress import serve

        try:
            if not is_executable or debug:
                print(f"Servidor iniciado em http://{host}:{port} (Waitress, {threads} threads)")
            serve(_app, host=host, port=port, threads=threads)
        except KeyboardInterrupt:
            if not is_executable or debug:
                print(f"\nServidor na porta {port} encerrado")
        except Exception as e:
            if is_executable and not debug:
                try:
                    import tkinter as tk
                    from tkinter import messagebox

                    root = tk.Tk()
                    root.withdraw()
                    messagebox.showerror(
                        "Erro ao Iniciar Servidor",
                        f"Não foi possível iniciar o servidor na porta {port}.\n\n"
                        f"Erro: {str(e)}\n\n"
                        "Verifique se:\n- A porta não está em uso\n"
                        "- Você tem permissões suficientes\n- O firewall não está bloqueando",
                    )
                    root.destroy()
                except Exception:
                    pass
            else:
                print(f"Erro ao iniciar servidor: {e}")
                import traceback

                traceback.print_exc()
            raise


def cleanup_flask():
    global _flask_server, _flask_servers
    for port, server in list(_flask_servers.items()):
        try:
            print(f"Encerrando servidor Flask na porta {port}...")
            server.shutdown()
            print(f"Servidor Flask na porta {port} encerrado")
        except Exception:
            pass
    _flask_servers.clear()
    if _flask_server:
        try:
            print("Encerrando servidor Flask...")
            _flask_server.shutdown()
            _flask_server = None
            print("Servidor Flask encerrado")
        except Exception:
            pass
    try:
        from inicio.rede.zeroconf_discovery import stop_zeroconf

        stop_zeroconf()
    except Exception:
        pass


atexit.register(cleanup_flask)

__all__ = [
    "app",
    "run_flask",
    "cleanup_flask",
    "get_db",
    "db",
    "atualizar_discovery_peers",
    "VERSION",
    "BUILD_DATE",
]
