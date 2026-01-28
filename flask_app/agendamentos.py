"""
API: CRUD de agendamentos.
"""
import uuid

from flask import Blueprint, jsonify, request

from .db import db

bp = Blueprint("api_agendamentos", __name__, url_prefix="/api")


@bp.route("/agendamentos", methods=["GET"])
def listar_agendamentos():
    try:
        agendamentos = db.listar_agendamentos(
            paciente_id=request.args.get("paciente_id"),
            data_inicio=request.args.get("data_inicio"),
            data_fim=request.args.get("data_fim"),
            status=request.args.get("status"),
        )
        return jsonify({"success": True, "agendamentos": agendamentos})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao listar agendamentos: {str(e)}"}), 500


@bp.route("/agendamentos", methods=["POST"])
def criar_agendamento():
    try:
        data = request.get_json()
        paciente_id = data.get("paciente_id")
        data_consulta = data.get("data_consulta")
        hora_consulta = data.get("hora_consulta")
        if not paciente_id or not data_consulta or not hora_consulta:
            return jsonify({
                "success": False,
                "message": "Dados obrigatórios faltando: paciente_id, data_consulta, hora_consulta",
            }), 400
        agendamento_id = str(uuid.uuid4())
        resultado = db.criar_agendamento(
            agendamento_id=agendamento_id,
            paciente_id=paciente_id,
            data_consulta=data_consulta,
            hora_consulta=hora_consulta,
            tipo_consulta=data.get("tipo_consulta"),
            observacoes=data.get("observacoes"),
            status=data.get("status", "agendado"),
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar agendamento: {str(e)}"}), 500


@bp.route("/agendamentos/<agendamento_id>", methods=["GET"])
def obter_agendamento(agendamento_id):
    try:
        agendamento = db.obter_agendamento(agendamento_id)
        if agendamento:
            return jsonify({"success": True, "agendamento": agendamento})
        return jsonify({"success": False, "message": "Agendamento não encontrado"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao obter agendamento: {str(e)}"}), 500


@bp.route("/agendamentos/<agendamento_id>", methods=["PUT"])
def atualizar_agendamento(agendamento_id):
    try:
        data = request.get_json()
        resultado = db.atualizar_agendamento(
            agendamento_id=agendamento_id,
            data_consulta=data.get("data_consulta"),
            hora_consulta=data.get("hora_consulta"),
            tipo_consulta=data.get("tipo_consulta"),
            observacoes=data.get("observacoes"),
            status=data.get("status"),
        )
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao atualizar agendamento: {str(e)}"}), 500


@bp.route("/agendamentos/<agendamento_id>", methods=["DELETE"])
def deletar_agendamento(agendamento_id):
    try:
        resultado = db.excluir_agendamento(agendamento_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao deletar agendamento: {str(e)}"}), 500
