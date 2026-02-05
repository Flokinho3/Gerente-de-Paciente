"""
Script para empacotar o release após o build:
  1. Cria GerenteApp_{version}.zip com dist/Gerente.exe e dist_launcher/Launcher.exe
  2. Inclui data/version.json no zip
  3. Gera sha256.txt com o hash do zip

Uso: python pack_release.py
Requer que dist/ e dist_launcher/ existam.
"""
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent
    root = base.parent
    version_path = root / "data" / "version.json"
    dist_dir = root / "dist"
    dist_launcher_dir = base / "dist_launcher"

    if not version_path.exists():
        print(f"ERRO: version.json não encontrado em {version_path}.")
        return 1

    with open(version_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    version = info.get("version", "").strip()
    template = info.get("asset_template", "GerenteApp_{version}.zip")
    if not version:
        print("ERRO: Campo 'version' ausente ou vazio em version.json.")
        return 1
    
    zip_name = template.replace("{version}", version)
    zip_path = root / zip_name

    gerente_exe = dist_dir / "Gerente.exe"
    if not gerente_exe.exists():
        print(f"ERRO: {gerente_exe} não encontrado. Rode build_gerente.py antes.")
        return 1

    launcher_exe = dist_launcher_dir / "Launcher.exe"
    if not launcher_exe.exists():
        print(f"ERRO: {launcher_exe} não encontrado. Rode build_launcher.py antes.")
        return 1

    print("=" * 50)
    print("  Empacotando release")
    print("=" * 50)
    print(f"  Versão: {version}")
    print(f"  Destino: {zip_path.name}")
    print()

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Adicionar Gerente.exe na raiz do zip
            zf.write(gerente_exe, "Gerente.exe")
            print("  + Gerente.exe")
            
            # Adicionar Launcher.exe na raiz do zip
            zf.write(launcher_exe, "Launcher.exe")
            print("  + Launcher.exe")
            
            # Adicionar data/version.json
            zf.write(version_path, "data/version.json")
            print("  + data/version.json")

        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print()
        print(f"  ZIP criado: {zip_path}")
        print(f"  Tamanho: {size_mb:.2f} MB")
        print()

        # SHA256
        sha_path = root / "sha256.txt"
        h = hashlib.sha256()
        with open(zip_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        digest = h.hexdigest()
        sha_path.write_text(digest + "\n", encoding="utf-8")
        print(f"  SHA256 gravado em sha256.txt: {digest}")
        print()
        print("=" * 50)
        print("  SUCESSO!")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"ERRO ao criar arquivos: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
