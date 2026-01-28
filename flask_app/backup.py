"""
API: Backup e restauração do banco.
"""
import io
import json
from datetime import datetime

from flask import Blueprint, jsonify, make_response, request, send_file

from .db import db

bp = Blueprint("api_backup", __name__, url_prefix="/api/backup")


@bp.route("/criar", methods=["GET"])
def criar_backup():
    try:
        return jsonify(db.criar_backup())
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar backup: {str(e)}"}), 500


@bp.route("/download", methods=["GET"])
def download_backup():
    try:
        resultado = db.criar_backup()
        buf = io.BytesIO(json.dumps(resultado["backup"], ensure_ascii=False, indent=2).encode("utf-8"))
        buf.seek(0)
        name = f"backup_pacientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return make_response(
            send_file(buf, mimetype="application/json", as_attachment=True, download_name=name)
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao gerar arquivo de backup: {str(e)}"}), 500


@bp.route("/restaurar", methods=["POST"])
def restaurar_backup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados do backup não fornecidos"}), 400
        backup = data.get("backup") if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({"success": False, "message": "Backup deve ser uma lista de registros"}), 400
        resultado = db.restaurar_backup(backup)
        if resultado["success"]:
            return jsonify(resultado)
        return jsonify(resultado), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao restaurar backup: {str(e)}"}), 500


@bp.route("/validar", methods=["POST"])
def validar_backup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Backup não fornecido"}), 400
        backup = data.get("backup") if isinstance(data, dict) else data
        if not isinstance(backup, list):
            return jsonify({"success": False, "message": "Backup deve ser uma lista de pacientes"}), 400
        erros = []
        for idx, reg in enumerate(backup):
            if not isinstance(reg, dict):
                erros.append(f"Item {idx + 1} não é um objeto válido")
                continue
            id_ = reg.get("identificacao", {})
            av = reg.get("avaliacao", {})
            if not id_.get("nome_gestante"):
                erros.append(f"Item {idx + 1} não possui nome da gestante")
            if not isinstance(av, dict) or "consultas_pre_natal" not in av:
                erros.append(f"Item {idx + 1} com avaliação incompleta")
        if erros:
            return jsonify({"success": False, "message": "Backup inválido", "errors": erros}), 400
        return jsonify({"success": True, "message": "Backup válido", "total": len(backup)})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao validar backup: {str(e)}"}), 500


@bp.route("/limpar", methods=["DELETE"])
def limpar_banco_dados():
    try:
        return jsonify(db.limpar_todos_dados())
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao limpar banco de dados: {str(e)}"}), 500
