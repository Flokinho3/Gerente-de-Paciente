"""
Exibição de erros conforme o modo de execução (executável, console, etc.).
"""
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


def _raiz_projeto():
    """Retorna o diretório raiz do projeto."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def exibir_erro(titulo, mensagem, erro_detalhado=None):
    """
    Exibe erro de forma adequada baseado no modo de execução.
    Se for executável sem console, usa messagebox.
    Caso contrário, usa print.
    """
    is_executable = getattr(sys, 'frozen', False)
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    if is_executable and not debug_mode:
        try:
            root = tk.Tk()
            root.withdraw()
            mensagem_completa = mensagem
            if erro_detalhado:
                mensagem_completa += f"\n\nDetalhes:\n{str(erro_detalhado)}"
            messagebox.showerror(titulo, mensagem_completa)
            root.destroy()
        except Exception:
            try:
                base = os.path.dirname(sys.executable) if is_executable else _raiz_projeto()
                log_path = os.path.join(base, 'erro.log')
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n[{datetime.now()}] {titulo}: {mensagem}\n")
                    if erro_detalhado:
                        f.write(f"Detalhes: {str(erro_detalhado)}\n")
            except Exception:
                pass
    else:
        print(f"\n{'='*60}")
        print(f"ERRO: {titulo}")
        print(f"{'='*60}")
        print(mensagem)
        if erro_detalhado:
            print(f"\nDetalhes:")
            print(str(erro_detalhado))
            import traceback
            traceback.print_exc()
        print(f"{'='*60}\n")
