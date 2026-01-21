"""
Sistema de Gestão de Pacientes - Inicialização
Gerencia a inicialização do sistema (tray icon, modo executável, etc.)
"""
import threading
import webbrowser
import os
import signal
import atexit
import sys
import subprocess
import socket
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Importar Flask app e funções relacionadas
from flask_app import app, VERSION, BUILD_DATE, run_flask, cleanup_flask

# #region agent log
def _log_debug(location, message, data=None, hypothesis_id=None):
    """Log de debug para análise"""
    try:
        import json
        # Usar caminho do .env ou padrão
        log_path = os.getenv('DEBUG_LOG_PATH', os.path.join(os.path.dirname(__file__), '.cursor', 'debug.log'))
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id or "A",
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception:
        pass
# #endregion agent log

def obter_pid_por_porta(porta):
    """
    Obtém o PID do processo que está usando a porta especificada.
    Retorna None se a porta não estiver em uso ou se não conseguir obter o PID.
    """
    # #region agent log
    _log_debug("main.py:obter_pid_por_porta", "Verificando porta", {"porta": porta}, "A")
    # #endregion agent log
    
    try:
        if sys.platform == 'win32':
            # Windows: usar netstat -ano para encontrar processos usando a porta
            # #region agent log
            _log_debug("main.py:obter_pid_por_porta", "Windows detectado", {"platform": sys.platform}, "A")
            # #endregion agent log
            
            cmd = f'netstat -ano | findstr ":{porta}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            # #region agent log
            _log_debug("main.py:obter_pid_por_porta", "Resultado netstat", {"stdout": result.stdout, "returncode": result.returncode}, "A")
            # #endregion agent log
            
            if result.returncode == 0 and result.stdout:
                # Parse da saída do netstat
                # Formato: TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    12345
                for line in result.stdout.strip().split('\n'):
                    if 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                pid_int = int(pid)
                                # #region agent log
                                _log_debug("main.py:obter_pid_por_porta", "PID encontrado", {"pid": pid_int}, "A")
                                # #endregion agent log
                                return pid_int
                            except ValueError:
                                continue
        else:
            # Linux/Unix: usar lsof ou ss para encontrar processos usando a porta
            # #region agent log
            _log_debug("main.py:obter_pid_por_porta", "Linux/Unix detectado", {"platform": sys.platform}, "A")
            # #endregion agent log
            
            # Tentar lsof primeiro
            try:
                cmd = f'lsof -ti:{porta}'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    pid = int(result.stdout.strip().split()[0])
                    # #region agent log
                    _log_debug("main.py:obter_pid_por_porta", "PID encontrado via lsof", {"pid": pid}, "A")
                    # #endregion agent log
                    return pid
            except:
                pass
            
            # Fallback: usar ss
            try:
                cmd = f'ss -lptn "sport = :{porta}"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout:
                    # Parse da saída do ss
                    for line in result.stdout.split('\n'):
                        if f':{porta}' in line and 'pid=' in line:
                            # Extrair PID da linha
                            import re
                            match = re.search(r'pid=(\d+)', line)
                            if match:
                                pid = int(match.group(1))
                                # #region agent log
                                _log_debug("main.py:obter_pid_por_porta", "PID encontrado via ss", {"pid": pid}, "A")
                                # #endregion agent log
                                return pid
            except:
                pass
        
        # #region agent log
        _log_debug("main.py:obter_pid_por_porta", "Nenhum PID encontrado", {}, "A")
        # #endregion agent log
        return None
        
    except Exception as e:
        # #region agent log
        _log_debug("main.py:obter_pid_por_porta", "Erro ao obter PID", {"erro": str(e)}, "A")
        # #endregion agent log
        return None

