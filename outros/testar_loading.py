#!/usr/bin/env python3
"""
Script para testar o sistema de loading da página de gerenciamento de BD.
"""
import time
import webbrowser
import threading
from main import run_flask

def abrir_navegador():
    """Abre o navegador após alguns segundos"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000/bd')
    print("✅ Navegador aberto! Teste as seguintes operações:")
    print("1. 🔄 Atualizar - deve mostrar loading ao carregar pacientes")
    print("2. 💾 Criar Cópia BD - deve mostrar progresso ao criar backup")
    print("3. 📂 Carregar Cópia - deve mostrar progresso ao restaurar backup")
    print("4. ➕ Adicionar - deve mostrar loading ao salvar paciente")
    print("5. 🗑️ Excluir Dados BD - deve mostrar progresso ao limpar dados")

if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask com sistema de loading...")
    print("📱 Abra http://localhost:5000/bd no navegador para testar")

    # Inicia thread para abrir navegador
    threading.Thread(target=abrir_navegador, daemon=True).start()

    # Inicia servidor Flask
    try:
        run_flask(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n👋 Servidor parado.")