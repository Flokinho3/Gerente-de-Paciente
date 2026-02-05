"""Endpoints de sincronização VPS"""
from flask import Blueprint, jsonify, request
import os


def register_vps_sync(bp: Blueprint):
    """Registra endpoints de sync VPS"""
    
    @bp.route("/sync/iniciar", methods=["POST"])
    def vps_iniciar_sync():
        try:
            from gerente.vps_sync_manager import iniciar_sync_vps
            iniciar_sync_vps(intervalo_minutos=30)
            return jsonify({"success": True, "message": "Sincronização VPS iniciada"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/sync/executar", methods=["POST"])
    def vps_sync_executar():
        try:
            from gerente.vps_sync_manager import sincronizar_vps_agora
            result = sincronizar_vps_agora()
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/sync/parar", methods=["POST"])
    def vps_parar_sync():
        try:
            from gerente.vps_sync_manager import parar_sync_vps
            parar_sync_vps()
            return jsonify({"success": True, "message": "Sincronização parada"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/sync/seletivo", methods=["POST"])
    def vps_sync_seletivo():
        try:
            from flask import request
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from gerente.vps_sync_manager import VpsSyncManager
            data = request.get_json()
            pacientes_ids = data.get("pacientes_ids", [])
            manager = VpsSyncManager()
            return jsonify(manager.sincronizar_seletivo(pacientes_ids))
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/upload", methods=["POST"])
    def vps_upload():
        try:
            from flask import request
            import tempfile
            import os
            session, vps_url = get_vps_client()
            if "file" in request.files:
                file = request.files["file"]
                temp_path = tempfile.mktemp(suffix=".db")
                file.save(temp_path)
                r = session.post(f"{vps_url}/api/vps/upload", files={"file": open(temp_path, "rb")}, timeout=60)
                os.remove(temp_path)
                return jsonify(r.json())
            else:
                return jsonify({"success": False, "message": "Nenhum arquivo enviado"}), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

    @bp.route("/download", methods=["GET"])
    def vps_download():
        try:
            session, vps_url = get_vps_client()
            r = session.get(f"{vps_url}/api/vps/download", timeout=60)
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pacientes.db")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(r.content)
            return jsonify({"success": True, "path": output_path, "size": len(r.content)})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500


def get_vps_client():
    """Retorna sessão autenticada para o VPS"""
    import requests
    import os
    vps_url = os.getenv('VPS_URL', 'http://168.231.95.33:8080')
    password = os.getenv('VPS_PASSWORD', '*******')
    session = requests.Session()
    session.headers.update({'X-API-Password': password})
    return session, vps_url