def matar_processo_por_pid(pid):
    """
    Mata um processo pelo seu PID.
    Retorna True se conseguiu matar o processo, False caso contrário.
    """
    # #region agent log
    _log_debug("main.py:matar_processo_por_pid", "Tentando matar processo", {"pid": pid}, "B")
    # #endregion agent log
    
    try:
        if sys.platform == 'win32':
            # Windows: usar taskkill
            cmd = f'taskkill /PID {pid} /F'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            # #region agent log
            _log_debug("main.py:matar_processo_por_pid", "Resultado taskkill", {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}, "B")
            # #endregion agent log
            
            if result.returncode == 0:
                # #region agent log
                _log_debug("main.py:matar_processo_por_pid", "Processo morto com sucesso", {"pid": pid}, "B")
                # #endregion agent log
                return True
            else:
                # Verificar se o processo já não existe
                if 'não foi encontrado' in result.stdout or 'not found' in result.stderr.lower():
                    # #region agent log
                    _log_debug("main.py:matar_processo_por_pid", "Processo já não existe", {"pid": pid}, "B")
                    # #endregion agent log
                    return True  # Considera sucesso se já não existe
                # #region agent log
                _log_debug("main.py:matar_processo_por_pid", "Falha ao matar processo", {"pid": pid, "erro": result.stderr}, "B")
                # #endregion agent log
                return False
        else:
            # Linux/Unix: usar kill
            try:
                os.kill(pid, signal.SIGTERM)
                # Aguardar um pouco para verificar se o processo foi morto
                import time
                time.sleep(0.5)
                # Tentar SIGKILL se ainda estiver vivo
                try:
                    os.kill(pid, 0)  # Verifica se processo ainda existe
                    os.kill(pid, signal.SIGKILL)  # Força encerramento
                except ProcessLookupError:
                    pass  # Processo já foi morto
                
                # #region agent log
                _log_debug("main.py:matar_processo_por_pid", "Processo morto com sucesso (Unix)", {"pid": pid}, "B")
                # #endregion agent log
                return True
            except ProcessLookupError:
                # #region agent log
                _log_debug("main.py:matar_processo_por_pid", "Processo já não existe (Unix)", {"pid": pid}, "B")
                # #endregion agent log
                return True  # Processo já não existe
            except PermissionError:
                # #region agent log
                _log_debug("main.py:matar_processo_por_pid", "Sem permissão para matar processo", {"pid": pid}, "B")
                # #endregion agent log
                return False
        
    except Exception as e:
        # #region agent log
        _log_debug("main.py:matar_processo_por_pid", "Erro ao matar processo", {"pid": pid, "erro": str(e)}, "B")
        # #endregion agent log
        return False

def verificar_e_liberar_porta(porta):
    """
    Verifica se a porta está em uso e, se estiver, mata o processo que a está usando.
    Retorna True se a porta está livre (ou foi liberada), False caso contrário.
    """
    # #region agent log
    _log_debug("main.py:verificar_e_liberar_porta", "Iniciando verificação de porta", {"porta": porta}, "C")
    # #endregion agent log
    
    # Obter PID do processo atual para não matar a si mesmo
    pid_atual = os.getpid()
    # #region agent log
    _log_debug("main.py:verificar_e_liberar_porta", "PID atual", {"pid_atual": pid_atual}, "C")
    # #endregion agent log
    
    # Verificar se a porta está em uso usando socket (método mais confiável)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex(('127.0.0.1', porta))
        sock.close()
        
        if result == 0:
            # Porta está em uso
            # #region agent log
            _log_debug("main.py:verificar_e_liberar_porta", "Porta em uso detectada", {"porta": porta}, "C")
            # #endregion agent log
            
            # Obter PID do processo usando a porta
            pid_antigo = obter_pid_por_porta(porta)
            
            if pid_antigo:
                # #region agent log
                _log_debug("main.py:verificar_e_liberar_porta", "PID do processo antigo", {"pid_antigo": pid_antigo, "pid_atual": pid_atual}, "C")
                # #endregion agent log
                
                # Não matar a si mesmo
                if pid_antigo == pid_atual:
                    # #region agent log
                    _log_debug("main.py:verificar_e_liberar_porta", "PID é o mesmo do processo atual, ignorando", {}, "C")
                    # #endregion agent log
                    return True
                
                # Matar o processo antigo
                print(f"Processo antigo encontrado na porta {porta} (PID: {pid_antigo}). Encerrando...")
                sucesso = matar_processo_por_pid(pid_antigo)
                
                if sucesso:
                    print(f"Processo antigo encerrado com sucesso.")
                    # Aguardar um pouco para a porta ser liberada
                    import time
                    time.sleep(1)
                    
                    # Verificar novamente se a porta foi liberada
                    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        result2 = sock2.connect_ex(('127.0.0.1', porta))
                        sock2.close()
                        
                        if result2 != 0:
                            # #region agent log
                            _log_debug("main.py:verificar_e_liberar_porta", "Porta liberada com sucesso", {"porta": porta}, "C")
                            # #endregion agent log
                            return True
                        else:
                            # #region agent log
                            _log_debug("main.py:verificar_e_liberar_porta", "Porta ainda em uso após matar processo", {"porta": porta}, "C")
                            # #endregion agent log
                            print(f"AVISO: Porta {porta} ainda está em uso após tentar encerrar o processo.")
                            return False
                    except:
                        # #region agent log
                        _log_debug("main.py:verificar_e_liberar_porta", "Erro ao verificar porta após matar processo", {}, "C")
                        # #endregion agent log
                        return False
                else:
                    # #region agent log
                    _log_debug("main.py:verificar_e_liberar_porta", "Falha ao matar processo antigo", {"pid_antigo": pid_antigo}, "C")
                    # #endregion agent log
                    print(f"ERRO: Não foi possível encerrar o processo antigo (PID: {pid_antigo}).")
                    return False
            else:
                # #region agent log
                _log_debug("main.py:verificar_e_liberar_porta", "Não foi possível obter PID do processo usando a porta", {"porta": porta}, "C")
                # #endregion agent log
                print(f"AVISO: Porta {porta} está em uso, mas não foi possível identificar o processo.")
                return False
        else:
            # Porta está livre
            # #region agent log
            _log_debug("main.py:verificar_e_liberar_porta", "Porta livre", {"porta": porta}, "C")
            # #endregion agent log
            return True
    except Exception as e:
        # #region agent log
        _log_debug("main.py:verificar_e_liberar_porta", "Erro ao verificar porta", {"porta": porta, "erro": str(e)}, "C")
        # #endregion agent log
        print(f"ERRO ao verificar porta {porta}: {e}")
        return False

