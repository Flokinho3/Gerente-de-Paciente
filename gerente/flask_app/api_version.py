"""
API: versão do sistema.
"""
from flask import Blueprint, jsonify

from .constants import BUILD_DATE, VERSION

bp = Blueprint("api_version", __name__, url_prefix="/api")


@bp.route("/version", methods=["GET"])
def get_version():
    return jsonify({"success": True, "version": VERSION, "build_date": BUILD_DATE})
