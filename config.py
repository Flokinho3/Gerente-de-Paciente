"""
Módulo de configuração para gerenciar identificador único de instalação (PC_ID)
"""
import os
import uuid
import socket
from typing import Optional


def get_data_dir() -> str:
    """Retorna o diretório de dados padrão"""
    import sys
    if getattr(sys, 'frozen', False):
        # Executável: usa diretório do executável
        base_dir = os.path.dirname(sys.executable)
    else:
        # Modo desenvolvimento: usa diretório do script
        base_dir = os.path.dirname(__file__)
    
    return os.path.join(base_dir, 'data')


def get_pc_id() -> str:
    """
    Obtém ou gera o PC_ID único para esta instalação.
    
    Prioridades:
    1. Variável de ambiente PC_ID
    2. Arquivo data/.pc_id
    3. Gerar novo UUID e salvar
    """
    from env_loader import load_env
    load_env()

    # Prioridade 1: variável de ambiente
    env_pc_id = os.getenv('PC_ID')
    if env_pc_id:
        return env_pc_id
    
    # Prioridade 2: arquivo .pc_id
    data_dir = get_data_dir()
    pc_id_file = os.path.join(data_dir, '.pc_id')
    
    # Criar diretório se não existir
    os.makedirs(data_dir, exist_ok=True)
    
    # Tentar ler arquivo existente
    if os.path.exists(pc_id_file):
        try:
            with open(pc_id_file, 'r', encoding='utf-8') as f:
                pc_id = f.read().strip()
                if pc_id:
                    return pc_id
        except Exception:
            pass  # Se falhar, gerar novo
    
    # Prioridade 3: gerar novo UUID
    new_pc_id = str(uuid.uuid4())
    
    # Salvar no arquivo
    try:
        with open(pc_id_file, 'w', encoding='utf-8') as f:
            f.write(new_pc_id)
    except Exception:
        # Se não conseguir salvar, ainda retorna o UUID gerado
        pass
    
    return new_pc_id


def get_pc_name() -> str:
    """
    Retorna um nome legível para identificar esta instalação.
    Usado para exibição na interface.
    """
    try:
        return socket.gethostname()
    except Exception:
        return "PC Desconhecido"
