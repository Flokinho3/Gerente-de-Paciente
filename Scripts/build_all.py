
import os
import shutil
import subprocess
import json
import hashlib
import zipfile
from pathlib import Path

def remover_pasta(pasta):
    path = Path(pasta)
    if path.exists():
        try:
            shutil.rmtree(path)
            print(f"  [OK] Removida: {pasta}")
        except Exception as e:
            print(f"  [AVISO] Erro ao remover {pasta}: {e}")

def build_exe(spec_file, name):
    print(f"\n--- Iniciando Build de {name} ---")
    try:
        # Pega a raiz do projeto (um nível acima da pasta Scripts)
        root = Path(__file__).parent.parent
        subprocess.run(['pyinstaller', str(root / spec_file), '--clean', '--noconfirm'], 
                       cwd=str(root), check=True)
        print(f"  [SUCESSO] {name} criado em dist/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [ERRO] Falha ao buildar {name}: {e}")
        return False

def pack_release():
    print("\n--- Empacotando Release ---")
    root = Path(__file__).parent.parent
    dist = root / "dist"
    data = root / "data"
    version_file = data / "version.json"

    if not version_file.exists():
        print(f"  [ERRO] version.json não encontrado em {version_file}")
        return

    try:
        with open(version_file, 'r', encoding='utf-8') as f:
            version_info = json.load(f)
        
        version = version_info.get("version", "0.0.0")
        zip_name = f"GerenteApp_{version}.zip"
        zip_path = root / zip_name

        print(f"  Criando {zip_name}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Adicionar exes na raiz do ZIP
            if (dist / "Gerente.exe").exists():
                zf.write(dist / "Gerente.exe", "Gerente.exe")
                print(f"  [+] Gerente.exe")
            
            if (dist / "Launcher.exe").exists():
                zf.write(dist / "Launcher.exe", "Launcher.exe")
                print(f"  [+] Launcher.exe")
                
            # Adicionar estrutura de dados essencial
            if version_file.exists():
                zf.write(version_file, "data/version.json")
                print(f"  [+] data/version.json")

        # Gerar SHA256 para integridade
        h = hashlib.sha256()
        with open(zip_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        
        sha_path = root / "sha256.txt"
        sha_path.write_text(h.hexdigest(), encoding='utf-8')

        print(f"\n[FINALIZADO] Release pronto na raiz do projeto!")
        print(f"ZIP: {zip_path.name}")
        print(f"SHA256: {h.hexdigest()}")
    except Exception as e:
        print(f"  [ERRO] Falha no empacotamento: {e}")

if __name__ == "__main__":
    # Garante que estamos operando a partir da raiz do projeto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print("="*50)
    print("      BUILD SYSTEM - GERENTE DE PACIENTES")
    print("="*50)

    # Limpeza
    remover_pasta('build')
    remover_pasta('dist')

    # Compilação e Empacotamento
    # Assume que os arquivos .spec estão na raiz conforme solicitado anteriormente
    if build_exe('Gerente.spec', 'Gerente.exe') and build_exe('Launcher.spec', 'Launcher.exe'):
        pack_release()
        print("\nProcesso concluído com sucesso!")
    else:
        print("\nBuild interrompido por erros técnicos.")
