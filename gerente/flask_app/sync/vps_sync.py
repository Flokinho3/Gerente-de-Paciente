"""Endpoints de sincronização VPS"""
from flask import Blueprint, jsonify, request
import os
from werkzeug.utils import secure_filename

# Carregar variáveis de ambiente do .env
try:
    from gerente.env_loader import load_env
    load_env()
except ImportError:
    pass


def register_vps_sync(bp: Blueprint):
    """Registra endpoints de sync VPS"""

    def _get_vps_env():
        vps_url = os.getenv('VPS_URL', '').strip()
        password = os.getenv('VPS_PASSWORD', '').strip()
        if not vps_url or not password:
            raise ValueError('VPS não configurado')
        allow_insecure = os.getenv('ALLOW_INSECURE_VPS', 'false').lower() == 'true'
        if not vps_url.startswith('https://') and not allow_insecure:
            raise ValueError('VPS_URL deve usar HTTPS (defina ALLOW_INSECURE_VPS=true para liberar)')
        return vps_url, password

    def _get_upload_limits():
        max_mb = int(os.getenv('MAX_VPS_UPLOAD_MB', '10'))
        return max_mb * 1024 * 1024

    def _allowed_upload(filename: str) -> bool:
        allowed = {'.db', '.sqlite', '.sqlite3'}
        _, ext = os.path.splitext(filename.lower())
        return ext in allowed

    def _check_local_auth():
        local_pwd = os.getenv('LOCAL_API_PASSWORD', '').strip()
        if not local_pwd:
            return True  # Sem senha definida, mantém compatibilidade local
        provided = request.headers.get('X-Local-Auth') or request.headers.get('X-API-Password')
        return provided == local_pwd
    
    @bp.route("/sync/iniciar", methods=["POST"])
    def vps_iniciar_sync():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_sync_manager import iniciar_sync_vps
            iniciar_sync_vps(intervalo_minutos=30)
            return jsonify({"success": True, "message": "Sincronização VPS iniciada"})
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao iniciar sincronização"}), 500

    @bp.route("/sync/executar", methods=["POST"])
    def vps_sync_executar():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_sync_manager import sincronizar_vps_agora
            result = sincronizar_vps_agora()
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao executar sincronização"}), 500

    @bp.route("/sync/parar", methods=["POST"])
    def vps_parar_sync():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            from gerente.vps_sync_manager import parar_sync_vps
            parar_sync_vps()
            return jsonify({"success": True, "message": "Sincronização parada"})
        except Exception as e:
            return jsonify({"success": False, "message": "Erro ao parar sincronização"}), 500

    @bp.route("/sync/seletivo", methods=["POST"])
    def vps_sync_seletivo():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
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
            return jsonify({"success": False, "message": "Erro ao sincronizar seletivamente"}), 500

    @bp.route("/upload", methods=["POST"])
    def vps_upload():
        try:
            from flask import request
            import tempfile
            import os
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            session, vps_url = get_vps_client()
            if "file" not in request.files:
                return jsonify({"success": False, "message": "Nenhum arquivo enviado"}), 400
            file = request.files["file"]
            filename = secure_filename(file.filename or '')
            if not filename or not _allowed_upload(filename):
                return jsonify({"success": False, "message": "Arquivo inválido"}), 400
            max_bytes = _get_upload_limits()
            if request.content_length and request.content_length > max_bytes:
                return jsonify({"success": False, "message": "Arquivo excede o limite"}), 413
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                file.save(tmp.name)
                with open(tmp.name, "rb") as f:
                    r = session.post(f"{vps_url}/api/vps/upload", files={"file": f}, timeout=60)
            os.remove(tmp.name)
            return jsonify(r.json())
        except Exception as e:
            return jsonify({"success": False, "message": "Erro no upload"}), 500

    @bp.route("/download", methods=["GET"])
    def vps_download():
        try:
            if not _check_local_auth():
                return jsonify({"success": False, "message": "Unauthorized"}), 401
            session, vps_url = get_vps_client()
            r = session.get(f"{vps_url}/api/vps/download", timeout=60)
            output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "pacientes.db")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(r.content)
            return jsonify({"success": True, "path": output_path, "size": len(r.content)})
        except Exception as e:
            return jsonify({"success": False, "message": "Erro no download"}), 500


def get_vps_client():
    """Retorna sessão autenticada para o VPS"""
    import requests
    import os
    vps_url = os.getenv('VPS_URL', '').strip()
    password = os.getenv('VPS_PASSWORD', '').strip()
    if not vps_url or not password:
        raise ValueError('VPS não configurado')
    session = requests.Session()
    session.headers.update({'X-API-Password': password})
    return session, vps_url
