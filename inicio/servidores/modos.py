"""
Inicialização dos modos de servidor: duplo, tray, executável, silencioso, desenvolvimento.
"""
import os
import sys
import threading
import time
import webbrowser

import tkinter as tk
from tkinter import messagebox

from flask_app import app, run_flask, cleanup_flask

from inicio.utils.erro import exibir_erro
from inicio.opcoes import deve_exibir_console
from inicio.rede import verificar_e_liberar_porta, sincronizar_servidores

def _detectar_ip_local():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    except Exception:
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return '127.0.0.1'

def obter_host_navegador():
    public_host = (os.getenv('FLASK_PUBLIC_HOST') or '').strip()
    if public_host:
        return public_host
    host = (os.getenv('FLASK_HOST') or '127.0.0.1').strip()
    if host in ('0.0.0.0', '::', '127.0.0.1', 'localhost'):
        return _detectar_ip_local()
    return host


def iniciar_servidor_em_porta(porta, debug=False, use_reloader=False, silent=False):
    """Inicia um servidor Flask em uma porta específica"""
    def servidor_thread():
        run_flask(debug=debug, use_reloader=use_reloader, silent=silent, port=porta)

    thread = threading.Thread(target=servidor_thread, daemon=False)
    thread.start()
    return thread


def verificar_servidor(porta):
    """Verifica se um servidor está respondendo"""
    try:
        import urllib.request
        url = f'http://127.0.0.1:{porta}/api/version'
        req = urllib.request.Request(url)
        urllib.request.urlopen(req, timeout=2)
        return True
    except Exception:
        return False


def iniciar_servidores_duplos(config):
    """Inicia dois servidores em portas diferentes"""
    porta1 = config['porta']
    porta2 = config['porta2']
    host_navegador = obter_host_navegador()

    if deve_exibir_console(config):
        print(f"Iniciando servidores em portas {porta1} e {porta2}...")

    if deve_exibir_console(config):
        print(f"Verificando porta {porta1}...")
    if not verificar_e_liberar_porta(porta1):
        exibir_erro(
            "Erro ao Iniciar Sistema",
            f"Não foi possível liberar a porta {porta1}.\n\nPossíveis causas:\n- Porta já está em uso\n- Permissões insuficientes\n- Firewall bloqueando",
            None
        )
        sys.exit(1)
    if deve_exibir_console(config):
        print(f"Porta {porta1} está livre e pronta para uso.")

    if deve_exibir_console(config):
        print(f"Verificando porta {porta2}...")
    if not verificar_e_liberar_porta(porta2):
        exibir_erro(
            "Erro ao Iniciar Sistema",
            f"Não foi possível liberar a porta {porta2}.\n\nPossíveis causas:\n- Porta já está em uso\n- Permissões insuficientes\n- Firewall bloqueando",
            None
        )
        sys.exit(1)
    if deve_exibir_console(config):
        print(f"Porta {porta2} está livre e pronta para uso.")

    if deve_exibir_console(config):
        print(f"Iniciando servidor Flask na porta {porta1}...")
    thread1 = iniciar_servidor_em_porta(porta1, debug=False, use_reloader=False, silent=False)

    time.sleep(1)

    if deve_exibir_console(config):
        print(f"Iniciando servidor Flask na porta {porta2}...")
    thread2 = iniciar_servidor_em_porta(porta2, debug=False, use_reloader=False, silent=False)

    if deve_exibir_console(config):
        print("Aguardando servidores iniciarem...")
    time.sleep(3)

    servidor1_ok = verificar_servidor(porta1)
    servidor2_ok = verificar_servidor(porta2)

    if not servidor1_ok or not servidor2_ok:
        if deve_exibir_console(config):
            print("AVISO: Um ou ambos os servidores podem não estar prontos ainda.")

    if deve_exibir_console(config):
        print(f"\n{'='*60}")
        print("Sincronizando bancos de dados...")
        print(f"{'='*60}")

    sincronizar_servidores(porta1, porta2)
    sincronizar_servidores(porta2, porta1)

    if deve_exibir_console(config):
        print(f"\n{'='*60}")
        print("SUCESSO: Dois servidores Flask iniciados!")
        print(f"Servidor 1: http://{host_navegador}:{porta1}")
        print(f"Servidor 2: http://{host_navegador}:{porta2}")
        print(f"{'='*60}\n")

    try:
        webbrowser.open(f'http://{host_navegador}:{porta1}')
        time.sleep(0.5)
        webbrowser.open(f'http://{host_navegador}:{porta2}')
    except Exception:
        pass

    try:
        thread1.join()
        thread2.join()
    except KeyboardInterrupt:
        if deve_exibir_console(config):
            print("\nInterrompido pelo usuário")
        cleanup_flask()
        sys.exit(0)


def criar_janela_tkinter_executavel(porta, config):
    """Cria janela Tkinter para executável sem tray"""
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Sistema de Gestão de Pacientes",
        "Sistema iniciado com sucesso!\nClique em OK para abrir no navegador."
    )

    def _run():
        run_flask(debug=False, use_reloader=False, silent=True, port=porta)

    flask_thread = threading.Thread(target=_run, daemon=False)
    flask_thread.start()
    host = obter_host_navegador()
    webbrowser.open(f'http://{host}:{porta}')

    def on_closing():
        if deve_exibir_console(config):
            print("Janela fechada, encerrando aplicação...")
        cleanup_flask()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()