def signal_handler(signum, frame):
    """Handler para sinais de encerramento"""
    print(f"\nRecebido sinal {signum}, encerrando aplicação...")
    cleanup_flask()
    sys.exit(0)

def main():
    # Registrar handlers de sinal (apenas em sistemas Unix)
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    # Mostrar versão do sistema
    print("=" * 60)
    print(f"Sistema de Gestao de Pacientes")
    print(f"Versao: {VERSION}")
    print(f"Build: {BUILD_DATE}")
    print("=" * 60)
    
    # Obter porta a ser usada (do .env ou variável de ambiente)
    porta = int(os.getenv('PORT', 5000))
    
    # #region agent log
    _log_debug("main.py:main", "Iniciando main", {"porta": porta}, "D")
    # #endregion agent log
    
    # Verificar e liberar porta antes de iniciar o servidor
    print(f"Verificando porta {porta}...")
    if not verificar_e_liberar_porta(porta):
        print(f"ERRO: Não foi possível liberar a porta {porta}. Encerrando aplicação.")
        sys.exit(1)
    print(f"Porta {porta} está livre e pronta para uso.")
    
    # Detecta se está rodando como executável ou em modo silencioso
    is_executable = getattr(sys, 'frozen', False)
    
    # Verificar se está sendo executado em modo silencioso (via script ou .env)
    is_silent = '--silent' in sys.argv or os.getenv('SILENT_MODE', '0') == '1'
    
    # Verificar se deve usar tray icon
    # SEMPRE tentar usar tray icon quando possível (padrão)
    # Exceto se explicitamente desabilitado com --no-tray
    no_tray = '--no-tray' in sys.argv  # Flag para desabilitar tray
    force_tray = '--tray' in sys.argv  # Flag para forçar tray
    use_tray_env = os.getenv('USE_TRAY', '1') == '1'  # Padrão é usar tray
    use_tray = not no_tray and (force_tray or use_tray_env or is_executable or is_silent)
    
    if use_tray and not no_tray:
        # Modo com tray icon - TENTAR SEMPRE iniciar o tray icon
        try:
            from tray_icon import TrayIconManager
            
            tray_manager = TrayIconManager(app, port=porta)
            
            # Iniciar Flask em thread separada ANTES do tray
            print(f"Iniciando servidor Flask na porta {porta}...")
            tray_manager.iniciar_flask()
            
            # Aguardar Flask iniciar
            threading.Event().wait(2)
            
            # Verificar se Flask iniciou corretamente
            if tray_manager.verificar_porta():
                print(f"SUCCESS: Servidor Flask iniciado na porta {porta}")
            else:
                print("AVISO: Porta pode não estar disponível")
            
            # Iniciar tray icon (bloqueia até sair - thread principal)
            print("Iniciando tray icon...")
            tray_manager.iniciar_tray()
            
        except ImportError as e:
            print(f"AVISO: pystray não instalado: {e}")
            print("Instale com: pip install pystray pillow")
            print("Continuando sem tray icon...")
            # Fallback para modo sem tray
            if is_executable:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(
                    "Sistema de Gestão de Pacientes",
                    "Sistema iniciado com sucesso!\nClique em OK para abrir no navegador."
                )
                flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
                flask_thread.start()
                host = os.getenv('FLASK_HOST', '127.0.0.1')
                webbrowser.open(f'http://{host}:{porta}')
                
                def on_closing():
                    print("Janela fechada, encerrando aplicação...")
                    cleanup_flask()
                    root.destroy()
                    sys.exit(0)
                
                root.protocol("WM_DELETE_WINDOW", on_closing)
                
                try:
                    root.mainloop()
                except KeyboardInterrupt:
                    on_closing()
            elif is_silent:
                flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
                flask_thread.start()
                try:
                    flask_thread.join()
                except KeyboardInterrupt:
                    print("\nInterrompido pelo usuário")
                    cleanup_flask()
                    sys.exit(0)
        except Exception as e:
            print(f"Erro ao iniciar tray icon: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: continuar sem tray
            if is_executable:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo(
                    "Sistema de Gestão de Pacientes",
                    "Sistema iniciado com sucesso!\nClique em OK para abrir no navegador."
                )
                flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
                flask_thread.start()
                host = os.getenv('FLASK_HOST', '127.0.0.1')
                webbrowser.open(f'http://{host}:{porta}')
                
                def on_closing():
                    print("Janela fechada, encerrando aplicação...")
                    cleanup_flask()
                    root.destroy()
                    sys.exit(0)
                
                root.protocol("WM_DELETE_WINDOW", on_closing)
                
                try:
                    root.mainloop()
                except KeyboardInterrupt:
                    on_closing()
            elif is_silent:
                flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
                flask_thread.start()
                try:
                    flask_thread.join()
                except KeyboardInterrupt:
                    print("\nInterrompido pelo usuário")
                    cleanup_flask()
                    sys.exit(0)
    elif is_executable:
        # Modo executável sem tray: mostra janela informativa e abre navegador
        root = tk.Tk()
        root.withdraw()  # esconde a janela principal

        messagebox.showinfo(
            "Sistema de Gestão de Pacientes",
            "Sistema iniciado com sucesso!\nClique em OK para abrir no navegador."
        )

        # Flask em thread separada SEM debug (evita erro de signal)
        flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
        flask_thread.start()
        webbrowser.open('http://localhost:5000')
        
        # Handler para quando a janela fecha
        def on_closing():
            print("Janela fechada, encerrando aplicação...")
            cleanup_flask()
            root.destroy()
            sys.exit(0)
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Mantém a aplicação rodando
        try:
            root.mainloop()
        except KeyboardInterrupt:
            on_closing()
    elif is_silent:
        # Modo silencioso: execução em background sem output
        flask_thread = threading.Thread(target=run_flask, args=(False, False, True), daemon=False)
        flask_thread.start()
        # Aguardar indefinidamente
        try:
            flask_thread.join()  # Aguardar thread do Flask
        except KeyboardInterrupt:
            print("\nInterrompido pelo usuário")
            cleanup_flask()
            sys.exit(0)
    else:
        # Modo desenvolvimento: usar tray apenas se explicitamente solicitado
        if '--tray' in sys.argv:
            # Modo desenvolvimento COM tray icon
            try:
                from tray_icon import TrayIconManager
                
                tray_manager = TrayIconManager(app, port=porta)
                
                # Iniciar Flask em thread separada
                tray_manager.iniciar_flask()
                
                # Aguardar Flask iniciar
                threading.Event().wait(2)
                
                # Tentar iniciar tray icon
                print("Modo desenvolvimento com tray icon...")
                tray_manager.iniciar_tray()
            
            except (ImportError, Exception) as e:
                print(f"Tray icon não disponível: {e}")
                print("Continuando em modo desenvolvimento normal...")
                run_flask(debug=True, use_reloader=True, silent=False)
        else:
            # Modo desenvolvimento: tentar usar tray icon se disponível
            try:
                from tray_icon import TrayIconManager
                
                tray_manager = TrayIconManager(app, port=porta)
                
                # Iniciar Flask em thread separada
                print(f"Iniciando servidor Flask na porta {porta}...")
                tray_manager.iniciar_flask()
                
                # Aguardar Flask iniciar
                threading.Event().wait(2)
                
                # Tentar iniciar tray icon
                print("Iniciando tray icon...")
                tray_manager.iniciar_tray()
                
            except (ImportError, Exception) as e:
                # Fallback: modo desenvolvimento normal sem tray
                print(f"Tray icon não disponível ({e}). Modo desenvolvimento normal...")
                print("Instale pystray e Pillow para usar tray icon: pip install pystray pillow")
                run_flask(debug=True, use_reloader=True, silent=False)

if __name__ == '__main__':
    main()
