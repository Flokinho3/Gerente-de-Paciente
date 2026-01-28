"""
Health check e registro de peers (DISCOVERY=scan).
"""
import os
from datetime import datetime

from flask import Blueprint, jsonify, request

from .db import _get_local_ip, _ip_sort_key, get_discovery_state

bp = Blueprint("discovery", __name__)


@bp.route("/health", methods=["GET"])
def health():
    try:
        port = int(request.environ.get("SERVER_PORT") or os.getenv("PORT", 5000))
    except (ValueError, TypeError):
        port = int(os.getenv("PORT", 5000))
    ip = _get_local_ip()
    return jsonify({"ok": True, "ip": ip, "port": port, "status": "ok"})


@bp.route("/register", methods=["POST"])
def register():
    _discovery_peers, _registered_peers, _leader_lock = get_discovery_state()
    try:
        data = request.get_json() or {}
        ip = (data.get("ip") or "").strip()
        port = int(data.get("port", 5000))
    except (ValueError, TypeError):
        return jsonify({"ok": False, "message": "Payload inválido: {ip, port}"}), 400
    if not ip:
        return jsonify({"ok": False, "message": "ip obrigatório"}), 400
    my_ip = _get_local_ip()
    with _leader_lock:
        peers = list(_discovery_peers)
    if not peers:
        return jsonify({"ok": True, "registered": False, "message": "Nenhum peer ainda"})
    min_peer = min(peers, key=lambda p: _ip_sort_key(p["ip"], p.get("port", 5000)))
    if min_peer["ip"] != my_ip:
        return jsonify({"ok": True, "registered": False, "message": "Não sou o líder"})
    now = datetime.now().timestamp()
    with _leader_lock:
        for p in _registered_peers:
            if p.get("ip") == ip and p.get("port") == port:
                p["ts"] = now
                return jsonify({"ok": True, "registered": True})
        _registered_peers.append({"ip": ip, "port": port, "ts": now})
    return jsonify({"ok": True, "registered": True})
