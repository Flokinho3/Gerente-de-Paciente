"""
API: CRUD de pacientes.
"""
from flask import Blueprint, jsonify, request
from concurrent.futures import ThreadPoolExecutor
import traceback

from .db import db
from .event_logger import log_event

bp = Blueprint("api_pacientes", __name__, url_prefix="/api")

_sync_executor = ThreadPoolExecutor(max_workers=2)


def _sync_paciente_background(paciente_id: str, paciente_data: dict):
    """Sincroniza um paciente específico com VPS em background"""
    try:
        from gerente.vps_client import get_vps_client
        client = get_vps_client()
        if not client:
            log_event("VPS não disponível para sync de paciente", "warning")
            return
        result = client.sync_pacientes([paciente_data])
        if result.get("success"):
            log_event(f"Paciente {paciente_id} sincronizado com VPS", "success")
        else:
            log_event(f"Erro ao sincronizar paciente {paciente_id}: {result.get('message', 'erro desconhecido')}", "warning")
    except Exception as e:
        log_event(f"Exceção ao sync background paciente {paciente_id}: {str(e)}", "error")


@bp.route("/salvar_paciente", methods=["POST"])
def salvar_paciente():
    try:
        data = request.get_json()
        if not data:
            log_event("Salvar paciente: dados não fornecidos", "warning")
            return jsonify({"success": False, "message": "Dados inválidos"}), 400
        if "identificacao" not in data:
            log_event("Salvar paciente: campo 'identificacao' ausente", "warning")
            return jsonify({"success": False, "message": "Dados inválidos - faltando identificacao"}), 400
        if "avaliacao" not in data:
            log_event("Salvar paciente: campo 'avaliacao' ausente", "warning")
            return jsonify({"success": False, "message": "Dados inválidos - faltando avaliacao"}), 400
        nome = data["identificacao"].get("nome_gestante", "").strip()
        if not nome:
            return jsonify({"success": False, "message": "Nome da gestante é obrigatório"}), 400
        resultado = db.adicionar_paciente(data)
        if resultado.get("success"):
            paciente_id = resultado.get("id")
            # Enviar dados completos para o sync
            _sync_executor.submit(_sync_paciente_background, paciente_id, data)
        return jsonify(resultado)
    except Exception as e:
        log_event(f"Erro ao salvar paciente: {traceback.format_exc()}", "error")
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
        log_event(f"Erro ao buscar pacientes: {traceback.format_exc()}", "error")
        return jsonify({"success": False, "message": str(e), "error": str(e)}), 500


@bp.route("/atualizar_paciente/<paciente_id>", methods=["PUT"])
def atualizar_paciente(paciente_id):
    try:
        data = request.get_json()
        if not data:
            log_event(f"Atualizar paciente {paciente_id}: dados não fornecidos", "warning")
            return jsonify({"success": False, "message": "Dados inválidos"}), 400
        
        # Validação básica
        if not isinstance(data.get('identificacao'), dict) or not isinstance(data.get('avaliacao'), dict):
            # Tentar prosseguir se db.atualizar_paciente for robusto, 
            # mas vamos exigir os campos mínimos para consistência.
            # No entanto, para não quebrar o frontend se ele mandar algo parcial,
            # vamos apenas logar um warning mas permitir, já que o DB agora aguenta.
            log_event(f"Atualizar paciente {paciente_id}: estrutura de dados incompleta enviada", "warning")

        resultado = db.atualizar_paciente(paciente_id, data)
        if resultado.get("success"):
            log_event(f"Paciente {paciente_id} atualizado com sucesso", "success")
            _sync_executor.submit(_sync_paciente_background, paciente_id, data)
            return jsonify(resultado)
        else:
            log_event(f"Falha ao atualizar paciente {paciente_id}: {resultado.get('message')}", "warning")
            return jsonify(resultado), 404
    except Exception as e:
        log_event(f"Erro ao atualizar paciente {paciente_id}: {traceback.format_exc()}", "error")
        return jsonify({"success": False, "message": f"Erro interno: {str(e)}"}), 500


@bp.route("/deletar_paciente/<paciente_id>", methods=["DELETE"])
def deletar_paciente(paciente_id):
    try:
        resultado = db.deletar_paciente(paciente_id)
        if resultado["success"]:
            return jsonify(resultado)
        return jsonify(resultado), 404
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao deletar: {str(e)}"}), 500
