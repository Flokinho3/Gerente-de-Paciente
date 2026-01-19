"""
Sistema de Tray Icon (Bandeja do Sistema)
Gerencia o ícone na bandeja com menu de ações
"""
import threading
import webbrowser
import sys
import os
from PIL import Image, ImageDraw, ImageFont

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
        
    def criar_icone(self):
        """Cria um ícone simples para a bandeja"""
        # Criar imagem 64x64 com fundo transparente
        image = Image.new('RGB', (64, 64), color='white')
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
            from werkzeug.serving import make_server
            if hasattr(self, '_server') and self._server:
                self._server.shutdown()
        except:
            pass
        
        # Aguardar thread finalizar
        if self.flask_thread and self.flask_thread.is_alive():
            threading.Event().wait(1)
    
    def iniciar_flask(self):
        """Inicia o servidor Flask em thread separada"""
        def run():
            try:
                import logging
                log = logging.getLogger('werkzeug')
                log.setLevel(logging.ERROR)
                
                self.is_running = True
                from werkzeug.serving import make_server
                self._server = make_server('127.0.0.1', self.port, self.flask_app)
                self._server.serve_forever()
            except Exception as e:
                print(f"Erro ao iniciar Flask: {e}")
                self.is_running = False
        
        self.flask_thread = threading.Thread(target=run, daemon=True)
        self.flask_thread.start()
    
    def sair_aplicacao(self, icon=None, item=None):
        """Encerra a aplicação completamente"""
        # Parar Flask
        self.parar_flask()
        
        # Aguardar um pouco para garantir que a porta foi liberada
        threading.Event().wait(1)
        
        # Parar o tray icon
        if self.icon:
            self.icon.stop()
        
        # Sair do programa
        os._exit(0)
    
    def criar_menu(self):
        """Cria o menu do tray icon"""
        status_text = "🟢 Rodando" if (self.is_running and self.verificar_porta()) else "🔴 Parado"
        porta_text = f"Porta: {self.port}"
        url_text = f"http://localhost:{self.port}"
        
        menu = pystray.Menu(
            item(f'{status_text} - {porta_text}', None, enabled=False),
            item(f'URL: {url_text}', None, enabled=False),
            item('─' * 35, None, enabled=False),
            item('🌐 Abrir no Navegador', self.abrir_navegador),
            item('🔄 Reiniciar', self.reiniciar_aplicacao),
            item('❌ Sair', self.sair_aplicacao)
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
            # Criar ícone
            image = self.criar_icone()
            
            # Criar menu inicial
            menu = self.criar_menu()
            
            # Criar tray icon (título SEM emojis para compatibilidade X11/latin-1)
            # O título precisa ser ASCII-safe para X11
            titulo_safe = f"Gerente de Pacientes - Porta {self.port}"
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
                        except:
                            break  # Sair se tray foi fechado
            
            status_thread = threading.Thread(target=atualizar_status, daemon=True)
            status_thread.start()
            
            # Iniciar tray icon (bloqueia até sair - deve ser na thread principal)
            self.icon.run()
            
            return True
        except Exception as e:
            print(f"Erro ao iniciar tray icon: {e}")
            import traceback
            traceback.print_exc()
            return False
