"""
API: Sincronização, descoberta de servidores, conflitos.
"""
import os
from datetime import datetime
from typing import Dict

from flask import jsonify, request

from .db import db, get_db

# Helpers usados pelo merge


def _registros_identicos(reg1: Dict, reg2: Dict, campos_ignorados: set = None) -> bool:
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


def _discover_servers_impl():
    """Lógica de discover (zeroconf ou scan). Retorna (json_dict, status_code)."""
    import socket

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except Exception:
            try:
                local_ip = socket.gethostbyname(socket.gethostname())
            except Exception:
                local_ip = "127.0.0.1"
        finally:
            s.close()
        sp = request.environ.get("SERVER_PORT")
        port = int(sp) if sp else int(os.getenv("PORT", 5000))
    except (ValueError, TypeError):
        port = int(os.getenv("PORT", 5000))

    flask_host = (os.getenv("FLASK_HOST") or "127.0.0.1").strip()
    host_warning = None
    if flask_host == "127.0.0.1":
        host_warning = (
            "Este servidor está escutando apenas em 127.0.0.1. Para outros PCs na rede "
            "serem encontrados e conectarem, defina FLASK_HOST=0.0.0.0 no .env e reinicie o Gerente. "
            "Verifique também se o Firewall do Windows permite o Gerente nas redes privadas."
        )

    discovery = (os.getenv("DISCOVERY") or "zeroconf").strip().lower()
    if discovery != "scan":
        try:
            from inicio.rede.zeroconf_discovery import get_discovered_servers

            raw = get_discovered_servers()
            discovered = [
                x for x in raw
                if not (str(x.get("ip")) == local_ip and int(x.get("port", 0)) == port)
            ]
        except Exception:
            discovered = []
        out = {"success": True, "local_ip": local_ip, "port": port, "servers": discovered}
        if host_warning:
            out["host_warning"] = host_warning
        return out, 200

    # DISCOVERY=scan
    import ipaddress
    from concurrent.futures import ThreadPoolExecutor, as_completed

    discovered = []
    targets = []
    targets_env = os.getenv("SYNC_TARGETS", "").strip()
    cidrs_env = os.getenv("SYNC_SCAN_CIDRS", "").strip()
    max_targets = int(os.getenv("SYNC_MAX_TARGETS", "1024"))

    def norm(v):
        v = (v or "").strip()
        if not v:
            return None
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            try:
                return socket.gethostbyname(v)
            except Exception:
                return None

    if targets_env:
        for raw in targets_env.replace(";", ",").split(","):
            ip = norm(raw)
            if ip and ip != local_ip:
                targets.append(ip)
    elif cidrs_env:
        for raw in cidrs_env.replace(";", ",").split(","):
            raw = raw.strip()
            if not raw:
                continue
            try:
                nw = ipaddress.ip_network(raw, strict=False)
            except ValueError:
                continue
            for h in nw.hosts():
                if len(targets) >= max_targets:
                    break
                ip = str(h)
                if ip != local_ip:
                    targets.append(ip)
    else:
        parts = local_ip.split(".")
        base = ".".join(parts[:-1])
        for i in range(1, 255):
            ip = f"{base}.{i}"
            if ip != local_ip:
                targets.append(ip)
    if len(targets) > max_targets:
        targets = targets[:max_targets]

    def check(ip):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            if sock.connect_ex((ip, port)) != 0:
                return None
            sock.close()
            import urllib.request

            try:
                req = urllib.request.Request(f"http://{ip}:{port}/api/version", timeout=1)
                r = urllib.request.urlopen(req)
                if r.status != 200:
                    return None
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except Exception:
                    hostname = ip
                return {"ip": ip, "port": port, "hostname": hostname}
            except Exception:
                return None
        except Exception:
            return None

    workers = min(100, max(1, len(targets)))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for f in as_completed(ex.submit(check, ip) for ip in targets):
            srv = f.result()
            if srv:
                discovered.append(srv)
    out = {"success": True, "local_ip": local_ip, "port": port, "servers": discovered}
    if host_warning:
        out["host_warning"] = host_warning
    return out, 200


def _merge_impl():
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


def create_sync_blueprint():
    from flask import Blueprint

    bp = Blueprint("api_sync", __name__, url_prefix="/api/sync")

    @bp.route("/discover", methods=["GET"])
    def discover_servers():
        out, code = _discover_servers_impl()
        return jsonify(out), code

    @bp.route("/data", methods=["GET"])
    def get_sync_data():
        try:
            from config import get_pc_id

            incluir = request.args.get("incluir_removidos", "false").lower() == "true"
            pacientes = db.buscar_pacientes(incluir_removidos=incluir)
            agendamentos = db.listar_agendamentos()
            return jsonify({
                "success": True,
                "pc_id": get_pc_id(),
                "pacientes": pacientes,
                "agendamentos": agendamentos,
            })
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/merge", methods=["POST"])
    def merge_sync_data():
        try:
            out, code = _merge_impl()
            return jsonify(out), code
        except Exception as e:
            import traceback

            return jsonify({
                "success": False,
                "message": f"Erro ao sincronizar: {str(e)}",
                "traceback": traceback.format_exc(),
            }), 500

    @bp.route("/conflitos", methods=["GET"])
    def listar_conflitos():
        try:
            return jsonify(db.listar_conflitos())
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/conflitos/resolver", methods=["POST"])
    def resolver_conflito():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            rid = data.get("registro_id")
            tipo = data.get("tipo")
            acao = data.get("acao")
            dados_remotos = data.get("dados_remotos")
            if not rid or not tipo or not acao:
                return jsonify({"success": False, "message": "Dados incompletos"}), 400
            return jsonify(db.resolver_conflito(rid, tipo, acao, dados_remotos))
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/remover_pacientes", methods=["POST"])
    def remover_pacientes_confirmados():
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "message": "Dados não fornecidos"}), 400
            ids = data.get("paciente_ids", [])
            if not ids:
                return jsonify({"success": False, "message": "Nenhum ID fornecido"}), 400
            return jsonify(db.remover_pacientes(ids))
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    return bp
