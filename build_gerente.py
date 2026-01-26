"""
Script para criar o executável Gerente.exe
Usa PyInstaller para gerar o arquivo .exe
Ajusta console baseado no FLASK_DEBUG do .env (false = sem terminal na versão compilada)
"""
import os
import re
import shutil
import subprocess
import sys
import time

def ajustar_spec_console():
    """Ajusta o console no .spec baseado no FLASK_DEBUG do .env.
    Versão compilada (FLASK_DEBUG=false): SEM terminal. Só com debug=true: com terminal."""
    from env_loader import load_env
    load_env()
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    base = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(base, 'build_gerente.spec')
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec_content = f.read()
    
    # Forçar console=True ou False (regex: não depende do valor atual no .spec)
    novo = 'console=True,' if debug_mode else 'console=False,'
    spec_content = re.sub(r'console\s*=\s*(?:True|False)\s*,', novo, spec_content)
    
    if debug_mode:
        print(f"  [OK] Console HABILITADO (FLASK_DEBUG=true)")
    else:
        print(f"  [OK] Console DESABILITADO -- versao compilada SEM terminal (FLASK_DEBUG=false)")
    
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    return debug_mode

def remover_pasta(pasta):
    if not os.path.exists(pasta):
        return True
    for tentativa in range(3):
        try:
            shutil.rmtree(pasta)
            print(f"  ✓ Pasta '{pasta}' removida")
            return True
        except PermissionError as e:
            if tentativa < 2:
                print(f"  [AVISO] Arquivo em uso ao remover '{pasta}'. Tentando novamente...")
                time.sleep(1)
            else:
                print(f"ERRO: Não foi possível remover '{pasta}'.")
                print(f"Arquivo em uso: {e}")
                print("Feche o executável/servidor que está usando a pasta e tente novamente.")
                return False
    return False


def main():
    print("=" * 50)
    print("  Criando executável Gerente.exe")
    print("=" * 50)
    print()
    
    # Ajustar console no .spec baseado no .env
    print("Ajustando configuração do console...")
    debug_mode = ajustar_spec_console()
    print()
    
    # Limpar builds anteriores
    print("Limpando builds anteriores...")
    if not remover_pasta('build'):
        return 1
    
    if not remover_pasta('dist'):
        return 1
    
    print()
    print("Executando PyInstaller...")
    
    try:
        # Executar PyInstaller
        result = subprocess.run(
            ['pyinstaller', 'build_gerente.spec', '--clean', '--noconfirm'],
            check=True,
            capture_output=False
        )
        
        # Verificar se o executável foi criado
        exe_path = os.path.join('dist', 'Gerente.exe')
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # Tamanho em MB
            print()
            print("=" * 50)
            print("  SUCESSO!")
            print("=" * 50)
            print()
            print(f"Executável criado em: {os.path.abspath(exe_path)}")
            print(f"Tamanho: {size:.2f} MB")
            print()
            return 0
        else:
            print()
            print("ERRO: Executável não foi criado!")
            print("Verifique os erros acima.")
            return 1
            
    except subprocess.CalledProcessError as e:
        print()
        print(f"ERRO ao executar PyInstaller: {e}")
        return 1
    except FileNotFoundError:
        print()
        print("ERRO: PyInstaller não encontrado!")
        print("Instale com: pip install pyinstaller")
        return 1

if __name__ == '__main__':
    sys.exit(main())
