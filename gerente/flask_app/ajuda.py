"""
API: Abrir ajuda (Bloco de Notas).
"""
import os
import subprocess
import sys

from flask import Blueprint, jsonify

bp = Blueprint("api_ajuda", __name__, url_prefix="/api")


@bp.route("/abrir_ajuda", methods=["GET"])
def abrir_ajuda():
    try:
        caminho = None
        if getattr(sys, "frozen", False):
            if hasattr(sys, "_MEIPASS"):
                p = os.path.join(sys._MEIPASS, "COMO_USAR.txt")
                if os.path.exists(p):
                    caminho = p
            if not caminho:
                p = os.path.join(os.path.dirname(sys.executable), "COMO_USAR.txt")
                if os.path.exists(p):
                    caminho = p
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            p1 = os.path.join(base, "COMO_USAR.txt")
            p2 = os.path.join(base, "outros", "COMO_USAR.txt")
            caminho = p1 if os.path.exists(p1) else (p2 if os.path.exists(p2) else None)
        if not caminho or not os.path.exists(caminho):
            return jsonify({"success": False, "message": "Arquivo de ajuda não encontrado"}), 404
        subprocess.Popen(["notepad.exe", caminho])
        return jsonify({"success": True, "message": "Arquivo de ajuda aberto no Bloco de Notas"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
