"""Cliente leve para baixar releases públicos do GitHub de forma segura."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

import requests
from packaging.version import InvalidVersion, Version

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_VERSION_FILE = _ROOT / "version.json"
_DEFAULT_DOWNLOAD_DIR = _ROOT / "updates"
_DEFAULT_REPO = os.getenv("GERENTE_GITHUB_REPO", "Flokinho3/Gerente-de-Paciente")


def _build_headers(token: Optional[str]) -> Dict[str, str]:
    headers = {"User-Agent": "GerentePacienteUpdater/1.0"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _load_local_metadata(path: Path) -> Dict[str, str]:
    if not path.exists():
        raise SystemExit(f"Arquivo de versão ausente ({path}). Atualize-o antes de liberar.")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path.name} está corrompido: {exc}") from exc

    version = payload.get("version")
    if not isinstance(version, str) or not version.strip():
        raise SystemExit(f"Campo 'version' inválido em {path.name}.")

    metadata = {"version": version.strip()}
    template = payload.get("asset_template")
    if isinstance(template, str) and template.strip():
        metadata["asset_template"] = template.strip()

    return metadata


def _parse_version(value: str, label: str) -> Version:
    candidate = value.lstrip("vV").strip()
    try:
        return Version(candidate)
    except InvalidVersion as exc:
        raise SystemExit(f"{label} inválida ('{value}'): {exc}") from exc


def _fetch_latest_release(repo: str, token: Optional[str]) -> Dict:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    response = requests.get(url, headers=_build_headers(token), timeout=30)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        if response.status_code == 403:
            raise SystemExit(
                "Limite da API do GitHub atingido. Espere alguns instantes e tente novamente."
            ) from exc
        raise SystemExit(f"Erro ao consultar release ({response.status_code}): {exc}") from exc

    return response.json()


def _is_candidate_zip(asset: Dict) -> bool:
    if not asset.get("name", "").lower().endswith(".zip"):
        return False
    size = asset.get("size")
    return isinstance(size, int) and size >= 1_048_576


def _select_asset(assets: List[Dict], desired_name: str) -> Optional[Dict]:
    for asset in assets:
        if asset.get("name") == desired_name:
            return asset

    for asset in assets:
        if _is_candidate_zip(asset):
            return asset

    return None


def _download_asset(asset: Dict, destination: Path, token: Optional[str]) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    target_path = destination / asset["name"]
    url = asset["browser_download_url"]

    with requests.get(url, headers=_build_headers(token), stream=True, timeout=60) as response:
        response.raise_for_status()
        with target_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    handle.write(chunk)

    return target_path


def _compute_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_expected_hash(assets: List[Dict], asset_name: str, token: Optional[str]) -> Optional[str]:
    hash_assets = [
        a for a in assets if "sha256" in a.get("name", "").lower()
    ]
    if not hash_assets:
        return None

    pattern = re.compile(asset_name.replace(".", r"\."))

    for hash_asset in hash_assets:
        text = requests.get(
            hash_asset["browser_download_url"], headers=_build_headers(token), timeout=30
        ).text
        for line in text.splitlines():
            entry = line.strip()
            if not entry:
                continue

            candidate = entry.split(maxsplit=1)[0]
            if re.fullmatch(r"[a-fA-F0-9]{64}", candidate):
                if pattern.search(entry) or len(hash_assets) == 1:
                    return candidate.lower()

        stripped = text.strip()
        if re.fullmatch(r"[a-fA-F0-9]{64}", stripped):
            return stripped.lower()

    return None


def _derive_asset_name(metadata: Dict[str, str], version: Version) -> str:
    template = metadata.get("asset_template", "GerenteApp_{version}.zip")
    try:
        return template.format(version=version.public)
    except Exception:
        return f"GerenteApp_{version.public}.zip"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verifica e baixa releases públicas do GitHub.")
    parser.add_argument(
        "--repo",
        default=_DEFAULT_REPO,
        help="Repositório no formato owner/repo (padrão: %(default)s)",
    )
    parser.add_argument(
        "--version-file",
        type=Path,
        default=_DEFAULT_VERSION_FILE,
        help="Arquivo que contém a versão local (padrão: %(default)s)",
    )
    parser.add_argument(
        "--asset-name",
        help="Nome exato do asset zip no release. Se omitido, usa o template de version.json.",
    )
    parser.add_argument(
        "--download-dir",
        type=Path,
        default=_DEFAULT_DOWNLOAD_DIR,
        help="Diretório onde o zip será salvo (padrão: %(default)s)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN"),
        help="Token GitHub para contornar limites de API (opcional).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Mostra a versão remota e encerra sem baixar nada.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Força o download independente da comparação de versões.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    metadata = _load_local_metadata(args.version_file)
    local_version = _parse_version(metadata["version"], "Versão local")
    release = _fetch_latest_release(args.repo, args.token)
    remote_version = _parse_version(release.get("tag_name", ""), "Tag do release")

    print(f"Versão local: {local_version}")
    print(f"Versão remota: {remote_version} ({release.get('name') or release.get('tag_name')})")

    if args.check_only:
        return 0

    needs_update = remote_version > local_version
    if not needs_update and not args.force:
        print("Nenhuma atualização disponível.")
        return 0

    asset_name = args.asset_name or _derive_asset_name(metadata, remote_version)
    asset = _select_asset(release.get("assets", []), asset_name)
    if not asset:
        raise SystemExit(
            "Não foi possível localizar o zip do release. "
            "Verifique o nome do asset ou os arquivos publicados."
        )

    target_path = _download_asset(asset, args.download_dir, args.token)
    expected_hash = _extract_expected_hash(release.get("assets", []), asset["name"], args.token)

    if expected_hash:
        actual_hash = _compute_sha256(target_path)
        if actual_hash != expected_hash:
            raise SystemExit(
                "O hash SHA256 do arquivo baixado não confere com o esperado. "
                "Não substitua nada até investigar."
            )
        print("Hash SHA256 validado com sucesso.")
    else:
        print("Hash SHA256 não fornecido no release; verifique manualmente.")
        print("Atualização baixada, mas não verificada.")

    print(f"Novo release baixado em: {target_path}")
    print(
        "Extraia o zip em uma pasta temporária, valide os arquivos e substitua a instalação "
        "após parar o sistema em produção."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
