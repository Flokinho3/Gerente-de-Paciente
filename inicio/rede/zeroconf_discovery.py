"""
Descoberta Zeroconf/mDNS: anúncio e descoberta na LAN sem scan nem líder.
Cada instância anuncia _gerentepaciente._http._tcp.local e descobre as demais.
"""
import os
import socket
import threading

from inicio.rede.leader import get_local_ip

# Singleton e estado
_lock = threading.RLock()
_zeroconf = None
_browser = None
_infos = []  # ServiceInfo registrados (modo duplo: um por porta)
_peers = []  # [{"ip", "port", "hostname"}, ...] descobertos
_peers_lock = threading.Lock()
_TYPE_DEFAULT = "_gerentepaciente._http._tcp.local."


def _get_service_type():
    return (os.getenv("ZEROCONF_SERVICE_TYPE") or _TYPE_DEFAULT).strip() or _TYPE_DEFAULT


def _make_service_name(hostname: str, port: int) -> str:
    """Nome único: Gerente @ HOSTNAME-5000._gerentepaciente._http._tcp.local."""
    safe = (hostname or "localhost").replace(" ", "-")[:50]
    st = _get_service_type()
    if not st.endswith("."):
        st = st + "."
    return f"Gerente @ {safe}-{port}.{st}"


class _Listener:
    def add_service(self, zc, type_, name):
        try:
            info = zc.get_service_info(type_, name)
            if info is None:
                return
            ip = None
            if info.addresses:
                ip = socket.inet_ntoa(info.addresses[0])
            elif getattr(info, "address", None):
                ip = socket.inet_ntoa(info.address)
            if not ip:
                return
            port = int(info.port or 5000)
            hostname = (info.server or name).rstrip(".")
            if hostname.endswith(".local"):
                hostname = hostname[: -len(".local")]
            entry = {"ip": ip, "port": port, "hostname": hostname or ip}
            with _peers_lock:
                # Atualizar se já existe (mesmo ip:port)
                for i, p in enumerate(_peers):
                    if p.get("ip") == ip and p.get("port") == port:
                        _peers[i] = entry
                        return
                _peers.append(entry)
        except Exception:
            pass

    def update_service(self, zc, type_, name):
        """Obrigatório em versões recentes do Zeroconf."""
        self.add_service(zc, type_, name)

    def remove_service(self, zc, type_, name):
        try:
            info = zc.get_service_info(type_, name)
            if info is None:
                return
            ip = None
            if info.addresses:
                ip = socket.inet_ntoa(info.addresses[0])
            elif getattr(info, "address", None):
                ip = socket.inet_ntoa(info.address)
            port = int(info.port or 5000)
            with _peers_lock:
                _peers[:] = [p for p in _peers if not (p.get("ip") == ip and p.get("port") == port)]
        except Exception:
            pass


def start_zeroconf(port: int) -> None:
    """
    Regista este servidor via mDNS e inicia o browser para descobrir outros.
    Singleton: na 1ª chamada cria Zeroconf e ServiceBrowser; nas seguintes
    (ex. modo duplo) apenas regista outro ServiceInfo para a nova porta.
    """
    try:
        from zeroconf import IPVersion, ServiceBrowser, ServiceInfo, Zeroconf
    except ImportError:
        return

    port = int(port)
    with _lock:
        global _zeroconf, _browser, _infos
        if _zeroconf is None:
            try:
                _zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
            except Exception:
                return
            st = _get_service_type()
            if not st.endswith("."):
                st = st + "."
            _browser = ServiceBrowser(_zeroconf, st, _Listener())

        hostname = socket.gethostname() or "localhost"
        ip = get_local_ip()
        st = _get_service_type()
        if not st.endswith("."):
            st = st + "."
        name = _make_service_name(hostname, port)
        try:
            info = ServiceInfo(
                st,
                name,
                addresses=[socket.inet_aton(ip)],
                port=port,
                server=f"{hostname}.local.",
            )
            _zeroconf.register_service(info)
            _infos.append(info)
        except Exception:
            pass


def get_discovered_servers():
    """
    Retorna cópia da lista de servidores descobertos: [{"ip", "port", "hostname"}, ...].
    """
    with _peers_lock:
        return list(_peers)


def stop_zeroconf() -> None:
    """Desregista todos os ServiceInfo e encerra Zeroconf."""
    with _lock:
        global _zeroconf, _browser, _infos
        try:
            if _zeroconf is not None:
                for info in _infos:
                    try:
                        _zeroconf.unregister_service(info)
                    except Exception:
                        pass
                _infos.clear()
                _zeroconf.close()
        except Exception:
            pass
        _zeroconf = None
        _browser = None
        with _peers_lock:
            _peers.clear()
