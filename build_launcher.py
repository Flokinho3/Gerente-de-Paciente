"""
Script para criar o executável Launcher.exe.
Usa PyInstaller para gerar o launcher do Gerente de Pacientes.
"""
import os
import shutil
import subprocess
import sys
import time


def remover_pasta(pasta: str) -> bool:
    if not os.path.exists(pasta):
        return True
    for tentativa in range(3):
        try:
            shutil.rmtree(pasta)
            print(f"  OK Pasta '{pasta}' removida")
            return True
        except PermissionError as e:
            if tentativa < 2:
                print(f"  [AVISO] Arquivo em uso ao remover '{pasta}'. Tentando novamente...")
                time.sleep(1)
            else:
                print(f"ERRO: Não foi possível remover '{pasta}'.")
                print(f"Arquivo em uso: {e}")
                print("Feche o executável que está usando a pasta e tente novamente.")
                return False
    return False


def main() -> int:
    base = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base)

    print("=" * 50)
    print("  Criando executável Launcher.exe")
    print("=" * 50)
    print()

    print("Limpando builds anteriores...")
    if not remover_pasta("build"):
        return 1
    if not remover_pasta("dist"):
        return 1
    print()

    print("Executando PyInstaller...")
    try:
        result = subprocess.run(
            ["pyinstaller", "build_launcher.spec", "--clean", "--noconfirm"],
            check=True,
            capture_output=False,
            cwd=base,
        )
        exe_path = os.path.join(base, "dist", "Launcher.exe")
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print()
            print("=" * 50)
            print("  SUCESSO!")
            print("=" * 50)
            print()
            print(f"Executável criado em: {os.path.abspath(exe_path)}")
            print(f"Tamanho: {size:.2f} MB")
            print()
            print("Coloque Launcher.exe na mesma pasta que Gerente.exe e version.json.")
            return 0
        print()
        print("ERRO: Executável não foi criado. Verifique os erros acima.")
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


if __name__ == "__main__":
    sys.exit(main())
