"""
Módulo de Sincronização - Estrutura Modular
Cada endpoint está em seu próprio arquivo para melhor organização
"""
from flask import Blueprint

# Importar helpers
from .helpers import (
    _registros_identicos,
    _marcar_conflito_paciente,
    _marcar_conflito_agendamento
)

# Importar implementações P2P
from .p2p_discover import _discover_servers_impl
from .p2p_merge import _merge_impl


def create_sync_blueprint():
    """Cria blueprint para sincronização P2P local"""
    from flask import jsonify
    
    bp = Blueprint('sync', __name__, url_prefix='/api/sync')
    
    # Importar endpoints P2P
    from .p2p_endpoints import register_p2p_endpoints
    register_p2p_endpoints(bp)
    
    return bp


def create_vps_blueprint():
    """Cria blueprint para sincronização VPS"""
    bp = Blueprint('vps', __name__, url_prefix='/api/vps')
    
    # Importar e registrar todos os endpoints VPS
    from .vps_status import register_vps_status
    from .vps_sync import register_vps_sync
    from .vps_data import register_vps_data
    from .vps_divergencias import register_vps_divergencias
    
    register_vps_status(bp)
    register_vps_sync(bp)
    register_vps_data(bp)
    register_vps_divergencias(bp)
    
    return bp
