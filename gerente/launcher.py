"""Launcher do Gerente de Pacientes.

Verifica releases via `outros/atualizador_github.py` e inicia o app principal.
O usuário vê apenas mensagens simples enquanto os detalhes técnicos ficam registrados em `updates/launcher.log`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path
from zipfile import ZipFile
from typing import Sequence

import sys

from outros.atualizador_github import run_updater
from gerente.config import get_version_file_path, get_updates_dir

# Ao rodar como .exe (PyInstaller), ROOT é a pasta do executável.
_FROZEN = getattr(sys, "frozen", False)
ROOT = Path(sys.executable).resolve().parent if _FROZEN else Path(__file__).resolve().parent
GERENTE_SCRIPT = ROOT / "main.py"
GERENTE_EXE = ROOT / "Gerente.exe"

# Centralizar caminhos de log e updates na pasta data/
LOG_DIR = Path(get_updates_dir())
LAUNCHER_LOG = LOG_DIR / "launcher.log"
EXTRACT_DIR = LOG_DIR / "extracted"
VERSION_FILE = Path(get_version_file_path())


def _append_log(lines: Sequence[str]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with LAUNCHER_LOG.open("a", encoding="utf-8") as handle:
            for line in lines:
                handle.write(f"{line.rstrip()}\n")
    except Exception:
        pass


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


def _resolve_update_destination() -> Path:
    """Define o destino da atualizacao evitando loop de subpastas."""
    if _FROZEN and ROOT.name.lower() == "gerente":
        return ROOT
    desktop = _desktop_directory()
    return desktop / "Gerente"


def _select_extract_root() -> Path:
    """Seleciona a raiz real do pacote extraido para evitar subpastas."""
    entries = [item for item in EXTRACT_DIR.iterdir()]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    for name in ("Gerente", "dist"):
        candidate = EXTRACT_DIR / name
        if candidate.exists() and candidate.is_dir():
            return candidate
    return EXTRACT_DIR


def _log_expected_layout(destination: Path) -> None:
    missing: list[str] = []
    if not (destination / "Gerente.exe").exists():
        missing.append("Gerente.exe")
    if not (destination / "Launcher.exe").exists():
        missing.append("Launcher.exe")
    if not (destination / "data").exists():
        missing.append("data/")
    if not (destination / ".env_Exemplo").exists():
        missing.append(".env_Exemplo")
    if not ((destination / "versao.json").exists() or (destination / "version.json").exists()):
        missing.append("versao.json|version.json")
    if missing:
        _append_log([f"[{datetime.now().isoformat()}] Layout incompleto no destino: {', '.join(missing)}"])


def _prepare_desktop_copy(zip_path: Path) -> None:
    """Extrai o zip e copia o conteúdo para a pasta 'Gerente'."""
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
        return

    destination = _resolve_update_destination()
    destination.mkdir(parents=True, exist_ok=True)

    source_root = _select_extract_root()
    if source_root != EXTRACT_DIR:
        _append_log([f"[{datetime.now().isoformat()}] Usando raiz extraida: {source_root}"])

    _kill_existing_gerente()
    exe_target = destination / "Gerente.exe"
    if exe_target.exists():
        try:
            exe_target.unlink()
        except PermissionError:
            _append_log(
                [f"[{datetime.now().isoformat()}] Erro ao remover Gerente.exe — feche o aplicativo e tente novamente."]
            )
            return

    for item in source_root.iterdir():
        target_item = destination / item.name
        
        # Preservar pasta data/ (banco de dados do cliente) - não sobrescrever
        if item.is_dir() and item.name == "data" and target_item.exists():
            _append_log([f"[{datetime.now().isoformat()}] Preservando pasta data/ existente (BD do cliente)"])
            continue
        
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
    _log_expected_layout(destination)
    _append_log([f"[{datetime.now().isoformat()}] Cópia de atualização criada em: {destination}"])

    # Limpar resíduos da atualização
    try:
        if zip_path.exists():
            zip_path.unlink()
            _append_log([f"[{datetime.now().isoformat()}] Arquivo ZIP de atualização removido: {zip_path.name}"])
        
        if EXTRACT_DIR.exists():
            shutil.rmtree(EXTRACT_DIR)
            _append_log([f"[{datetime.now().isoformat()}] Pasta de extração removida: {EXTRACT_DIR}"])
    except Exception as exc:
        _append_log([f"[{datetime.now().isoformat()}] Falha ao limpar resíduos da atualização: {exc}"])


def _ensure_version_file() -> None:
    """Se estiver congelado e version.json não existir, cria um mínimo para permitir o primeiro download."""
    if not _FROZEN:
        return
    vf = VERSION_FILE
    if vf.exists():
        return
    try:
        # Garantir pasta data/
        vf.parent.mkdir(parents=True, exist_ok=True)
        vf.write_text(
            '{"version": "0.0.0", "asset_template": "GerenteApp_{version}.zip"}',
            encoding="utf-8",
        )
        _append_log([f"[{datetime.now().isoformat()}] version.json criado em {vf} (0.0.0 para primeiro download)"])
    except OSError as exc:
        _append_log([f"[{datetime.now().isoformat()}] Falha ao criar version.json: {exc}"])


def _run_updater() -> bool:
    stdout_buffer = StringIO()
    stderr_buffer = StringIO()
    returncode = 0

    # No .exe, passar caminhos relativos à pasta do launcher.
    # Se Gerente.exe não existe, forçar download para “instalar” na primeira execução.
    updater_argv: list[str] | None = None
    if _FROZEN:
        _ensure_version_file()
        updater_argv = [
            "--version-file", str(VERSION_FILE),
            "--download-dir", str(LOG_DIR),
        ]
        if not GERENTE_EXE.exists():
            updater_argv.append("--force")

    downloaded_path: Path | None = None
    try:
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            returncode, downloaded_path = run_updater(updater_argv)
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
        if exc.args:
            stderr_buffer.write(str(exc.args[0]))
    except Exception:
        stderr_buffer.write(traceback.format_exc())
        returncode = 1

    stdout_value = stdout_buffer.getvalue()
    stderr_value = stderr_buffer.getvalue()
    _log_updater_result(returncode, stdout_value, stderr_value)

    if returncode != 0:
        return False

    if downloaded_path:
        _prepare_desktop_copy(downloaded_path)
    return True


def _gerente_exe_path() -> Path | None:
    """Retorna o caminho do Gerente.exe (ao lado do Launcher ou em Desktop/Gerente)."""
    if GERENTE_EXE.exists():
        return GERENTE_EXE
    if _FROZEN:
        desktop_folder = _desktop_directory() / "Gerente"
        candidates = [
            desktop_folder / "Gerente.exe",
            desktop_folder / "dist" / "Gerente.exe",  # layout antigo do zip
        ]
        for path in candidates:
            if path.exists():
                return path
    return None


def _start_gerente() -> int:
    if _FROZEN:
        exe_path = _gerente_exe_path()
        if exe_path is not None:
            command = [str(exe_path)] + sys.argv[1:]
        else:
            return 1
    else:
        command = [sys.executable, str(GERENTE_SCRIPT)] + sys.argv[1:]
    
    try:
        # Iniciar o Gerente em background (não bloquear)
        process = subprocess.Popen(command)
        
        # Aguardar alguns segundos para garantir que o Gerente iniciou
        # e então encerrar o launcher automaticamente
        wait_seconds = 3
        time.sleep(wait_seconds)
        
        # Verificar se o processo ainda está rodando (Gerente iniciou com sucesso)
        if process.poll() is None:
            return 0
        else:
            # Gerente encerrou rapidamente (possível erro)
            returncode = process.returncode
            _append_log([f"[{datetime.now().isoformat()}] Gerente encerrou rapidamente com exitcode={returncode}"])
            return returncode if returncode else 1
    except KeyboardInterrupt:
        return 130  # Ctrl+C
    except Exception as exc:
        _append_log([f"[{datetime.now().isoformat()}] Erro ao iniciar Gerente: {exc}"])
        return 1


def main() -> int:
    _run_updater()
    return _start_gerente()


if __name__ == "__main__":
    raise SystemExit(main())
