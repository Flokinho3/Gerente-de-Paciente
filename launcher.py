"""Launcher do Gerente de Pacientes.

Verifica releases via `outros/atualizador_github.py` e inicia o app principal.
O usuário vê apenas mensagens simples enquanto os detalhes técnicos ficam registrados em `updates/launcher.log`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Sequence
from zipfile import ZipFile

import sys

from outros.atualizador_github import run_updater

# Ao rodar como .exe (PyInstaller), ROOT é a pasta do executável.
_FROZEN = getattr(sys, "frozen", False)
ROOT = Path(sys.executable).resolve().parent if _FROZEN else Path(__file__).resolve().parent
GERENTE_SCRIPT = ROOT / "main.py"
GERENTE_EXE = ROOT / "Gerente.exe"
LOG_DIR = ROOT / "updates"
LAUNCHER_LOG = LOG_DIR / "launcher.log"
EXTRACT_DIR = LOG_DIR / "extracted"


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


def _desktop_directory() -> Path:
    """Retorna a pasta Desktop do usuário (Windows ou Linux)."""
    candidates = [
        Path(os.path.expanduser("~/Desktop")),
        Path(os.path.expanduser("~/Área de trabalho")),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return Path.home()


def _kill_existing_gerente() -> None:
    """Tenta encerrar o Gerente.exe caso ainda esteja em execução."""
    if sys.platform.startswith("win"):
        subprocess.run(
            ["taskkill", "/f", "/im", "Gerente.exe"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(
            ["pkill", "-f", "Gerente"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def _ensure_shortcut(target_exe: Path) -> None:
    """Cria um atalho simples na área de trabalho apontando para o Gerente.exe."""
    desktop = _desktop_directory()
    if sys.platform.startswith("win"):
        shortcut = desktop / "Gerente.url"
        content = (
            "[InternetShortcut]\n"
            f"URL=file:///{target_exe.as_posix()}\n"
            f"IconFile={target_exe.as_posix()}\n"
            "IconIndex=0\n"
        )
    else:
        shortcut = desktop / "Gerente.desktop"
        content = (
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Gerente de Pacientes\n"
            f"Exec={target_exe.as_posix()}\n"
            "Terminal=false\n"
        )
    try:
        shortcut.write_text(content, encoding="utf-8")
    except Exception as exc:
        _append_log([f"[{datetime.now().isoformat()}] Falha ao criar atalho: {exc}"])


def _prepare_desktop_copy(zip_path: Path) -> None:
    """Extrai o zip e copia o conteúdo para a pasta 'Gerente' na área de trabalho."""
    if not zip_path.exists():
        _append_log(
            [f"[{datetime.now().isoformat()}] Falha: zip não encontrado para copiar à área de trabalho."]
        )
        return

    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with ZipFile(zip_path, "r") as archive:
            archive.extractall(EXTRACT_DIR)
    except Exception as exc:
        _append_log([f"[{datetime.now().isoformat()}] Erro ao extrair zip: {exc}"])
        print("Não foi possível extrair o pacote de atualização.")
        return

    desktop = _desktop_directory()
    destination = desktop / "Gerente"
    destination.mkdir(parents=True, exist_ok=True)

    _kill_existing_gerente()
    exe_target = destination / "Gerente.exe"
    if exe_target.exists():
        try:
            exe_target.unlink()
        except PermissionError:
            _append_log(
                [f"[{datetime.now().isoformat()}] Erro ao remover Gerente.exe — feche o aplicativo e tente novamente."]
            )
            print("Gerente.exe ainda está em execução. Feche o aplicativo e tente novamente.")
            return

    for item in EXTRACT_DIR.iterdir():
        target_item = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target_item, dirs_exist_ok=True)
        else:
            if target_item.exists():
                try:
                    target_item.unlink()
                except Exception:
                    pass
            shutil.copy2(item, target_item)

    _ensure_shortcut(exe_target)
    _append_log([f"[{datetime.now().isoformat()}] Cópia de atualização criada em: {destination}"])
    print(f"Cópia de atualização pronta na área de trabalho: {destination}")


def _run_updater() -> bool:
    print("Verificando atualizações…")
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    returncode = 0

    # No .exe, passar caminhos relativos à pasta do launcher.
    updater_argv: list[str] | None = None
    if _FROZEN:
        updater_argv = [
            "--version-file", str(ROOT / "version.json"),
            "--download-dir", str(LOG_DIR),
        ]

    downloaded_path: Path | None = None
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            returncode, downloaded_path = run_updater(updater_argv)
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    except Exception:
        stderr_buffer.write(traceback.format_exc())
        returncode = 1

    stdout_value = stdout_buffer.getvalue()
    stderr_value = stderr_buffer.getvalue()
    _log_updater_result(returncode, stdout_value, stderr_value)

    if returncode != 0:
        print("Atualização falhou. Consulte updates/launcher.log para detalhes.")
        return False

    print("Atualização conferida.")
    if downloaded_path:
        _prepare_desktop_copy(downloaded_path)
    return True


def _start_gerente() -> int:
    print("Abrindo o Gerente…")
    if _FROZEN:
        if GERENTE_EXE.exists():
            command = [str(GERENTE_EXE)] + sys.argv[1:]
        else:
            print("Gerente.exe não encontrado nesta pasta. Coloque-o ao lado do Launcher.")
            return 1
    else:
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
