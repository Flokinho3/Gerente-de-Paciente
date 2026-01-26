"""
Sistema de Tray Icon (Bandeja do Sistema)
Gerencia o ícone na bandeja com menu de ações
"""
import threading
import webbrowser
import sys
import os
import subprocess
import signal
import atexit
from PIL import Image, ImageDraw

from env_loader import load_env
load_env()

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

try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    pystray = None
    item = None

class TrayIconManager:
    def __init__(self, flask_app, port=5000):
        self.flask_app = flask_app
        self.port = port
        self.icon = None
        self.is_running = False
        self.flask_thread = None
        self._server = None
        
        # Registrar handler de encerramento
        atexit.register(self.cleanup)
        
        # Registrar handlers de sinal
        if sys.platform != 'win32':
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de encerramento"""
        print(f"\nRecebido sinal {signum}, encerrando aplicação...")
        self.sair_aplicacao()
    
    def cleanup(self):
        """Limpeza ao encerrar aplicação"""
        if self.is_running:
            self.parar_flask()
        
    def criar_icone(self):
        """Carrega o logo para usar como ícone na bandeja"""
        try:
            import sys
            
            # Tentar carregar o logo
            caminho_logo = None
            
            # Detectar se está rodando como executável ou em desenvolvimento
            if getattr(sys, 'frozen', False):
                # Modo executável: procurar em vários locais possíveis
                # 1. No diretório temporário do PyInstaller (sys._MEIPASS)
                if hasattr(sys, '_MEIPASS'):
                    caminho_temp = os.path.join(sys._MEIPASS, 'static', 'img', 'logo.png')
                    if os.path.exists(caminho_temp):
                        caminho_logo = caminho_temp
                
                # 2. No diretório do executável
                if not caminho_logo:
                    caminho_exe = os.path.join(os.path.dirname(sys.executable), 'static', 'img', 'logo.png')
                    if os.path.exists(caminho_exe):
                        caminho_logo = caminho_exe
            else:
                # Modo desenvolvimento: usar o diretório do script
                caminho_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'logo.png')
            
            # Se encontrou o logo, carregar e redimensionar
            if caminho_logo and os.path.exists(caminho_logo):
                image = Image.open(caminho_logo)
                # Redimensionar para 64x64 mantendo proporção
                # Usar LANCZOS se disponível, senão usar ANTIALIAS (versões antigas do PIL)
                try:
                    image = image.resize((64, 64), Image.Resampling.LANCZOS)
                except AttributeError:
                    # Fallback para versões antigas do PIL
                    image = image.resize((64, 64), Image.ANTIALIAS)
                # Converter para RGBA se necessário
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                return image
        except Exception as e:
            print(f"Erro ao carregar logo, usando ícone padrão: {e}")
        
        # Fallback: criar um ícone simples se não conseguir carregar o logo
        image = Image.new('RGBA', (64, 64), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Desenhar um círculo azul (representando saúde)
        draw.ellipse([10, 10, 54, 54], fill='#2196F3', outline='#1976D2', width=2)
        
        # Desenhar uma cruz branca (símbolo médico)
        draw.line([32, 20, 32, 44], fill='white', width=4)
        draw.line([20, 32, 44, 32], fill='white', width=4)
        
        return image
    
    def verificar_porta(self):
        """Verifica se a porta está em uso"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', self.port))
        sock.close()
        return result == 0
    
    def atualizar_titulo(self):
        """Atualiza o título do tray icon com status (sem emojis para compatibilidade X11)"""
        if self.is_running and self.verificar_porta():
            status = f"[OK] Rodando - Porta {self.port}"
        else:
            status = f"[X] Parado - Porta {self.port}"
        return f"Gerente de Pacientes - {status}"
    
    def abrir_navegador(self, icon=None, item=None):
        """Abre o navegador na porta configurada"""
        host = obter_host_navegador()
        url = f'http://{host}:{self.port}'
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Erro ao abrir navegador: {e}")
    
    def abrir_ajuda(self, icon=None, item=None):
        """Abre o arquivo de ajuda no Bloco de Notas do Windows"""
        try:
            caminho_ajuda = None
            
            # Detectar se está rodando como executável ou em desenvolvimento
            if getattr(sys, 'frozen', False):
                # Modo executável: procurar em vários locais possíveis
                # 1. No diretório temporário do PyInstaller (sys._MEIPASS)
                if hasattr(sys, '_MEIPASS'):
                    caminho_temp = os.path.join(sys._MEIPASS, 'COMO_USAR.txt')
                    if os.path.exists(caminho_temp):
                        caminho_ajuda = caminho_temp
                
                # 2. No diretório do executável
                if not caminho_ajuda:
                    caminho_exe = os.path.join(os.path.dirname(sys.executable), 'COMO_USAR.txt')
                    if os.path.exists(caminho_exe):
                        caminho_ajuda = caminho_exe
            else:
                # Modo desenvolvimento: usar o diretório do script
                caminho_ajuda = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'COMO_USAR.txt')
            
            # Verificar se o arquivo existe
            if not caminho_ajuda or not os.path.exists(caminho_ajuda):
                print("Arquivo de ajuda não encontrado")
                return
            
            # Abrir no Bloco de Notas do Windows
            subprocess.Popen(['notepad.exe', caminho_ajuda])
        except Exception as e:
            print(f"Erro ao abrir ajuda: {e}")
    
    def reiniciar_aplicacao(self, icon=None, item=None):
        """Reinicia a aplicação Flask"""
        print("Reiniciando servidor Flask...")
        
        # Parar Flask atual
        self.parar_flask()
        
        # Aguardar um pouco para garantir que parou
        threading.Event().wait(2)
        
        # Verificar se porta está livre
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', self.port))
        sock.close()
        
        if result == 0:
            # Porta ainda em uso, tentar liberar
            print("Aguardando porta ser liberada...")
            threading.Event().wait(1)
        
        # Iniciar Flask novamente
        self.iniciar_flask()
        
        # Aguardar iniciar
        threading.Event().wait(2)
        
        # Atualizar menu
        self.atualizar_menu()
        
        # Abrir navegador
        self.abrir_navegador()
    
    def parar_flask(self):
        """Para o servidor (Waitress)"""
        if not self.is_running:
            return
        self.is_running = False
        try:
            from inicio.rede.zeroconf_discovery import stop_zeroconf
            stop_zeroconf()
        except Exception:
            pass
        try:
            if hasattr(self, '_server') and self._server:
                print("Encerrando servidor...")
                self._server.close()
                self._server = None
        except Exception as e:
            print(f"Erro ao encerrar servidor: {e}")
        
        # Aguardar thread finalizar (máximo 3 segundos)
        if self.flask_thread and self.flask_thread.is_alive():
            for _ in range(30):  # 30 tentativas de 0.1s = 3 segundos
                if not self.flask_thread.is_alive():
                    break
                threading.Event().wait(0.1)
            
            if self.flask_thread.is_alive():
                print("Aviso: Thread do servidor não finalizou normalmente")
        print("Servidor encerrado")
    
    def iniciar_flask(self):
        """Inicia o servidor Flask em thread separada"""
        # Se já estiver rodando, não iniciar novamente
        if self.is_running and self.flask_thread and self.flask_thread.is_alive():
            print("Servidor Flask já está rodando")
            return
        
        def run():
            try:
                import logging
                debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
                is_executable = getattr(sys, 'frozen', False)
                host = os.getenv('FLASK_HOST', '127.0.0.1')
                threads = int(os.getenv('WAITRESS_THREADS', '8'))
                if not debug_mode:
                    logging.getLogger('werkzeug').setLevel(logging.ERROR)
                    logging.getLogger('waitress').setLevel(logging.WARNING)
                if hasattr(self.flask_app, 'config'):
                    self.flask_app.config['DEBUG'] = debug_mode
                self.is_running = True
                from waitress import create_server
                self._server = create_server(
                    self.flask_app, host=host, port=self.port, threads=threads
                )
                if not is_executable or debug_mode:
                    print(f"Servidor iniciado em http://{host}:{self.port} (Waitress, {threads} threads)")
                discovery = (os.getenv('DISCOVERY') or 'zeroconf').strip().lower()
                try:
                    if discovery == 'scan':
                        from inicio.rede import run_scan_loop
                        run_scan_loop(port=self.port)
                    else:
                        from inicio.rede.zeroconf_discovery import start_zeroconf
                        start_zeroconf(self.port)
                except Exception:
                    pass
                self._server.run()
            except Exception as e:
                self.is_running = False
                if is_executable and not debug_mode:
                    try:
                        import tkinter as tk
                        from tkinter import messagebox
                        root = tk.Tk()
                        root.withdraw()
                        messagebox.showerror(
                            "Erro ao Iniciar Servidor",
                            f"Não foi possível iniciar o servidor na porta {self.port}.\n\n"
                            f"Erro: {str(e)}\n\n"
                            f"Verifique se:\n"
                            f"- A porta não está em uso\n"
                            f"- Você tem permissões suficientes\n"
                            f"- O firewall não está bloqueando"
                        )
                        root.destroy()
                    except Exception:
                        pass
                else:
                    print(f"Erro ao iniciar servidor: {e}")
                    import traceback
                    traceback.print_exc()
        
        self.flask_thread = threading.Thread(target=run, daemon=True)
        self.flask_thread.start()
    
    def sair_aplicacao(self, icon=None, item=None):
        """Encerra a aplicação completamente"""
        print("Encerrando aplicação...")
        
        # Parar Flask primeiro
        self.parar_flask()
        
        # Aguardar um pouco para garantir que a porta foi liberada
        threading.Event().wait(2)
        
        # Verificar se porta foi liberada
        if self.verificar_porta():
            print("Aviso: Porta ainda em uso após encerramento")
        
        # Parar o tray icon
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass
        
        print("Aplicação encerrada")
        
        # Sair do programa
        os._exit(0)
    
    def criar_menu(self):
        """Cria o menu do tray icon (sem emojis para compatibilidade Windows)"""
        if self.is_running and self.verificar_porta():
            status_text = "[OK] Rodando"
        else:
            status_text = "[X] Parado"
        porta_text = f"Porta: {self.port}"
        host = obter_host_navegador()
        url_text = f"http://{host}:{self.port}"
        
        menu = pystray.Menu(
            item(f'{status_text} - {porta_text}', None, enabled=False),
            item(f'URL: {url_text}', None, enabled=False),
            item('-' * 35, None, enabled=False),
            item('Abrir no Navegador', self.abrir_navegador),
            item('Reiniciar', self.reiniciar_aplicacao),
            item('-' * 35, None, enabled=False),
            item('Ajuda', self.abrir_ajuda),
            item('Sair', self.sair_aplicacao)
        )
        return menu
    
    def atualizar_menu(self):
        """Atualiza o menu do tray icon"""
        if self.icon:
            try:
                self.icon.menu = self.criar_menu()
                # Título sem emojis para compatibilidade X11
                titulo_sem_emoji = self.atualizar_titulo()
                self.icon.title = titulo_sem_emoji
            except:
                pass  # Ignorar erros de atualização
    
    def iniciar_tray(self):
        """Inicia o tray icon"""
        if not pystray:
            print("pystray não está instalado. Instale com: pip install pystray pillow")
            return False
        
        try:
            import platform
            print(f"Sistema operacional: {platform.system()}")
            
            # Criar ícone
            print("Criando ícone...")
            image = self.criar_icone()
            print(f"Ícone criado: {image.size}, modo: {image.mode}")
            
            # Criar menu inicial
            menu = self.criar_menu()
            
            # Criar tray icon (título SEM emojis para compatibilidade Windows/X11)
            titulo_safe = f"Gerente de Pacientes - Porta {self.port}"
            print(f"Criando tray icon com título: {titulo_safe}")
            self.icon = pystray.Icon(
                "Gerente de Pacientes",
                image,
                titulo_safe,  # Título sem emojis
                menu
            )
            
            # Atualizar título inicial (sem emojis)
            self.atualizar_menu()
            
            # Thread para atualizar status periodicamente
            def atualizar_status():
                while True:
                    threading.Event().wait(5)  # Atualizar a cada 5 segundos
                    if self.icon:
                        try:
                            self.atualizar_menu()
                        except Exception as e:
                            print(f"Erro ao atualizar menu: {e}")
                            break  # Sair se tray foi fechado
            
            status_thread = threading.Thread(target=atualizar_status, daemon=True)
            status_thread.start()
            
            # Iniciar tray icon (bloqueia até sair - deve ser na thread principal)
            # No Windows, o pystray gerencia automaticamente o loop de mensagens
            print("Iniciando tray icon... Verifique a área de notificação do Windows.")
            print("(Se não aparecer, verifique se o Windows não está ocultando ícones)")
            
            try:
                self.icon.run()
            except KeyboardInterrupt:
                print("\nInterrompido pelo usuário")
            finally:
                # Garantir que Flask seja encerrado quando tray icon fecha
                print("Tray icon fechado, encerrando Flask...")
                self.parar_flask()
            
            return True
        except Exception as e:
            print(f"Erro ao iniciar tray icon: {e}")
            import traceback
            traceback.print_exc()
            print("\nDicas para resolver:")
            print("1. Certifique-se de que pystray está instalado: pip install pystray pillow")
            print("2. No Windows, verifique se os ícones não estão ocultos na área de notificação")
            print("3. Verifique se o aplicativo tem permissões de rede")
            print("4. Verifique se não há antivírus bloqueando")
            return False
