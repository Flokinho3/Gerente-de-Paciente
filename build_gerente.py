"""
Script para criar o executável Gerente.exe
Usa PyInstaller para gerar o arquivo .exe
"""
import os
import subprocess
import sys
import shutil

def main():
    print("=" * 50)
    print("  Criando executável Gerente.exe")
    print("=" * 50)
    print()
    
    # Limpar builds anteriores
    print("Limpando builds anteriores...")
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("  ✓ Pasta 'build' removida")
    
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("  ✓ Pasta 'dist' removida")
    
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
