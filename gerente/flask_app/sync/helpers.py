"""Funções auxiliares para sincronização"""
from datetime import datetime
from typing import Dict, Optional, Set
from ..db import db, get_db


def _registros_identicos(reg1: Dict, reg2: Dict, campos_ignorados: Optional[Set[str]] = None) -> bool:
    """Verifica se dois registros são idênticos, ignorando campos específicos"""
    if campos_ignorados is None:
        campos_ignorados = {"ultima_modificacao", "versao", "pc_id"}
    campos_ignorados = campos_ignorados | {"id"}
    todos = set(reg1.keys()) | set(reg2.keys())
    for campo in todos:
        if campo in campos_ignorados:
            continue
        if reg1.get(campo) != reg2.get(campo):
            return False
    return True


def _marcar_conflito_paciente(paciente_id: str):
    """Marca um paciente como em conflito"""
    try:
        paciente = db.buscar_paciente(paciente_id)
        if paciente and paciente.get("status") != "conflito":
            d = get_db()
            c = d.conn.cursor()
            c.execute(
                "UPDATE pacientes SET status = 'conflito', ultima_modificacao = ?, versao = versao + 1 WHERE id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), paciente_id),
            )
            d.conn.commit()
    except Exception:
        pass


def _marcar_conflito_agendamento(agendamento_id: str):
    """Marca um agendamento como em conflito"""
    try:
        ag = db.obter_agendamento(agendamento_id)
        if ag and ag.get("status") != "conflito":
            d = get_db()
            c = d.conn.cursor()
            c.execute(
                "UPDATE agendamentos SET status = 'conflito', ultima_modificacao = ?, versao = versao + 1 WHERE id = ?",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), agendamento_id),
            )
            d.conn.commit()
    except Exception:
        pass
