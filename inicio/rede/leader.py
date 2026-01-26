"""
Descoberta passiva e liderança emergente (menor IP ativo).
- Scan /24 na rede local via GET /health
- Líder = menor IP entre os peers vivos
- Não-líderes registram-se no líder via POST /register
"""
import json
import os
import socket
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        finally:
            s.close()
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'


def _ip_sort_key(ip_str, port=5000):
    try:
        import ipaddress
        a = ipaddress.ip_address(ip_str)
        return (tuple(int(x) for x in str(a).split('.')), port)
    except Exception:
        return ((255, 255, 255, 255), port)


def scan_local_24(port, timeout=0.6):
    """
    Varre o /24 da rede local com GET /health. Inclui a si mesmo.
    Retorna [{"ip", "port", "ts"}, ...].
    """
    local_ip = get_local_ip()
    try:
        parts = [int(x) for x in local_ip.split('.') if x.isdigit()]
        if len(parts) != 4:
            base = '192.168.1'
        else:
            base = '.'.join(str(p) for p in parts[:3])
    except Exception:
        base = '192.168.1'

    targets = [f'{base}.{i}' for i in range(1, 255) if f'{base}.{i}' != local_ip]
    now = time.time()
    peers = []

    def check(ip):
        try:
            url = f'http://{ip}:{port}/health'
            req = urllib.request.Request(url, timeout=timeout)
            with urllib.request.urlopen(req) as resp:
                if resp.status != 200:
                    return None
                data = json.loads(resp.read().decode())
                if not data.get('ok') and data.get('status') != 'ok':
                    return None
                return {
                    'ip': data.get('ip', ip),
                    'port': int(data.get('port', port)),
                    'ts': now
                }
        except Exception:
            return None

    workers = min(50, max(1, len(targets)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for r in as_completed([ex.submit(check, ip) for ip in targets]):
            p = r.result()
            if p:
                peers.append(p)

    # Incluir a si mesmo
    peers.append({'ip': local_ip, 'port': port, 'ts': now})
    return peers


def run_one_cycle(port=None):
    """
    Executa um ciclo: scan /24, atualiza discovery no flask_app, e,
    se não for líder, POST /register no líder.
    """
    port = int(port or os.getenv('PORT', 5000))
    from flask_app import atualizar_discovery_peers

    peers = scan_local_24(port)
    atualizar_discovery_peers(peers)

    if not peers:
        return

    min_peer = min(peers, key=lambda p: _ip_sort_key(p['ip'], p.get('port', port)))
    leader_ip = min_peer['ip']
    leader_port = min_peer.get('port', port)
    my_ip = get_local_ip()

    if leader_ip == my_ip:
        return

    try:
        url = f'http://{leader_ip}:{leader_port}/register'
        data = json.dumps({'ip': my_ip, 'port': port}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=2):
            pass
    except Exception:
        pass


def run_scan_loop(port=None, interval_sec=None, daemon=True):
    """
    Inicia uma thread que executa run_one_cycle a cada interval_sec segundos.
    interval_sec: default de LEADER_SCAN_INTERVAL ou 15.
    Retorna a thread (já iniciada).
    """
    import threading

    port = int(port or os.getenv('PORT', 5000))
    interval = float(interval_sec or os.getenv('LEADER_SCAN_INTERVAL', '15'))

    def _loop():
        while True:
            try:
                run_one_cycle(port)
            except Exception:
                pass
            time.sleep(interval)

    t = threading.Thread(target=_loop, daemon=daemon)
    t.start()
    return t
