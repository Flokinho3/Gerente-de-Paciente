import sqlite3
from datetime import datetime

class SchemaMixin:
    def _ensure_schema(self) -> None:
        ddl = """
        CREATE TABLE IF NOT EXISTS pacientes (
            id TEXT PRIMARY KEY,
            nome_gestante TEXT NOT NULL,
            unidade_saude TEXT,
            data_salvamento TEXT,
            inicio_pre_natal_antes_12s INTEGER,
            inicio_pre_natal_semanas INTEGER,
            inicio_pre_natal_observacao TEXT,
            consultas_pre_natal INTEGER,
            vacinas_completas TEXT,
            plano_parto INTEGER,
            participou_grupos INTEGER,
            avaliacao_odontologica INTEGER,
            estratificacao INTEGER,
            estratificacao_problema TEXT,
            cartao_pre_natal_completo INTEGER,
            dum TEXT,
            dpp TEXT,
            ganhou_kit INTEGER,
            kit_tipo TEXT,
            proxima_avaliacao TEXT,
            proxima_avaliacao_hora TEXT,
            arquivo_origem TEXT
        )
        """
        self.conn.execute(ddl)
        # Adicionar colunas se não existirem (migrações históricas mantidas)
        migration_columns = [
            ("estratificacao_problema", "TEXT"),
            ("inicio_pre_natal_semanas", "INTEGER"),
            ("inicio_pre_natal_observacao", "TEXT"),
            ("proxima_avaliacao", "TEXT"),
            ("proxima_avaliacao_hora", "TEXT"),
            ("dum", "TEXT"),
            ("dpp", "TEXT"),
            ("ganhou_kit", "INTEGER"),
            ("kit_tipo", "TEXT"),
            ("ja_ganhou_crianca", "INTEGER"),
            ("data_ganhou_crianca", "TEXT"),
            ("quantidade_filhos", "INTEGER"),
            ("generos_filhos", "TEXT"),
            ("metodo_preventivo", "TEXT"),
            ("metodo_preventivo_outros", "TEXT"),
            ("possui_bolsa_familia", "INTEGER"),
            ("tem_vacina_covid", "INTEGER"),
            ("plano_parto_entregue_por_unidade", "TEXT"),
            ("pc_id", "TEXT"),
            ("ultima_modificacao", "TEXT"),
            ("versao", "INTEGER DEFAULT 1"),
            ("status", "TEXT DEFAULT 'ativo'"),
            ("removido_em", "TEXT"),
            ("removido_por", "TEXT")
        ]
        
        for col_name, col_type in migration_columns:
            try:
                self.conn.execute(f"ALTER TABLE pacientes ADD COLUMN {col_name} {col_type}")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass  # Coluna já existe

        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nome ON pacientes(nome_gestante)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_unidade ON pacientes(unidade_saude)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_pacientes_status ON pacientes(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_pacientes_pc_id ON pacientes(pc_id)")
        
        # Criar tabela de agendamentos
        ddl_agendamentos = """
        CREATE TABLE IF NOT EXISTS agendamentos (
            id TEXT PRIMARY KEY,
            paciente_id TEXT,
            data_consulta TEXT NOT NULL,
            hora_consulta TEXT NOT NULL,
            tipo_consulta TEXT,
            observacoes TEXT,
            status TEXT DEFAULT 'agendado',
            data_criacao TEXT,
            data_atualizacao TEXT,
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id)
        )
        """
        self.conn.execute(ddl_agendamentos)
        
        migration_columns_agendamentos = [
            ("pc_id", "TEXT"),
            ("ultima_modificacao", "TEXT"),
            ("versao", "INTEGER DEFAULT 1"),
            ("removido_em", "TEXT"),
            ("removido_por", "TEXT")
        ]
        
        for col_name, col_type in migration_columns_agendamentos:
            try:
                self.conn.execute(f"ALTER TABLE agendamentos ADD COLUMN {col_name} {col_type}")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass  # Coluna já existe
                
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamento_paciente ON agendamentos(paciente_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamento_data ON agendamentos(data_consulta)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamentos_status ON agendamentos(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamentos_pc_id ON agendamentos(pc_id)")
        
        # Table for pending conflicts
        ddl_conflitos = """
        CREATE TABLE IF NOT EXISTS conflitos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            timestamp TEXT,
            origem TEXT
        )
        """
        self.conn.execute(ddl_conflitos)
        
        # Table for ignored items
        ddl_itens_ignorados = """
        CREATE TABLE IF NOT EXISTS itens_ignorados (
            id TEXT PRIMARY KEY,
            paciente_id TEXT NOT NULL,
            dados_backup TEXT,
            tipo_acao TEXT,
            data_criacao TEXT,
            data_expiracao TEXT,
            motivo TEXT,
            origem_backup TEXT
        )
        """
        self.conn.execute(ddl_itens_ignorados)
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_itens_ignorados_paciente ON itens_ignorados(paciente_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_itens_ignorados_expiracao ON itens_ignorados(data_expiracao)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_itens_ignorados_origem ON itens_ignorados(origem_backup)")
        self.conn.commit()

    def _migrar_dados_existentes(self) -> None:
        """
        Migra dados existentes preenchendo campos novos para registros antigos.
        """
        try:
            cursor = self.conn.cursor()
            now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Migrar pacientes
            cursor.execute("""
                UPDATE pacientes 
                SET 
                    pc_id = ?,
                    ultima_modificacao = COALESCE(ultima_modificacao, data_salvamento, ?),
                    versao = COALESCE(versao, 1),
                    status = COALESCE(status, 'ativo')
                WHERE pc_id IS NULL OR ultima_modificacao IS NULL OR versao IS NULL OR status IS NULL
            """, (self.pc_id, now_str))
            
            # Migrar agendamentos
            cursor.execute("""
                UPDATE agendamentos 
                SET 
                    pc_id = ?,
                    ultima_modificacao = COALESCE(ultima_modificacao, data_atualizacao, data_criacao, ?),
                    versao = COALESCE(versao, 1)
                WHERE pc_id IS NULL OR ultima_modificacao IS NULL OR versao IS NULL
            """, (self.pc_id, now_str))
            
            self.conn.commit()
        except Exception:
            pass