def iniciar_com_tray_icon(porta, config):
    """Inicia servidor com tray icon"""
    try:
        from tray_icon import TrayIconManager

        tray_manager = TrayIconManager(app, port=porta)

        if deve_exibir_console(config):
            print(f"Iniciando servidor Flask na porta {porta}...")
        tray_manager.iniciar_flask()

        threading.Event().wait(2)

        if not tray_manager.verificar_porta():
            exibir_erro(
                "Erro ao Iniciar Servidor",
                f"O servidor Flask não conseguiu iniciar na porta {porta}.\n\nVerifique se:\n- A porta não está sendo usada por outro processo\n- Você tem permissões suficientes",
                None
            )
            sys.exit(1)

        if deve_exibir_console(config):
            print(f"SUCCESS: Servidor Flask iniciado na porta {porta}")

        if deve_exibir_console(config):
            print("Iniciando tray icon...")
        tray_manager.iniciar_tray()

    except ImportError as e:
        if deve_exibir_console(config):
            print(f"AVISO: pystray não instalado: {e}")
            print("Instale com: pip install pystray pillow")
            print("Continuando sem tray icon...")

        if config['is_executable']:
            criar_janela_tkinter_executavel(porta, config)
        elif config['is_silent']:
            def _run():
                run_flask(debug=False, use_reloader=False, silent=True, port=porta)
            flask_thread = threading.Thread(target=_run, daemon=False)
            flask_thread.start()
            try:
                flask_thread.join()
            except KeyboardInterrupt:
                if deve_exibir_console(config):
                    print("\nInterrompido pelo usuário")
                cleanup_flask()
                sys.exit(0)

    except Exception as e:
        exibir_erro(
            "Erro ao Iniciar Tray Icon",
            "Não foi possível iniciar o ícone na bandeja do sistema.\n\nO sistema continuará sem o tray icon.",
            e
        )

        if config['is_executable']:
            criar_janela_tkinter_executavel(porta, config)
        elif config['is_silent']:
            def _run():
                run_flask(debug=False, use_reloader=False, silent=True, port=porta)
            flask_thread = threading.Thread(target=_run, daemon=False)
            flask_thread.start()
            try:
                flask_thread.join()
            except KeyboardInterrupt:
                if deve_exibir_console(config):
                    print("\nInterrompido pelo usuário")
                cleanup_flask()
                sys.exit(0)


def iniciar_modo_executavel_sem_tray(porta, config):
    """Inicia servidor em modo executável sem tray"""
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Sistema de Gestão de Pacientes",
        "Sistema iniciado com sucesso!\nClique em OK para abrir no navegador."
    )

    def _run():
        run_flask(debug=False, use_reloader=False, silent=True, port=porta)

    flask_thread = threading.Thread(target=_run, daemon=False)
    flask_thread.start()
    host = obter_host_navegador()
    webbrowser.open(f'http://{host}:{porta}')

    def on_closing():
        if deve_exibir_console(config):
            print("Janela fechada, encerrando aplicação...")
        cleanup_flask()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()


def iniciar_modo_silencioso(config):
    """Inicia servidor em modo silencioso"""
    porta = config['porta']

    def _run():
        run_flask(debug=False, use_reloader=False, silent=True, port=porta)

    flask_thread = threading.Thread(target=_run, daemon=False)
    flask_thread.start()

    try:
        flask_thread.join()
    except KeyboardInterrupt:
        if deve_exibir_console(config):
            print("\nInterrompido pelo usuário")
        cleanup_flask()
        sys.exit(0)


def iniciar_modo_desenvolvimento(porta, config):
    """Inicia servidor em modo desenvolvimento"""
    if '--tray' in sys.argv:
        try:
            from tray_icon import TrayIconManager

            tray_manager = TrayIconManager(app, port=porta)
            tray_manager.iniciar_flask()
            threading.Event().wait(2)
            print("Modo desenvolvimento com tray icon...")
            tray_manager.iniciar_tray()
        except (ImportError, Exception) as e:
            print(f"Tray icon não disponível: {e}")
            print("Continuando em modo desenvolvimento normal...")
            run_flask(debug=True, use_reloader=True, silent=False, port=porta)
    else:
        try:
            from tray_icon import TrayIconManager

            tray_manager = TrayIconManager(app, port=porta)
            print(f"Iniciando servidor Flask na porta {porta}...")
            tray_manager.iniciar_flask()
            threading.Event().wait(2)
            print("Iniciando tray icon...")
            tray_manager.iniciar_tray()
        except (ImportError, Exception) as e:
            print(f"Tray icon não disponível ({e}). Modo desenvolvimento normal...")
            print("Instale pystray e Pillow para usar tray icon: pip install pystray pillow")
            run_flask(debug=True, use_reloader=True, silent=False, port=porta)
