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
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

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
        url = f'http://localhost:{self.port}'
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
        """Para o servidor Flask"""
        self.is_running = False
        
        # Usar shutdown do Werkzeug se disponível
        try:
            if hasattr(self, '_server') and self._server:
                print("Encerrando servidor Flask...")
                self._server.shutdown()
                self._server = None
        except Exception as e:
            print(f"Erro ao encerrar servidor: {e}")
        
        # Aguardar thread finalizar (máximo 3 segundos)
        if self.flask_thread and self.flask_thread.is_alive():
            for _ in range(30):  # 30 tentativas de 0.1s = 3 segundos
                if not self.flask_thread.is_alive():
                    break
                threading.Event().wait(0.1)
            
            # Se ainda estiver vivo, forçar encerramento
            if self.flask_thread.is_alive():
                print("Aviso: Thread do Flask não finalizou normalmente")
        
        print("Servidor Flask encerrado")
    
    def iniciar_flask(self):
        """Inicia o servidor Flask em thread separada"""
        def run():
            try:
                import logging
                log = logging.getLogger('werkzeug')
                
                # Verificar modo debug do .env
                debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
                
                # Configurar nível de log baseado no debug
                if debug_mode:
                    log.setLevel(logging.DEBUG)
                    print(f"Modo DEBUG ativado (via .env)")
                else:
                    log.setLevel(logging.ERROR)
                
                self.is_running = True
                from werkzeug.serving import make_server
                host = os.getenv('FLASK_HOST', '127.0.0.1')
                self._server = make_server(host, self.port, self.flask_app)
                print(f"Servidor Flask iniciado em http://{host}:{self.port} (Debug: {debug_mode})")
                self._server.serve_forever()
            except Exception as e:
                print(f"Erro ao iniciar Flask: {e}")
                self.is_running = False
        
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
        url_text = f"http://localhost:{self.port}"
        
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
            print("3. Execute como administrador se necessário")
            print("4. Verifique se não há antivírus bloqueando")
            return False
