"""
Banco de dados e proxy por porta/thread. Estado de discovery (scan).
"""
import os
import threading
from database import Database

# Instância global padrão
_db_default = Database()
_db_instances = {}
_thread_local = threading.local()

# Discovery (DISCOVERY=scan): peers + /register no líder
_leader_lock = threading.Lock()
_discovery_peers = []
_registered_peers = []


class DatabaseProxy:
    """Proxy que redireciona chamadas para a instância correta do banco de dados."""

    def __getattr__(self, name):
        return getattr(get_db(), name)

    def __call__(self, *args, **kwargs):
        return get_db()(*args, **kwargs)


db = DatabaseProxy()


def get_db():
    """Retorna a instância do banco correta (thread/porta)."""
    global _db_default, _db_instances, _thread_local
    if hasattr(_thread_local, "db_instance"):
        return _thread_local.db_instance
    try:
        from flask import request

        sp = request.environ.get("SERVER_PORT")
        if sp:
            port = int(sp)
            if port in _db_instances:
                _thread_local.db_instance = _db_instances[port]
                return _db_instances[port]
    except Exception:
        pass
    _thread_local.db_instance = _db_default
    return _db_default


def _get_local_ip():
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def atualizar_discovery_peers(peers):
    """Atualiza a lista de peers (chamado por leader.run_one_cycle quando DISCOVERY=scan)."""
    global _discovery_peers, _leader_lock
    with _leader_lock:
        _discovery_peers[:] = peers


def _ip_sort_key(ip_str, port=5000):
    """Chave de ordenação para menor IP. Usado por /register quando DISCOVERY=scan."""
    try:
        import ipaddress

        a = ipaddress.ip_address(ip_str)
        return (tuple(int(x) for x in str(a).split(".")), port)
    except Exception:
        return ((255, 255, 255, 255), port)


def _get_db_for_port(port):
    """Retorna a instância do banco para uma porta específica."""
    global _db_instances
    if port not in _db_instances:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if port == 5001:
            db_path = os.path.join(base_dir, "data", "pacientes_porta5001.db")
            _db_instances[port] = Database(db_path=db_path)
            print(f"Banco configurado para porta {port}: {db_path}")
        else:
            _db_instances[port] = Database()
    return _db_instances[port]


def get_discovery_state():
    """Retorna referências ao estado de discovery (para discovery blueprint)."""
    return _discovery_peers, _registered_peers, _leader_lock
