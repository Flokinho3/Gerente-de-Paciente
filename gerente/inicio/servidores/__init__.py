"""Modos de inicialização do servidor Flask."""
from .modos import (
    criar_janela_tkinter_executavel,
    iniciar_com_tray_icon,
    iniciar_modo_desenvolvimento,
    iniciar_modo_executavel_sem_tray,
    iniciar_modo_silencioso,
    iniciar_servidor_em_porta,
    iniciar_servidores_duplos,
    verificar_servidor,
)

__all__ = [
    'criar_janela_tkinter_executavel',
    'iniciar_com_tray_icon',
    'iniciar_modo_desenvolvimento',
    'iniciar_modo_executavel_sem_tray',
    'iniciar_modo_silencioso',
    'iniciar_servidor_em_porta',
    'iniciar_servidores_duplos',
    'verificar_servidor',
]
