"""Endpoints P2P de sincronização"""
from flask import Blueprint, jsonify, request
from .p2p_discover import _discover_servers_impl
from .p2p_merge import _merge_impl
from ..db import db
from ...config import get_pc_id


def register_p2p_endpoints(bp: Blueprint):
    """Registra todos os endpoints P2P no blueprint"""
    
    @bp.route("/discover", methods=["GET"])
    def discover_servers():
        out, code = _discover_servers_impl()
        return jsonify(out), code

    @bp.route("/data", methods=["GET"])
    def get_sync_data():
        try:
            incluir = request.args.get("incluir_removidos", "false").lower() == "true"
            pacientes = db.buscar_pacientes(incluir_removidos=incluir)
            agendamentos = db.listar_agendamentos()
            return jsonify({
                "success": True,
                "pc_id": get_pc_id(),
                "pacientes": pacientes,
                "agendamentos": agendamentos,
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/merge", methods=["POST"])
    def merge_sync_data():
        try:
            out, code = _merge_impl()
            return jsonify(out), code
        except Exception as e:
            import traceback
            return jsonify({
                "success": False,
                "message": f"Erro ao sincronizar: {str(e)}",
                "traceback": traceback.format_exc(),
            }), 500

    @bp.route("/conflitos", methods=["GET"])
    def listar_conflitos():
        try:
            return jsonify(db.listar_conflitos())
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/conflitos/resolver", methods=["POST"])
    def resolver_conflito():
        try:
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
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/remover_pacientes", methods=["POST"])
    def remover_pacientes_confirmados():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            ids = data.get("paciente_ids", [])
            if not ids:
                return jsonify({"success": False, "message": "Nenhum ID fornecido"}), 400
            return jsonify(db.remover_pacientes(ids))
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
