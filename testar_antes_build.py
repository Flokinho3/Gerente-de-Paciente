#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar se todas as dependências estão corretas antes de criar o .exe
"""

import sys
import importlib

def testar_modulo(nome_modulo, nome_exibicao=None):
    """Testa se um módulo pode ser importado"""
    if nome_exibicao is None:
        nome_exibicao = nome_modulo
    
    try:
        importlib.import_module(nome_modulo)
        print(f"[OK] {nome_exibicao:<30} Instalado")
        return True
    except ImportError as e:
        print(f"[X]  {nome_exibicao:<30} FALTANDO")
        print(f"     Erro: {e}")
        return False

def main():
    print("=" * 60)
    print(" TESTE DE DEPENDÊNCIAS - Gerente de Pacientes")
    print("=" * 60)
    print()
    
    modulos = [
        ("flask", "Flask"),
        ("openpyxl", "OpenPyXL (Excel)"),
        ("docx", "python-docx (Word)"),
        ("PyInstaller", "PyInstaller"),
        ("tkinter", "Tkinter (GUI)"),
        ("webbrowser", "WebBrowser"),
        ("sqlite3", "SQLite3"),
        ("jinja2", "Jinja2"),
        ("werkzeug", "Werkzeug"),
        ("markupsafe", "MarkupSafe"),
    ]
    
    resultados = []
    for modulo, nome in modulos:
        resultado = testar_modulo(modulo, nome)
        resultados.append(resultado)
    
    print()
    print("=" * 60)
    
    if all(resultados):
        print("[OK] TODAS AS DEPENDENCIAS ESTAO INSTALADAS!")
        print("     Voce pode criar o .exe com seguranca.")
        print()
        print("     Execute: build_exe.bat")
        print("=" * 60)
        return 0
    else:
        print("[X] ALGUMAS DEPENDENCIAS ESTAO FALTANDO!")
        print("    Instale as dependencias primeiro:")
        print()
        print("    pip install -r requirements.txt")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
