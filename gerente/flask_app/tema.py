"""
API: Tema (obter, salvar, padrão, salvar CSS).
"""
import hashlib
import json
import os
import re

from flask import Blueprint, jsonify, request

bp = Blueprint("api_tema", __name__, url_prefix="/api/tema")


@bp.route("/obter", methods=["GET"])
def obter_tema():
    return jsonify({
        "success": True,
        "message": "Tema obtido via cookie do navegador",
    })


@bp.route("/salvar", methods=["POST"])
def salvar_tema():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Dados do tema não fornecidos"}), 400
        if "nome" not in data or "cores" not in data:
            return jsonify({"success": False, "message": "Estrutura do tema inválida"}), 400
        if not isinstance(data["cores"], dict):
            return jsonify({"success": False, "message": "Campo cores deve ser um objeto"}), 400
        for key, color in data["cores"].items():
            if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
                return jsonify({
                    "success": False,
                    "message": f"Cor inválida para {key}: {color}. Deve ser hexadecimal (#RRGGBB)",
                }), 400
        theme_json = json.dumps(data)
        if len(theme_json) > 4000:
            return jsonify({"success": False, "message": "Tema muito grande para salvar"}), 400
        return jsonify({
            "success": True,
            "message": "Tema validado. Salvamento via cookie no navegador.",
            "tema": {"nome": data["nome"], "cores_count": len(data["cores"])},
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/padrao", methods=["GET"])
def obter_tema_padrao():
    tema = {
        "nome": "Padrão Hospitalar",
        "cores": {
            "--bg": "#f2f5f4",
            "--card": "#ffffff",
            "--primary": "#2f7d6d",
            "--primary-hover": "#266758",
            "--secondary": "#4a90a4",
            "--secondary-hover": "#3d7a8a",
            "--accent": "#e6f2ef",
            "--text": "#263238",
            "--text-muted": "#607d8b",
            "--success": "#2e7d32",
            "--success-light": "#c8e6c9",
            "--warning": "#f57c00",
            "--warning-light": "#ffe0b2",
            "--danger": "#c62828",
            "--danger-light": "#ffcdd2",
            "--info": "#0277bd",
            "--info-light": "#b3e5fc",
            "--border": "#d0d7d5",
            "--border-light": "#e8edec",
        },
    }
    return jsonify({"success": True, "tema": tema})


@bp.route("/salvar_css", methods=["POST"])
def salvar_css():
    try:
        data = request.get_json()
        if not data or "css" not in data:
            return jsonify({"success": False, "message": "CSS não fornecido"}), 400
        css_content = data["css"]
        if not css_content.strip():
            return jsonify({"success": False, "message": "CSS vazio"}), 400
        h = hashlib.md5(css_content.encode("utf-8")).hexdigest()[:8]
        filename = f"custom_{h}.css"
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        css_dir = os.path.join(base, "static", "css")
        os.makedirs(css_dir, exist_ok=True)
        path = os.path.join(css_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(css_content)
        return jsonify({"success": True, "filename": filename, "message": f"CSS salvo como {filename}"})
    except Exception as e:
        import traceback

        return jsonify({
            "success": False,
            "message": str(e),
            "traceback": traceback.format_exc(),
        }), 500
