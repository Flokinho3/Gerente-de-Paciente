"""Launcher do Gerente de Pacientes.

Verifica releases no GitHub via `outros/atualizador_github.py` e inicia o app principal.
O usuário vê apenas mensagens simples enquanto os detalhes técnicos ficam registrados em `updates/launcher.log`.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent
UPDATER_SCRIPT = ROOT / "outros" / "atualizador_github.py"
GERENTE_SCRIPT = ROOT / "main.py"
LOG_DIR = ROOT / "updates"
LAUNCHER_LOG = LOG_DIR / "launcher.log"


def _append_log(lines: Sequence[str]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with LAUNCHER_LOG.open("a", encoding="utf-8") as handle:
        for line in lines:
            handle.write(f"{line.rstrip()}\n")


def _log_updater_result(returncode: int, stdout: str, stderr: str) -> None:
    timestamp = datetime.now().isoformat()
    entries: list[str] = [f"[{timestamp}] Atualização exitcode={returncode}"]
    if stdout:
        entries.append(f"[{timestamp}] STDOUT:")
        entries.extend(stdout.rstrip().splitlines())
    if stderr:
        entries.append(f"[{timestamp}] STDERR:")
        entries.extend(stderr.rstrip().splitlines())
    _append_log(entries)


def _run_updater() -> bool:
    print("Verificando atualizações…")
    command = [sys.executable, str(UPDATER_SCRIPT)]
    try:
        process = subprocess.run(command, capture_output=True, text=True)
    except OSError:
        print("Não foi possível executar o verificador de atualizações.")
        _append_log([f"[{datetime.now().isoformat()}] Falha ao chamar o updater."])
        return False

    _log_updater_result(process.returncode, process.stdout, process.stderr)

    if process.returncode != 0:
        print("Atualização falhou. Consulte updates/launcher.log para detalhes.")
        return False

    print("Atualização conferida.")
    return True


def _start_gerente() -> int:
    print("Abrindo o Gerente…")
    command = [sys.executable, str(GERENTE_SCRIPT)] + sys.argv[1:]
    try:
        return subprocess.run(command).returncode
    except KeyboardInterrupt:
        return 130  # Ctrl+C


def main() -> int:
    _run_updater()
    return _start_gerente()


if __name__ == "__main__":
    raise SystemExit(main())
