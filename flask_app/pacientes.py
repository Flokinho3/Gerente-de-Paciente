"""
API: CRUD de pacientes.
"""
from flask import Blueprint, jsonify, request

from .db import db

bp = Blueprint("api_pacientes", __name__, url_prefix="/api")


@bp.route("/salvar_paciente", methods=["POST"])
def salvar_paciente():
    try:
        data = request.get_json()
        if not data or "identificacao" not in data or "avaliacao" not in data:
            return jsonify({"success": False, "message": "Dados inválidos"}), 400
        nome = data["identificacao"].get("nome_gestante", "").strip()
        if not nome:
            return jsonify({"success": False, "message": "Nome da gestante é obrigatório"}), 400
        resultado = db.adicionar_paciente(data)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao salvar: {str(e)}"}), 500


@bp.route("/pacientes", methods=["GET"])
def listar_pacientes():
    try:
        filtro = {}
        if request.args.get("nome"):
            filtro["nome"] = request.args.get("nome")
        if request.args.get("unidade_saude"):
            filtro["unidade_saude"] = request.args.get("unidade_saude")
        pacientes = db.buscar_pacientes(filtro if filtro else None)
        return jsonify({"success": True, "total": len(pacientes), "pacientes": pacientes})
    except Exception as e:
        import traceback

        print(f"Erro ao buscar pacientes: {traceback.format_exc()}")
        return jsonify({"success": False, "message": str(e), "error": str(e)}), 500


@bp.route("/atualizar_paciente/<paciente_id>", methods=["PUT"])
def atualizar_paciente(paciente_id):
    try:
        data = request.get_json()
        if not data or "identificacao" not in data or "avaliacao" not in data:
            return jsonify({"success": False, "message": "Dados inválidos"}), 400
        resultado = db.atualizar_paciente(paciente_id, data)
        if resultado["success"]:
            return jsonify(resultado)
        return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao atualizar: {str(e)}"}), 500


@bp.route("/deletar_paciente/<paciente_id>", methods=["DELETE"])
def deletar_paciente(paciente_id):
    try:
        resultado = db.deletar_paciente(paciente_id)
        if resultado["success"]:
            return jsonify(resultado)
        return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao deletar: {str(e)}"}), 500
