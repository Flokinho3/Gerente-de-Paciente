"""
Carrega o .env do diretório correto em qualquer modo:
- .exe (frozen): pasta do executável
- Python (main.py): raiz do projeto (pasta deste arquivo)
"""
import os
import sys


def get_base_dir():
    """
    Raiz de configuração: pasta do .exe ou do projeto.
    O .env deve ficar nessa pasta.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_env_path():
    """Caminho do arquivo .env."""
    return os.path.join(get_base_dir(), ".env")


def load_env():
    """
    Carrega o .env. Não sobrescreve variáveis já definidas em os.environ.
    Retorna True se o arquivo existia e foi carregado.
    """
    from dotenv import load_dotenv
    path = get_env_path()
    return load_dotenv(path) or False
