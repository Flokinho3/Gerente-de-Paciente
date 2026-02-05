"""
Firewall do Windows: Funcionalidade desativada.
Este módulo agora apenas mantém as assinaturas das funções para evitar erros de importação,
mas não realiza nenhuma operação que exija privilégios administrativos.
"""
import sys

def _is_admin():
    return False

def ensure_firewall_rule():
    """Garante que a regra de firewall por executavel existe (DESATIVADO)."""
    pass

def _executar_apenas_firewall_e_reabrir():
    """Usado quando o .exe foi iniciado com --elevated-firewall (DESATIVADO)."""
    pass

def relaunch_as_admin():
    """Reexecuta o mesmo .exe como administrador (DESATIVADO)."""
    pass
