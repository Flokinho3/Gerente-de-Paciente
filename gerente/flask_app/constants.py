"""Constantes da aplicação."""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict


def _load_version_info() -> Dict[str, str]:
    """Carrega a versão oficial descrita em `version.json`."""
    root = Path(__file__).resolve().parents[1]
    version_path = root / "version.json"
    fallback: Dict[str, str] = {
        "version": "0.0.0",
        "build_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if not version_path.exists():
        return fallback

    try:
        payload = json.loads(version_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return fallback

    # Apenas strings são válidas para estas chaves
    for key in ("version", "build_date"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            fallback[key] = value.strip()

    return fallback


_VERSION_INFO = _load_version_info()

VERSION = _VERSION_INFO["version"]
BUILD_DATE = _VERSION_INFO["build_date"]
