"""
Gestão de portas e processos: obter PID por porta, matar processo, liberar porta.
"""
import os
import re
import signal
import socket
import subprocess
import sys
import time

from inicio.utils.debug import _log_debug


def porta_acessivel(host="0.0.0.0", port=5000):
    """
    True se for possivel fazer bind em (host, port).
    Falha pode ser: porta em uso, firewall ou permissao.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except (OSError, OverflowError, ValueError):
        return False


def obter_pid_por_porta(porta):
    """
    Obtém o PID do processo que está usando a porta especificada.
    Retorna None se a porta não estiver em uso ou se não conseguir obter o PID.
    """
    _log_debug("inicio.rede.porta:obter_pid_por_porta", "Verificando porta", {"porta": porta}, "A")

    try:
        if sys.platform == 'win32':
            _log_debug("inicio.rede.porta:obter_pid_por_porta", "Windows detectado", {"platform": sys.platform}, "A")
            cmd = f'netstat -ano | findstr ":{porta}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            _log_debug("inicio.rede.porta:obter_pid_por_porta", "Resultado netstat", {"stdout": result.stdout, "returncode": result.returncode}, "A")

            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                pid_int = int(pid)
                                _log_debug("inicio.rede.porta:obter_pid_por_porta", "PID encontrado", {"pid": pid_int}, "A")
                                return pid_int
                            except ValueError:
                                continue
        else:
            _log_debug("inicio.rede.porta:obter_pid_por_porta", "Linux/Unix detectado", {"platform": sys.platform}, "A")
            try:
                cmd = f'lsof -ti:{porta}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    pid = int(result.stdout.strip().split()[0])
                    _log_debug("inicio.rede.porta:obter_pid_por_porta", "PID encontrado via lsof", {"pid": pid}, "A")
                    return pid
            except Exception:
                pass

            try:
                cmd = f'ss -lptn "sport = :{porta}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.split('\n'):
                        if f':{porta}' in line and 'pid=' in line:
                            match = re.search(r'pid=(\d+)', line)
                            if match:
                                pid = int(match.group(1))
                                _log_debug("inicio.rede.porta:obter_pid_por_porta", "PID encontrado via ss", {"pid": pid}, "A")
                                return pid
            except Exception:
                pass

        _log_debug("inicio.rede.porta:obter_pid_por_porta", "Nenhum PID encontrado", {}, "A")
        return None

    except Exception as e:
        _log_debug("inicio.rede.porta:obter_pid_por_porta", "Erro ao obter PID", {"erro": str(e)}, "A")
        return None


def matar_processo_por_pid(pid):
    """
    Mata um processo pelo seu PID.
    Retorna True se conseguiu matar o processo, False caso contrário.
    """
    _log_debug("inicio.rede.porta:matar_processo_por_pid", "Tentando matar processo", {"pid": pid}, "B")

    try:
        if sys.platform == 'win32':
            cmd = f'taskkill /PID {pid} /F'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            _log_debug("inicio.rede.porta:matar_processo_por_pid", "Resultado taskkill",
                       {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}, "B")

            if result.returncode == 0:
                _log_debug("inicio.rede.porta:matar_processo_por_pid", "Processo morto com sucesso", {"pid": pid}, "B")
                return True
            if 'não foi encontrado' in (result.stdout or '') or (result.stderr or '').lower().find('not found') >= 0:
                _log_debug("inicio.rede.porta:matar_processo_por_pid", "Processo já não existe", {"pid": pid}, "B")
                return True
            _log_debug("inicio.rede.porta:matar_processo_por_pid", "Falha ao matar processo", {"pid": pid, "erro": result.stderr}, "B")
            return False

        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _log_debug("inicio.rede.porta:matar_processo_por_pid", "Processo morto com sucesso (Unix)", {"pid": pid}, "B")
            return True
        except ProcessLookupError:
            _log_debug("inicio.rede.porta:matar_processo_por_pid", "Processo já não existe (Unix)", {"pid": pid}, "B")
            return True
        except PermissionError:
            _log_debug("inicio.rede.porta:matar_processo_por_pid", "Sem permissão para matar processo", {"pid": pid}, "B")
            return False

    except Exception as e:
        _log_debug("inicio.rede.porta:matar_processo_por_pid", "Erro ao matar processo", {"pid": pid, "erro": str(e)}, "B")
        return False


def verificar_e_liberar_porta(porta):
    """
    Verifica se a porta está em uso e, se estiver, mata o processo que a está usando.
    Retorna True se a porta está livre (ou foi liberada), False caso contrário.
    """
    _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Iniciando verificação de porta", {"porta": porta}, "C")
    pid_atual = os.getpid()
    _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "PID atual", {"pid_atual": pid_atual}, "C")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', porta))
        sock.close()

        if result == 0:
            _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Porta em uso detectada", {"porta": porta}, "C")
            pid_antigo = obter_pid_por_porta(porta)

            if pid_antigo:
                _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "PID do processo antigo",
                           {"pid_antigo": pid_antigo, "pid_atual": pid_atual}, "C")
                if pid_antigo == pid_atual:
                    _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "PID é o mesmo do processo atual, ignorando", {}, "C")
                    return True

                print(f"Processo antigo encontrado na porta {porta} (PID: {pid_antigo}). Encerrando...")
                sucesso = matar_processo_por_pid(pid_antigo)

                if sucesso:
                    print("Processo antigo encerrado com sucesso.")
                    time.sleep(1)
                    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        result2 = sock2.connect_ex(('127.0.0.1', porta))
                        sock2.close()
                        if result2 != 0:
                            _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Porta liberada com sucesso", {"porta": porta}, "C")
                            return True
                        _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Porta ainda em uso após matar processo", {"porta": porta}, "C")
                        print(f"AVISO: Porta {porta} ainda está em uso após tentar encerrar o processo.")
                        return False
                    except Exception:
                        _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Erro ao verificar porta após matar processo", {}, "C")
                        return False
                _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Falha ao matar processo antigo", {"pid_antigo": pid_antigo}, "C")
                print(f"ERRO: Não foi possível encerrar o processo antigo (PID: {pid_antigo}).")
                return False

            _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Não foi possível obter PID do processo usando a porta", {"porta": porta}, "C")
            print(f"AVISO: Porta {porta} está em uso, mas não foi possível identificar o processo.")
            return False

        _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Porta livre", {"porta": porta}, "C")
        return True

    except Exception as e:
        _log_debug("inicio.rede.porta:verificar_e_liberar_porta", "Erro ao verificar porta", {"porta": porta, "erro": str(e)}, "C")
        print(f"ERRO ao verificar porta {porta}: {e}")
        return False
