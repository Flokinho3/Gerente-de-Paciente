"""
Rotas de páginas HTML (render_template).
"""
from flask import Blueprint, render_template

from .constants import VERSION

bp = Blueprint("paginas", __name__)


@bp.route("/")
def home():
    return render_template("Home.html")


@bp.route("/novo_paciente")
def novo_paciente():
    return render_template("novo_paciente.html")


@bp.route("/pacientes")
def pacientes():
    return render_template("pacientes.html")


@bp.route("/exportar")
def exportar():
    return render_template("exportar.html")


@bp.route("/bd")
def bd():
    return render_template("bd.html")


@bp.route("/conflitos")
def conflitos():
    return render_template("conflitos.html", version=VERSION)


@bp.route("/agendamentos")
def agendamentos():
    return render_template("agendamentos.html")


@bp.route("/aparencia")
def aparencia():
    return render_template("aparencia.html")


@bp.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


@bp.route("/ranks")
def ranks():
    return render_template("ranks.html")
