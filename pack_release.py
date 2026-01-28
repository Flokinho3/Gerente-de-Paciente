"""
Script para empacotar o release após o build:
  1. Cria GerenteApp_{version}.zip com dist/ e data/ (conforme version.json)
  2. Gera sha256.txt com o hash do zip

Uso: python pack_release.py
Requer que dist/ exista (rode build_gerente.py antes).
"""
import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent
    version_path = base / "version.json"
    dist_dir = base / "dist"
    data_dir = base / "data"

    if not version_path.exists():
        print("ERRO: version.json não encontrado.")
        return 1

    with open(version_path, "r", encoding="utf-8") as f:
        info = json.load(f)
    version = info.get("version", "").strip()
    template = info.get("asset_template", "GerenteApp_{version}.zip")
    if not version:
        print("ERRO: Campo 'version' ausente ou vazio em version.json.")
        return 1
    zip_name = template.replace("{version}", version)
    zip_path = base / zip_name

    if not dist_dir.is_dir():
        print("ERRO: Pasta 'dist' não encontrada. Rode build_gerente.py antes.")
        return 1

    # Pastas/arquivos a incluir no zip
    to_include = [dist_dir]
    if data_dir.is_dir():
        to_include.append(data_dir)
    else:
        print("  [AVISO] Pasta 'data' não existe; apenas dist/ será incluída.")

    print("=" * 50)
    print("  Empacotando release")
    print("=" * 50)
    print(f"  Versão: {version}")
    print(f"  Destino: {zip_path.name}")
    print()

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for folder in to_include:
                for root, _dirs, files in os.walk(folder):
                    for f in files:
                        full = Path(root) / f
                        arc = full.relative_to(base)
                        zf.write(full, arc)
                        print(f"  + {arc}")

        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print()
        print(f"  ZIP criado: {zip_path}")
        print(f"  Tamanho: {size_mb:.2f} MB")
        print()

        # SHA256
        sha_path = base / "sha256.txt"
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
    except OSError as e:
        print(f"ERRO ao criar arquivos: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
