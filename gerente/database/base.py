import os
import sqlite3
from typing import Optional

class DatabaseBase:
    def __init__(self, db_path: Optional[str] = None):
        # Verificar se há um caminho configurado via variável de ambiente
        from gerente.env_loader import load_env
        load_env()
        env_db_path = os.getenv('DB_PATH')
        
        if db_path:
            # Prioridade 1: caminho passado explicitamente
            self.db_path = db_path
        elif env_db_path:
            # Prioridade 2: caminho do arquivo .env
            self.db_path = env_db_path
        else:
            # Prioridade 3: caminho padrão local
            import sys
            if getattr(sys, 'frozen', False):
                # Executável: usa diretório do executável
                base_dir = os.path.dirname(sys.executable)
            else:
                # Modo desenvolvimento: usa diretório do script
                # __file__ agora está em gerente/database/base.py, queremos o pai do pai de gerente
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.db_path = os.path.join(base_dir, 'data', 'pacientes.db')
        
        # Criar diretório se necessário (apenas para caminhos locais)
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and (not os.path.isabs(db_dir) or not os.path.exists(os.path.dirname(os.path.abspath(self.db_path)))):
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except (OSError, ValueError):
            # Se for um caminho de rede ou caminho absoluto problemático, apenas tentar conectar
            pass
        
        # Configurar timeout maior para banco compartilhado em rede
        # WAL mode para melhor concorrência (opcional, mas recomendado)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        # Habilitar WAL mode para melhor suporte a múltiplos acessos simultâneos
        try:
            self.conn.execute('PRAGMA journal_mode=WAL;')
            self.conn.commit()
        except sqlite3.OperationalError:
            # Se WAL não for suportado (ex: em alguns sistemas de arquivos de rede), continuar normalmente
            pass
        
        # Carregar PC_ID
        from gerente.config import get_pc_id
        self.pc_id = get_pc_id()
        
        self._ensure_schema()
        # Migrar dados existentes (preencher campos novos para registros antigos)
        self._migrar_dados_existentes()

    def close(self) -> None:
        if hasattr(self, 'conn'):
            self.conn.close()

    def testar_conexao(self) -> dict:
        """Testa a conexão com o banco de dados executando uma consulta simples"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return {'status': 'ok', 'mensagem': 'Conexão estabelecida com sucesso'}
        except Exception as e:
            return {'status': 'erro', 'mensagem': f'Erro na conexão: {str(e)}'}
