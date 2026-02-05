"""Lógica de merge P2P"""
from typing import Tuple, Dict, Any
from flask import request
from .helpers import (
    _registros_identicos,
    _marcar_conflito_paciente,
    _marcar_conflito_agendamento
)
from ..db import db


def _merge_impl() -> Tuple[Dict[str, Any], int]:
    """Lógica do merge. Retorna (json_dict, status_code)."""
    data = request.get_json()
    if not data:
        return {"success": False, "message": "Dados não fornecidos"}, 400
    pacientes_remotos = data.get("pacientes", [])
    agendamentos_remotos = data.get("agendamentos", [])
    pc_id_remoto = data.get("pc_id")
    pacientes_locais = db.buscar_pacientes(incluir_removidos=True)
    pl_dict = {p["id"]: p for p in pacientes_locais}
    agendamentos_locais = db.listar_agendamentos()
    al_dict = {a["id"]: a for a in agendamentos_locais}
    pa = pu = pc = aa = au = ac = 0

    for pr in pacientes_remotos:
        pid = pr["id"]
        pl = pl_dict.get(pid)
        if not pl:
            try:
                db.inserir_registro(
                    pid,
                    pr,
                    arquivo_origem="sync",
                    data_salvamento=pr.get("data_salvamento"),
                    pc_id=pr.get("pc_id", pc_id_remoto),
                    ultima_modificacao=pr.get("ultima_modificacao"),
                    versao=pr.get("versao", 1),
                    status=pr.get("status", "ativo"),
                )
                pa += 1
            except Exception:
                pass
            continue
        sl, sr = pl.get("status", "ativo"), pr.get("status", "ativo")
        if (sl == "removido" and sr != "removido") or (sl != "removido" and sr == "removido"):
            _marcar_conflito_paciente(pid)
            pc += 1
            continue
        if sl == "removido" and sr == "removido":
            continue
        if _registros_identicos(pl, pr):
            continue
        uml = pl.get("ultima_modificacao") or pl.get("data_salvamento", "")
        umr = pr.get("ultima_modificacao") or pr.get("data_salvamento", "")
        if umr > uml:
            try:
                pr["pc_id"] = pr.get("pc_id", pc_id_remoto)
                db.atualizar_paciente(pid, pr)
                pu += 1
            except Exception:
                pass
        elif uml > umr:
            pass
        else:
            pcl = pl.get("pc_id", "")
            pcr = pr.get("pc_id", pc_id_remoto or "")
            if pcl != pcr or True:
                _marcar_conflito_paciente(pid)
                pc += 1

    for ar in agendamentos_remotos:
        aid = ar["id"]
        al = al_dict.get(aid)
        if not al:
            try:
                db.criar_agendamento(
                    aid,
                    ar["paciente_id"],
                    ar["data_consulta"],
                    ar["hora_consulta"],
                    ar.get("tipo_consulta"),
                    ar.get("observacoes"),
                    ar.get("status", "agendado"),
                    ar.get("data_criacao"),
                    ar.get("data_atualizacao"),
                    pc_id=ar.get("pc_id", pc_id_remoto),
                    ultima_modificacao=ar.get("ultima_modificacao"),
                    versao=ar.get("versao", 1),
                )
                aa += 1
            except Exception:
                pass
            continue
        sl, sr = al.get("status", "agendado"), ar.get("status", "agendado")
        if (sl == "removido" and sr != "removido") or (sl != "removido" and sr == "removido"):
            _marcar_conflito_agendamento(aid)
            ac += 1
            continue
        if sl == "removido" and sr == "removido":
            continue
        if _registros_identicos(al, ar, {"nome_gestante", "unidade_saude"}):
            continue
        uml = al.get("ultima_modificacao") or al.get("data_atualizacao", "")
        umr = ar.get("ultima_modificacao") or ar.get("data_atualizacao", "")
        if umr > uml:
            try:
                db.atualizar_agendamento(
                    aid,
                    ar["paciente_id"],
                    ar["data_consulta"],
                    ar["hora_consulta"],
                    ar.get("tipo_consulta"),
                    ar.get("observacoes"),
                    ar.get("status", "agendado"),
                    pc_id=ar.get("pc_id", pc_id_remoto),
                    ultima_modificacao=ar.get("ultima_modificacao"),
                )
                au += 1
            except Exception:
                pass
        elif uml > umr:
            pass
        else:
            _marcar_conflito_agendamento(aid)
            ac += 1

    return {
        "success": True,
        "message": "Sincronização concluída",
        "stats": {
            "pacientes_adicionados": pa,
            "pacientes_atualizados": pu,
            "pacientes_conflito": pc,
            "agendamentos_adicionados": aa,
            "agendamentos_atualizados": au,
            "agendamentos_conflito": ac,
        },
    }, 200
