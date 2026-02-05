"""Endpoints de status VPS"""
from flask import Blueprint, jsonify, request
import requests
import os


def get_vps_client():
    """Retorna sessão autenticada para o VPS"""
    vps_url = os.getenv('VPS_URL', '').strip()
    password = os.getenv('VPS_PASSWORD', '').strip()
    if not vps_url or not password:
        raise ValueError('VPS não configurado')
    session = requests.Session()
    session.headers.update({'X-API-Password': password})
    return session, vps_url


def register_vps_status(bp: Blueprint):
    """Registra endpoints de status VPS"""

    def _check_local_auth():
        local_pwd = os.getenv('LOCAL_API_PASSWORD', '').strip()
        if not local_pwd:
            return True  # Sem senha definida, mantém compatibilidade local
        provided = request.headers.get('X-Local-Auth') or request.headers.get('X-API-Password')
        return provided == local_pwd
    
    @bp.route("/status", methods=["GET"])
    def vps_status():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            session, vps_url = get_vps_client()
            r = session.get(f"{vps_url}/api/vps/status", timeout=10)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao consultar status"}), 500

    @bp.route("/pendentes", methods=["GET"])
    def vps_pendentes():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from ..db import db, get_db
            pacientes_local = db.buscar_pacientes()
            agendamentos_local = db.listar_agendamentos()
            session, vps_url = get_vps_client()
            r = session.post(f"{vps_url}/api/vps/compare", json={"tables": ["pacientes", "agendamentos"]}, timeout=10)
            compare = r.json()
            return jsonify({"success": True, "locais": {"pacientes": len(pacientes_local), "agendamentos": len(agendamentos_local)}, "vps": compare})
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao consultar pendentes"}), 500

    @bp.route("/sync/status", methods=["GET"])
    def vps_sync_status():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_sync_manager import get_sync_manager
            manager = get_sync_manager()
            status = manager.get_status_sync()
            return jsonify({"success": True, "sync_running": status.get("sync_ativa", False), "last_sync": status.get("ultima_sync")})
        except Exception as e:
            import traceback
            return jsonify({"success": False, "message": "Erro ao consultar status"}), 500

    @bp.route("/conflitos", methods=["GET"])
    def vps_conflitos():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from ..db import db
            return jsonify(db.listar_conflitos())
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao listar conflitos"}), 500

    @bp.route("/conflitos/resolver", methods=["POST"])
    def vps_resolver_conflito():
        try:
            from flask import request
            from ..db import db
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            rid = data.get("registro_id")
            tipo = data.get("tipo")
            acao = data.get("acao")
            dados_remotos = data.get("dados_remotos")
            if not rid or not tipo or not acao:
                return jsonify({"success": False, "message": "Dados incompletos"}), 400
            return jsonify(db.resolver_conflito(rid, tipo, acao, dados_remotos))
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao resolver conflito"}), 500
