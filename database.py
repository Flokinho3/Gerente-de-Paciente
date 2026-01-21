"""
SQLite-based database layer for managing paciente data.
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def bool_to_int(value: Optional[bool]) -> int:
    return 1 if value else 0


def int_to_bool(value: Optional[int]) -> bool:
    return bool(value)


class Database:
    def __init__(self, db_path: Optional[str] = None):
        # Verificar se há um caminho configurado via variável de ambiente
        from dotenv import load_dotenv
        load_dotenv()
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
                base_dir = os.path.dirname(__file__)
            
            self.db_path = os.path.join(base_dir, 'data', 'pacientes.db')
        
        # Criar diretório se necessário (apenas para caminhos locais)
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.isabs(db_dir) or not os.path.exists(os.path.dirname(os.path.abspath(self.db_path))):
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
        self._ensure_schema()

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
        # Adicionar coluna estratificacao_problema se não existir (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN estratificacao_problema TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        # Adicionar colunas de início do pré-natal se não existirem (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN inicio_pre_natal_semanas INTEGER")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN inicio_pre_natal_observacao TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        # Adicionar coluna proxima_avaliacao se não existir (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN proxima_avaliacao TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        # Adicionar coluna proxima_avaliacao_hora se não existir (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN proxima_avaliacao_hora TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        # Adicionar colunas DUM, DPP, ganhou_kit e kit_tipo se não existirem (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN dum TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN dpp TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN ganhou_kit INTEGER")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN kit_tipo TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        # Adicionar novas colunas de histórico reprodutivo se não existirem (migração)
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN ja_ganhou_crianca INTEGER")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN data_ganhou_crianca TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN quantidade_filhos INTEGER")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN generos_filhos TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN metodo_preventivo TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        try:
            self.conn.execute("ALTER TABLE pacientes ADD COLUMN metodo_preventivo_outros TEXT")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Coluna já existe
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_nome ON pacientes(nome_gestante)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_unidade ON pacientes(unidade_saude)")
        
        # Criar tabela de agendamentos
        ddl_agendamentos = """
        CREATE TABLE IF NOT EXISTS agendamentos (
            id TEXT PRIMARY KEY,
            paciente_id TEXT NOT NULL,
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
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamento_paciente ON agendamentos(paciente_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agendamento_data ON agendamentos(data_consulta)")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def testar_conexao(self) -> Dict:
        """Testa a conexão com o banco de dados executando uma consulta simples"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return {'status': 'ok', 'mensagem': 'Conexão estabelecida com sucesso'}
        except Exception as e:
            return {'status': 'erro', 'mensagem': f'Erro na conexão: {str(e)}'}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        # sqlite3.Row não tem método .get(), então precisamos usar try/except ou verificar se a chave existe
        estratificacao_problema = ''
        try:
            # Tentar acessar a coluna estratificacao_problema
            estratificacao_problema = row['estratificacao_problema'] or ''
        except (KeyError, IndexError):
            # Coluna não existe ou não está disponível
            estratificacao_problema = ''
        
        # Verificar se arquivo_origem existe na row
        arquivo_origem = None
        try:
            # Verificar se a coluna existe usando keys()
            if 'arquivo_origem' in row.keys():
                arquivo_origem = row['arquivo_origem']
        except (KeyError, IndexError):
            # Coluna não existe
            arquivo_origem = None
        
        # Verificar se inicio_pre_natal_semanas existe na row
        inicio_pre_natal_semanas = None
        try:
            if 'inicio_pre_natal_semanas' in row.keys():
                inicio_pre_natal_semanas = row['inicio_pre_natal_semanas']
        except (KeyError, IndexError):
            inicio_pre_natal_semanas = None
        
        # Verificar se inicio_pre_natal_observacao existe na row
        inicio_pre_natal_observacao = ''
        try:
            if 'inicio_pre_natal_observacao' in row.keys():
                inicio_pre_natal_observacao = row['inicio_pre_natal_observacao'] or ''
        except (KeyError, IndexError):
            inicio_pre_natal_observacao = ''
        
        # Verificar se proxima_avaliacao existe na row
        proxima_avaliacao = None
        try:
            if 'proxima_avaliacao' in row.keys():
                proxima_avaliacao = row['proxima_avaliacao']
        except (KeyError, IndexError):
            proxima_avaliacao = None
        
        # Verificar se proxima_avaliacao_hora existe na row
        proxima_avaliacao_hora = None
        try:
            if 'proxima_avaliacao_hora' in row.keys():
                proxima_avaliacao_hora = row['proxima_avaliacao_hora']
        except (KeyError, IndexError):
            proxima_avaliacao_hora = None
        
        # Verificar se dum existe na row
        dum = None
        try:
            if 'dum' in row.keys():
                dum = row['dum']
        except (KeyError, IndexError):
            dum = None
        
        # Verificar se dpp existe na row
        dpp = None
        try:
            if 'dpp' in row.keys():
                dpp = row['dpp']
        except (KeyError, IndexError):
            dpp = None
        
        # Verificar se ganhou_kit existe na row
        ganhou_kit = None
        try:
            if 'ganhou_kit' in row.keys():
                ganhou_kit = int_to_bool(row['ganhou_kit'])
        except (KeyError, IndexError):
            ganhou_kit = None
        
        # Verificar se kit_tipo existe na row
        kit_tipo = None
        try:
            if 'kit_tipo' in row.keys():
                kit_tipo = row['kit_tipo']
        except (KeyError, IndexError):
            kit_tipo = None
        
        # Verificar novos campos de histórico reprodutivo
        ja_ganhou_crianca = None
        try:
            if 'ja_ganhou_crianca' in row.keys():
                ja_ganhou_crianca = int_to_bool(row['ja_ganhou_crianca'])
        except (KeyError, IndexError):
            ja_ganhou_crianca = None
        
        data_ganhou_crianca = None
        try:
            if 'data_ganhou_crianca' in row.keys():
                data_ganhou_crianca = row['data_ganhou_crianca']
        except (KeyError, IndexError):
            data_ganhou_crianca = None
        
        quantidade_filhos = None
        try:
            if 'quantidade_filhos' in row.keys():
                quantidade_filhos = row['quantidade_filhos']
        except (KeyError, IndexError):
            quantidade_filhos = None
        
        generos_filhos = None
        try:
            if 'generos_filhos' in row.keys():
                generos_filhos = row['generos_filhos']
        except (KeyError, IndexError):
            generos_filhos = None
        
        metodo_preventivo = None
        try:
            if 'metodo_preventivo' in row.keys():
                metodo_preventivo = row['metodo_preventivo']
        except (KeyError, IndexError):
            metodo_preventivo = None
        
        metodo_preventivo_outros = None
        try:
            if 'metodo_preventivo_outros' in row.keys():
                metodo_preventivo_outros = row['metodo_preventivo_outros']
        except (KeyError, IndexError):
            metodo_preventivo_outros = None
        
        return {
            'id': row['id'],
            'data_salvamento': row['data_salvamento'],
            'identificacao': {
                'nome_gestante': row['nome_gestante'],
                'unidade_saude': row['unidade_saude']
            },
            'avaliacao': {
                'inicio_pre_natal_antes_12s': int_to_bool(row['inicio_pre_natal_antes_12s']),
                'inicio_pre_natal_semanas': inicio_pre_natal_semanas,
                'inicio_pre_natal_observacao': inicio_pre_natal_observacao,
                'consultas_pre_natal': row['consultas_pre_natal'],
                'vacinas_completas': row['vacinas_completas'] or '',
                'plano_parto': int_to_bool(row['plano_parto']),
                'participou_grupos': int_to_bool(row['participou_grupos']),
                'avaliacao_odontologica': int_to_bool(row['avaliacao_odontologica']),
                'estratificacao': int_to_bool(row['estratificacao']),
                'estratificacao_problema': estratificacao_problema,
                'cartao_pre_natal_completo': int_to_bool(row['cartao_pre_natal_completo']),
                'dum': dum,
                'dpp': dpp,
                'ganhou_kit': ganhou_kit,
                'kit_tipo': kit_tipo,
                'proxima_avaliacao': proxima_avaliacao,
                'proxima_avaliacao_hora': proxima_avaliacao_hora,
                'ja_ganhou_crianca': ja_ganhou_crianca,
                'data_ganhou_crianca': data_ganhou_crianca,
                'quantidade_filhos': quantidade_filhos,
                'generos_filhos': generos_filhos,
                'metodo_preventivo': metodo_preventivo,
                'metodo_preventivo_outros': metodo_preventivo_outros
            },
            'arquivo_origem': arquivo_origem
        }

    def gerar_id(self, nome: str, data_salvamento: Optional[str] = None) -> str:
        if not data_salvamento:
            data_salvamento = datetime.now().strftime('%Y%m%d_%H%M%S')
        else:
            data_salvamento = data_salvamento.replace(' ', '_').replace(':', '').replace('-', '')
        nome_formatado = nome.strip().replace(' ', '_')
        return f"{nome_formatado}_{data_salvamento}"

    def inserir_registro(
        self,
        paciente_id: str,
        paciente_data: Dict,
        arquivo_origem: Optional[str] = None,
        data_salvamento: Optional[str] = None
    ) -> Dict:
        if not data_salvamento:
            data_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        identificacao = paciente_data.get('identificacao', {})
        avaliacao = paciente_data.get('avaliacao', {})
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO pacientes (
                id, nome_gestante, unidade_saude, data_salvamento,
                inicio_pre_natal_antes_12s, inicio_pre_natal_semanas, inicio_pre_natal_observacao,
                consultas_pre_natal, vacinas_completas,
                plano_parto, participou_grupos, avaliacao_odontologica,
                estratificacao, estratificacao_problema, cartao_pre_natal_completo, 
                dum, dpp, ganhou_kit, kit_tipo, proxima_avaliacao, proxima_avaliacao_hora,
                ja_ganhou_crianca, data_ganhou_crianca, quantidade_filhos, generos_filhos,
                metodo_preventivo, metodo_preventivo_outros, arquivo_origem
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                paciente_id,
                identificacao.get('nome_gestante', '').strip(),
                identificacao.get('unidade_saude', '').strip(),
                data_salvamento,
                bool_to_int(avaliacao.get('inicio_pre_natal_antes_12s')),
                avaliacao.get('inicio_pre_natal_semanas') if avaliacao.get('inicio_pre_natal_semanas') else None,
                avaliacao.get('inicio_pre_natal_observacao', '').strip() or None,
                avaliacao.get('consultas_pre_natal', 0),
                avaliacao.get('vacinas_completas', ''),
                bool_to_int(avaliacao.get('plano_parto')),
                bool_to_int(avaliacao.get('participou_grupos')),
                bool_to_int(avaliacao.get('avaliacao_odontologica')),
                bool_to_int(avaliacao.get('estratificacao')),
                avaliacao.get('estratificacao_problema', '').strip(),
                bool_to_int(avaliacao.get('cartao_pre_natal_completo')),
                avaliacao.get('dum', '').strip() or None,
                avaliacao.get('dpp', '').strip() or None,
                bool_to_int(avaliacao.get('ganhou_kit')),
                avaliacao.get('kit_tipo', '').strip() or None,
                avaliacao.get('proxima_avaliacao', '').strip() or None,
                avaliacao.get('proxima_avaliacao_hora', '').strip() or None,
                bool_to_int(avaliacao.get('ja_ganhou_crianca')),
                avaliacao.get('data_ganhou_crianca', '').strip() or None,
                avaliacao.get('quantidade_filhos') if avaliacao.get('quantidade_filhos') is not None else None,
                avaliacao.get('generos_filhos', '').strip() or None,
                avaliacao.get('metodo_preventivo', '').strip() or None,
                avaliacao.get('metodo_preventivo_outros', '').strip() or None,
                arquivo_origem
            )
        )
        self.conn.commit()
        return {
            'success': True,
            'message': 'Paciente registrado com sucesso',
            'id': paciente_id
        }

    def adicionar_paciente(self, paciente_data: Dict) -> Dict:
        nome = paciente_data.get('identificacao', {}).get('nome_gestante', '').strip()
        data_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        paciente_id = self.gerar_id(nome, data_salvamento)
        resultado = self.inserir_registro(paciente_id, paciente_data, data_salvamento=data_salvamento)

        # Se foi sucesso e tem próxima avaliação, criar agendamento automaticamente
        if resultado['success']:
            proxima_avaliacao = paciente_data.get('avaliacao', {}).get('proxima_avaliacao')
            proxima_avaliacao_hora = paciente_data.get('avaliacao', {}).get('proxima_avaliacao_hora')

            if proxima_avaliacao:
                # Verificar se já existe agendamento nesta data/hora
                agendamentos_existentes = self.listar_agendamentos(
                    paciente_id=paciente_id,
                    data_inicio=proxima_avaliacao,
                    data_fim=proxima_avaliacao
                )

                # Filtrar por hora se especificada
                ja_existe = False
                if proxima_avaliacao_hora:
                    for agendamento in agendamentos_existentes:
                        if agendamento['hora_consulta'] == proxima_avaliacao_hora:
                            ja_existe = True
                            break
                else:
                    ja_existe = len(agendamentos_existentes) > 0

                if not ja_existe:
                    # Criar agendamento
                    import uuid
                    agendamento_id = str(uuid.uuid4())

                    agendamento_resultado = self.criar_agendamento(
                        agendamento_id=agendamento_id,
                        paciente_id=paciente_id,
                        data_consulta=proxima_avaliacao,
                        hora_consulta=proxima_avaliacao_hora or '08:00',  # Hora padrão se não especificada
                        tipo_consulta='consulta_pre_natal',
                        observacoes='Agendamento automático da próxima avaliação',
                        status='agendado'
                    )

                    if not agendamento_resultado['success']:
                        print(f"Aviso: Não foi possível criar agendamento automático: {agendamento_resultado['message']}")

        return resultado

    def buscar_paciente(self, paciente_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def buscar_pacientes(self, filtro: Optional[Dict] = None) -> List[Dict]:
        query = "SELECT * FROM pacientes"
        params: Tuple[str, ...] = ()
        if filtro:
            clauses = []
            if 'nome' in filtro:
                clauses.append("LOWER(nome_gestante) LIKE ?")
                params += (f"%{filtro['nome'].lower()}%",)
            if 'unidade_saude' in filtro:
                clauses.append("LOWER(unidade_saude) LIKE ?")
                params += (f"%{filtro['unidade_saude'].lower()}%",)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def atualizar_paciente(self, paciente_id: str, paciente_data: Dict) -> Dict:
        if not self.buscar_paciente(paciente_id):
            return {'success': False, 'message': 'Paciente não encontrado'}

        # Buscar dados antigos para comparar
        paciente_antigo = self.buscar_paciente(paciente_id)

        resultado = self.inserir_registro(paciente_id, paciente_data)

        # Se foi sucesso, gerenciar agendamento da próxima avaliação
        if resultado['success']:
            self._gerenciar_agendamento_proxima_avaliacao(paciente_id, paciente_data, paciente_antigo)

        return resultado

    def _gerenciar_agendamento_proxima_avaliacao(self, paciente_id: str, paciente_data: Dict, paciente_antigo: Dict = None):
        """Gerencia agendamento automático da próxima avaliação"""
        proxima_avaliacao = paciente_data.get('avaliacao', {}).get('proxima_avaliacao')
        proxima_avaliacao_hora = paciente_data.get('avaliacao', {}).get('proxima_avaliacao_hora')

        # Verificar se mudou a data/hora da próxima avaliação
        mudou_data = False
        if paciente_antigo:
            antiga_data = paciente_antigo.get('avaliacao', {}).get('proxima_avaliacao')
            antiga_hora = paciente_antigo.get('avaliacao', {}).get('proxima_avaliacao_hora')
            mudou_data = (proxima_avaliacao != antiga_data) or (proxima_avaliacao_hora != antiga_hora)

        if proxima_avaliacao and (not paciente_antigo or mudou_data):
            # Verificar se já existe agendamento nesta data/hora
            agendamentos_existentes = self.listar_agendamentos(
                paciente_id=paciente_id,
                data_inicio=proxima_avaliacao,
                data_fim=proxima_avaliacao
            )

            # Filtrar por hora se especificada
            agendamento_existente = None
            if proxima_avaliacao_hora:
                for agendamento in agendamentos_existentes:
                    if agendamento['hora_consulta'] == proxima_avaliacao_hora:
                        agendamento_existente = agendamento
                        break
            elif agendamentos_existentes:
                agendamento_existente = agendamentos_existentes[0]

            if agendamento_existente:
                # Atualizar agendamento existente
                self.atualizar_agendamento(
                    agendamento_id=agendamento_existente['id'],
                    data_consulta=proxima_avaliacao,
                    hora_consulta=proxima_avaliacao_hora,
                    tipo_consulta='consulta_pre_natal',
                    observacoes='Agendamento automático da próxima avaliação (atualizado)',
                    status='agendado'
                )
            else:
                # Criar novo agendamento
                import uuid
                agendamento_id = str(uuid.uuid4())

                agendamento_resultado = self.criar_agendamento(
                    agendamento_id=agendamento_id,
                    paciente_id=paciente_id,
                    data_consulta=proxima_avaliacao,
                    hora_consulta=proxima_avaliacao_hora or '08:00',  # Hora padrão se não especificada
                    tipo_consulta='consulta_pre_natal',
                    observacoes='Agendamento automático da próxima avaliação',
                    status='agendado'
                )

                if not agendamento_resultado['success']:
                    print(f"Aviso: Não foi possível criar agendamento automático: {agendamento_resultado['message']}")

        elif not proxima_avaliacao and paciente_antigo:
            # Removeu a próxima avaliação - poderia cancelar agendamentos existentes
            # Mas por enquanto vamos deixar como está para não cancelar agendamentos manuais
            pass

    def obter_todos_pacientes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes ORDER BY data_salvamento DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def obter_unidades_saude_unicas(self) -> List[str]:
        """Retorna lista de unidades de saúde únicas"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT unidade_saude FROM pacientes WHERE unidade_saude IS NOT NULL AND unidade_saude != '' ORDER BY unidade_saude")
        rows = cursor.fetchall()
        return [row['unidade_saude'] for row in rows if row['unidade_saude']]

    def obter_estatisticas(self, unidade_saude: Optional[str] = None) -> Dict:
        cursor = self.conn.cursor()
        if unidade_saude:
            cursor.execute("SELECT * FROM pacientes WHERE LOWER(unidade_saude) = LOWER(?)", (unidade_saude,))
        else:
            cursor.execute("SELECT * FROM pacientes")
        rows = cursor.fetchall()
        stats = {
            'total_pacientes': len(rows),
            'ultima_atualizacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
            'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
            'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
            'plano_parto': {'sim': 0, 'nao': 0},
            'participou_grupos': {'sim': 0, 'nao': 0}
        }
        for row in rows:
            inicio = row['inicio_pre_natal_antes_12s']
            stats['inicio_pre_natal_antes_12s']['sim'] += 1 if inicio == 1 else 0
            stats['inicio_pre_natal_antes_12s']['nao'] += 1 if inicio == 0 else 0
            num_consultas = row['consultas_pre_natal'] or 0
            stats['consultas_pre_natal']['mais_6'] += 1 if num_consultas >= 6 else 0
            stats['consultas_pre_natal']['ate_6'] += 1 if num_consultas < 6 else 0
            vacinas = (row['vacinas_completas'] or '').lower()
            if 'completa' in vacinas:
                stats['vacinas_completas']['completa'] += 1
            elif 'incompleta' in vacinas:
                stats['vacinas_completas']['incompleta'] += 1
            else:
                stats['vacinas_completas']['nao_avaliado'] += 1
            stats['plano_parto']['sim'] += 1 if row['plano_parto'] == 1 else 0
            stats['plano_parto']['nao'] += 1 if row['plano_parto'] == 0 else 0
            stats['participou_grupos']['sim'] += 1 if row['participou_grupos'] == 1 else 0
            stats['participou_grupos']['nao'] += 1 if row['participou_grupos'] == 0 else 0
        return stats

    def limpar_todos_dados(self) -> None:
        self.conn.execute("DELETE FROM pacientes")
        self.conn.commit()
        return {'success': True, 'message': 'Todos os dados foram excluídos com sucesso'}

    def deletar_paciente(self, paciente_id: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            return {'success': False, 'message': 'Paciente não encontrado'}
        return {'success': True, 'message': 'Paciente deletado com sucesso'}

    def criar_backup(self) -> Dict:
        pacientes = self.obter_todos_pacientes()
        return {
            'success': True,
            'backup': pacientes,
            'data_backup': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def obter_estatisticas_temporais(self, filtro: str) -> Dict:
        """Retorna estatísticas temporais agrupadas por data para um indicador específico"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes ORDER BY data_salvamento ASC")
        rows = cursor.fetchall()
        
        # Agrupar por data
        dados_por_data = {}
        
        for row in rows:
            data_salvamento = row['data_salvamento']
            if not data_salvamento:
                continue
            
            # Extrair apenas a data (sem hora)
            data = data_salvamento.split(' ')[0] if ' ' in data_salvamento else data_salvamento
            
            if data not in dados_por_data:
                dados_por_data[data] = {
                    'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
                    'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
                    'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
                    'plano_parto': {'sim': 0, 'nao': 0},
                    'participou_grupos': {'sim': 0, 'nao': 0}
                }
            
            stats = dados_por_data[data]
            
            # Processar cada indicador
            inicio = row['inicio_pre_natal_antes_12s']
            stats['inicio_pre_natal_antes_12s']['sim'] += 1 if inicio == 1 else 0
            stats['inicio_pre_natal_antes_12s']['nao'] += 1 if inicio == 0 else 0
            
            num_consultas = row['consultas_pre_natal'] or 0
            stats['consultas_pre_natal']['mais_6'] += 1 if num_consultas >= 6 else 0
            stats['consultas_pre_natal']['ate_6'] += 1 if num_consultas < 6 else 0
            
            vacinas = (row['vacinas_completas'] or '').lower()
            if 'completa' in vacinas:
                stats['vacinas_completas']['completa'] += 1
            elif 'incompleta' in vacinas:
                stats['vacinas_completas']['incompleta'] += 1
            else:
                stats['vacinas_completas']['nao_avaliado'] += 1
            
            stats['plano_parto']['sim'] += 1 if row['plano_parto'] == 1 else 0
            stats['plano_parto']['nao'] += 1 if row['plano_parto'] == 0 else 0
            stats['participou_grupos']['sim'] += 1 if row['participou_grupos'] == 1 else 0
            stats['participou_grupos']['nao'] += 1 if row['participou_grupos'] == 0 else 0
        
        # Preparar resposta no formato esperado
        datas = sorted(dados_por_data.keys())
        valores = {}
        
        for data in datas:
            stats = dados_por_data[data]
            valores[data] = {}
            
            if filtro == 'inicio_pre_natal_antes_12s':
                valores[data]['Sim'] = stats['inicio_pre_natal_antes_12s']['sim']
                valores[data]['Não'] = stats['inicio_pre_natal_antes_12s']['nao']
            elif filtro == 'consultas_pre_natal':
                valores[data]['≥ 6 consultas'] = stats['consultas_pre_natal']['mais_6']
                valores[data]['< 6 consultas'] = stats['consultas_pre_natal']['ate_6']
            elif filtro == 'vacinas_completas':
                valores[data]['Completo'] = stats['vacinas_completas']['completa']
                valores[data]['Incompleto'] = stats['vacinas_completas']['incompleta']
                valores[data]['Não avaliado'] = stats['vacinas_completas']['nao_avaliado']
            elif filtro == 'plano_parto':
                valores[data]['Sim'] = stats['plano_parto']['sim']
                valores[data]['Não'] = stats['plano_parto']['nao']
            elif filtro == 'participou_grupos':
                valores[data]['Participou'] = stats['participou_grupos']['sim']
                valores[data]['Não participou'] = stats['participou_grupos']['nao']
        
        return {
            'datas': datas,
            'valores': valores
        }

    def restaurar_backup(self, backup_data: List[Dict]) -> Dict:
        if not isinstance(backup_data, list):
            return {'success': False, 'message': 'Estrutura do backup inválida'}
        self.conn.execute("DELETE FROM pacientes")
        self.conn.commit()
        inseridos = 0
        for registro in backup_data:
            nome = registro.get('identificacao', {}).get('nome_gestante', '').strip()
            if not nome:
                continue
            paciente_id = registro.get('id') or self.gerar_id(nome)
            data_salvamento = registro.get('data_salvamento', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            resultado = self.inserir_registro(
                paciente_id,
                registro,
                arquivo_origem=registro.get('arquivo_origem'),
                data_salvamento=data_salvamento
            )
            if resultado['success']:
                inseridos += 1
            return {
            'success': True,
            'message': f'Backup restaurado com sucesso ({inseridos} registros)',
            'total_pacientes': inseridos
        }

    # Métodos para agendamentos
    def criar_agendamento(self, agendamento_id: str, paciente_id: str, data_consulta: str, 
                          hora_consulta: str, tipo_consulta: str = None, observacoes: str = None, 
                          status: str = 'agendado', data_criacao: str = None, data_atualizacao: str = None) -> Dict:
        """Cria um novo agendamento"""
        try:
            if not data_criacao:
                data_criacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not data_atualizacao:
                data_atualizacao = data_criacao
            self.conn.execute("""
                INSERT INTO agendamentos 
                (id, paciente_id, data_consulta, hora_consulta, tipo_consulta, observacoes, status, data_criacao, data_atualizacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (agendamento_id, paciente_id, data_consulta, hora_consulta, tipo_consulta, observacoes, status, data_criacao, data_atualizacao))
            self.conn.commit()
            return {'success': True, 'message': 'Agendamento criado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao criar agendamento: {str(e)}'}

    def listar_agendamentos(self, paciente_id: str = None, data_inicio: str = None, 
                           data_fim: str = None, status: str = None) -> List[Dict]:
        """Lista agendamentos com filtros opcionais"""
        try:
            query = """
                SELECT a.*, p.nome_gestante, p.unidade_saude
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                WHERE 1=1
            """
            params = []
            
            if paciente_id:
                query += " AND a.paciente_id = ?"
                params.append(paciente_id)
            
            if data_inicio:
                query += " AND a.data_consulta >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND a.data_consulta <= ?"
                params.append(data_fim)
            
            if status:
                query += " AND a.status = ?"
                params.append(status)
            
            query += " ORDER BY a.data_consulta ASC, a.hora_consulta ASC"
            
            cursor = self.conn.execute(query, params)
            rows = cursor.fetchall()
            
            agendamentos = []
            for row in rows:
                agendamento = {
                    'id': row['id'],
                    'paciente_id': row['paciente_id'],
                    'nome_gestante': row['nome_gestante'],
                    'unidade_saude': row['unidade_saude'],
                    'data_consulta': row['data_consulta'],
                    'hora_consulta': row['hora_consulta'],
                    'tipo_consulta': row['tipo_consulta'],
                    'observacoes': row['observacoes'],
                    'status': row['status'],
                    'data_criacao': row['data_criacao'],
                    'data_atualizacao': row['data_atualizacao']
                }
                agendamentos.append(agendamento)
            
            return agendamentos
        except Exception as e:
            return []

    def obter_agendamento(self, agendamento_id: str) -> Optional[Dict]:
        """Obtém um agendamento específico"""
        try:
            cursor = self.conn.execute("""
                SELECT a.*, p.nome_gestante, p.unidade_saude
                FROM agendamentos a
                LEFT JOIN pacientes p ON a.paciente_id = p.id
                WHERE a.id = ?
            """, (agendamento_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'paciente_id': row['paciente_id'],
                    'nome_gestante': row['nome_gestante'],
                    'unidade_saude': row['unidade_saude'],
                    'data_consulta': row['data_consulta'],
                    'hora_consulta': row['hora_consulta'],
                    'tipo_consulta': row['tipo_consulta'],
                    'observacoes': row['observacoes'],
                    'status': row['status'],
                    'data_criacao': row['data_criacao'],
                    'data_atualizacao': row['data_atualizacao']
                }
            return None
        except Exception as e:
            return None

    def atualizar_agendamento(self, agendamento_id: str, paciente_id: str = None, data_consulta: str = None,
                              hora_consulta: str = None, tipo_consulta: str = None,
                              observacoes: str = None, status: str = None, data_atualizacao: str = None) -> Dict:
        """Atualiza um agendamento existente"""
        try:
            if not data_atualizacao:
                data_atualizacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updates = []
            params = []
            
            if paciente_id is not None:
                updates.append("paciente_id = ?")
                params.append(paciente_id)
            
            if data_consulta is not None:
                updates.append("data_consulta = ?")
                params.append(data_consulta)
            
            if hora_consulta is not None:
                updates.append("hora_consulta = ?")
                params.append(hora_consulta)
            
            if tipo_consulta is not None:
                updates.append("tipo_consulta = ?")
                params.append(tipo_consulta)
            
            if observacoes is not None:
                updates.append("observacoes = ?")
                params.append(observacoes)
            
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            
            if not updates:
                return {'success': False, 'message': 'Nenhum campo para atualizar'}
            
            updates.append("data_atualizacao = ?")
            params.append(data_atualizacao)
            params.append(agendamento_id)
            
            query = f"UPDATE agendamentos SET {', '.join(updates)} WHERE id = ?"
            self.conn.execute(query, params)
            self.conn.commit()
            
            return {'success': True, 'message': 'Agendamento atualizado com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao atualizar agendamento: {str(e)}'}

    def excluir_agendamento(self, agendamento_id: str) -> Dict:
        """Exclui um agendamento"""
        try:
            self.conn.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
            self.conn.commit()
            return {'success': True, 'message': 'Agendamento excluído com sucesso'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao excluir agendamento: {str(e)}'}

    def comparar_com_banco_remoto(self, pacientes_remotos: List[Dict]) -> Dict:
        """
        Compara o banco local com um banco remoto e detecta:
        - Pacientes que existem localmente mas não no remoto (removidos no remoto)
        - Pacientes que existem no remoto mas não localmente (novos no remoto)
        - Pacientes que existem em ambos (para atualização)
        """
        pacientes_locais = self.obter_todos_pacientes()
        pacientes_locais_ids = {p['id'] for p in pacientes_locais}
        pacientes_remotos_ids = {p['id'] for p in pacientes_remotos}
        
        # Pacientes que existem localmente mas não no remoto (removidos no remoto)
        pacientes_removidos_no_remoto = [
            p for p in pacientes_locais 
            if p['id'] not in pacientes_remotos_ids
        ]
        
        # Pacientes que existem no remoto mas não localmente (novos)
        pacientes_novos = [
            p for p in pacientes_remotos 
            if p['id'] not in pacientes_locais_ids
        ]
        
        # Pacientes que existem em ambos (podem precisar atualização)
        pacientes_em_ambos = [
            p for p in pacientes_remotos 
            if p['id'] in pacientes_locais_ids
        ]
        
        return {
            'pacientes_removidos_no_remoto': pacientes_removidos_no_remoto,
            'pacientes_novos': pacientes_novos,
            'pacientes_em_ambos': pacientes_em_ambos,
            'total_local': len(pacientes_locais),
            'total_remoto': len(pacientes_remotos)
        }

    def remover_pacientes(self, paciente_ids: List[str]) -> Dict:
        """Remove múltiplos pacientes por seus IDs"""
        try:
            if not paciente_ids:
                return {'success': False, 'message': 'Nenhum ID fornecido'}
            
            cursor = self.conn.cursor()
            placeholders = ','.join(['?'] * len(paciente_ids))
            cursor.execute(f"DELETE FROM pacientes WHERE id IN ({placeholders})", paciente_ids)
            self.conn.commit()
            
            removidos = cursor.rowcount
            return {
                'success': True, 
                'message': f'{removidos} paciente(s) removido(s) com sucesso',
                'removidos': removidos
            }
        except Exception as e:
            return {'success': False, 'message': f'Erro ao remover pacientes: {str(e)}'}


# Instância global do banco de dados
db = Database()
