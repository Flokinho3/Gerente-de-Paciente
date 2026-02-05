"""Lógica de descoberta de servidores P2P"""
import os
import socket
from typing import Tuple, Dict, Any


def _discover_servers_impl() -> Tuple[Dict[str, Any], int]:
    """Lógica de discover (zeroconf ou scan). Retorna (json_dict, status_code)."""
    from flask import request
    
    local_ip = "127.0.0.1"
    port = int(os.getenv("PORT", 5000))
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            try:
                local_ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                local_ip = "127.0.0.1"
        finally:
            s.close()
        
        sp = request.environ.get("SERVER_PORT")
        if sp:
            port = int(sp)
    except (ValueError, TypeError):
        port = int(os.getenv("PORT", 5000))

    flask_host = (os.getenv("FLASK_HOST") or "127.0.0.1").strip()
    host_warning = ""
    if flask_host == "127.0.0.1":
        host_warning = (
            "Este servidor está escutando apenas em 127.0.0.1. Para outros PCs na rede "
            "serem encontrados e conectarem, defina FLASK_HOST=0.0.0.0 no .env e reinicie o Gerente. "
            "Verifique também se o Firewall do Windows permite o Gerente nas redes privadas."
        )

    discovery = (os.getenv("DISCOVERY") or "zeroconf").strip().lower()
    if discovery != "scan":
        try:
            from inicio.rede.zeroconf_discovery import get_discovered_servers

            raw = get_discovered_servers()
            discovered = [
                x for x in raw
                if not (str(x.get("ip")) == local_ip and int(x.get("port", 0)) == port)
            ]
        except Exception:
            discovered = []
        out = {"success": True, "local_ip": local_ip, "port": port, "servers": discovered}
        if host_warning:
            out["host_warning"] = host_warning
        return out, 200

    return _scan_discover(local_ip, port, host_warning)


def _scan_discover(local_ip: str, port: int, host_warning: str = "") -> Tuple[Dict[str, Any], int]:
    """Implementação de descoberta por scan de rede"""
    import ipaddress
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor, as_completed

    discovered = []
    targets = []
    targets_env = os.getenv("SYNC_TARGETS", "").strip()
    cidrs_env = os.getenv("SYNC_SCAN_CIDRS", "").strip()
    max_targets = int(os.getenv("SYNC_MAX_TARGETS", "1024"))

    def norm(v):
        v = (v or "").strip()
        if not v:
            return None
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            try:
                return socket.gethostbyname(v)
            except Exception:
                return None

    if targets_env:
        for raw in targets_env.replace(";", ",").split(","):
            ip = norm(raw)
            if ip and ip != local_ip:
                targets.append(ip)
    elif cidrs_env:
        for raw in cidrs_env.replace(";", ",").split(","):
            raw = raw.strip()
            if not raw:
                continue
            try:
                nw = ipaddress.ip_network(raw, strict=False)
            except ValueError:
                continue
            for h in nw.hosts():
                if len(targets) >= max_targets:
                    break
                ip = str(h)
                if ip != local_ip:
                    targets.append(ip)
    else:
        parts = local_ip.split(".")
        base = ".".join(parts[:-1])
        for i in range(1, 255):
            ip = f"{base}.{i}"
            if ip != local_ip:
                targets.append(ip)
    if len(targets) > max_targets:
        targets = targets[:max_targets]

    def check(ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((ip, port)) != 0:
                return None
            sock.close()

            try:
                req = urllib.request.Request(f"http://{ip}:{port}/api/version")
                r = urllib.request.urlopen(req, timeout=1)
                if r.status != 200:
                    return None
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = ip
                return {"ip": ip, "port": port, "hostname": hostname}
            except Exception:
                return None
        except Exception:
            return None

    workers = min(100, max(1, len(targets)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed(ex.submit(check, ip) for ip in targets):
            srv = f.result()
            if srv:
                discovered.append(srv)
    out = {"success": True, "local_ip": local_ip, "port": port, "servers": discovered}
    if host_warning:
        out["host_warning"] = host_warning
    return out, 200
