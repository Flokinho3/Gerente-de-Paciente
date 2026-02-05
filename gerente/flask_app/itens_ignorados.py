"""
API: Gerenciamento de itens ignorados temporariamente durante importação.
Itens ficam disponíveis por 5 dias para possível recuperação.
"""
from flask import Blueprint, jsonify, request

from .db import db

bp = Blueprint("api_itens_ignorados", __name__, url_prefix="/api/itens_ignorados")


@bp.route("/listar", methods=["GET"])
def listar_itens_ignorados():
    """Lista todos os itens ignorados não expirados."""
    try:
        # Limpar itens expirados antes de listar
        db.limpar_itens_ignorados_expirados()
        
        # Listar apenas não expirados
        resultado = db.listar_itens_ignorados(apenas_nao_expirados=True)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao listar itens ignorados: {str(e)}"}), 500


@bp.route("/restaurar/<item_id>", methods=["POST"])
def restaurar_item(item_id):
    """Restaura um item ignorado para o processo de importação."""
    try:
        resultado = db.restaurar_item_ignorado(item_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao restaurar item: {str(e)}"}), 500


@bp.route("/remover/<item_id>", methods=["DELETE"])
def remover_item(item_id):
    """Remove permanentemente um item ignorado."""
    try:
        resultado = db.remover_item_ignorado(item_id)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao remover item: {str(e)}"}), 500


@bp.route("/limpar_expirados", methods=["DELETE"])
def limpar_expirados():
    """Remove todos os itens ignorados que já expiraram."""
    try:
        resultado = db.limpar_itens_ignorados_expirados()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao limpar itens expirados: {str(e)}"}), 500


@bp.route("/atualizar/<item_id>", methods=["PUT"])
def atualizar_item(item_id):
    """Atualiza os dados de um item ignorado (para edição)."""
    try:
        data = request.get_json()
        if not data or "dados_backup" not in data:
            return jsonify({"success": False, "message": "Dados do backup não fornecidos"}), 400
        
        # Buscar item ignorado
        itens = db.listar_itens_ignorados(apenas_nao_expirados=False)
        if not itens.get("success"):
            return jsonify({"success": False, "message": "Erro ao buscar item"}), 500
        
        item = None
        for i in itens.get("itens", []):
            if i["id"] == item_id:
                item = i
                break
        
        if not item:
            return jsonify({"success": False, "message": "Item não encontrado"}), 404
        
        # Remover item antigo
        db.remover_item_ignorado(item_id)
        
        # Adicionar com dados atualizados
        import json
        novo_item = db.adicionar_item_ignorado(
            paciente_id=item["paciente_id"],
            dados_backup=data["dados_backup"],
            origem_backup=item["origem_backup"],
            motivo="Editado e atualizado"
        )
        
        return jsonify({
            "success": True,
            "message": "Item atualizado com sucesso",
            "id": novo_item.get("id")
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao atualizar item: {str(e)}"}), 500
