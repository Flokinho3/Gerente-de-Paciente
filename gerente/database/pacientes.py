from datetime import datetime
from typing import Optional, Dict, List, Tuple
from .models import bool_to_int

class PacienteMixin:
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
        data_salvamento: Optional[str] = None,
        pc_id: Optional[str] = None,
        ultima_modificacao: Optional[str] = None,
        versao: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict:
        if not data_salvamento:
            data_salvamento = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not ultima_modificacao:
            ultima_modificacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not pc_id:
            pc_id = self.pc_id
        if versao is None:
            versao = 1
        if not status:
            status = 'ativo'
        
        identificacao = paciente_data.get('identificacao', {})
        if not isinstance(identificacao, dict):
            identificacao = {}
        
        avaliacao = paciente_data.get('avaliacao', {})
        if not isinstance(avaliacao, dict):
            avaliacao = {}

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO pacientes (
                id, nome_gestante, unidade_saude, data_salvamento,
                inicio_pre_natal_antes_12s, inicio_pre_natal_semanas, inicio_pre_natal_observacao,
                consultas_pre_natal, vacinas_completas,
                plano_parto, participou_grupos, avaliacao_odontologica,
                estratificacao, estratificacao_problema, cartao_pre_natal_completo,
                possui_bolsa_familia, tem_vacina_covid, plano_parto_entregue_por_unidade,
                dum, dpp, ganhou_kit, kit_tipo, proxima_avaliacao, proxima_avaliacao_hora,
                ja_ganhou_crianca, data_ganhou_crianca, quantidade_filhos, generos_filhos,
                metodo_preventivo, metodo_preventivo_outros, arquivo_origem,
                pc_id, ultima_modificacao, versao, status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                paciente_id,
                (identificacao.get('nome_gestante') or '').strip(),
                (identificacao.get('unidade_saude') or '').strip(),
                data_salvamento,
                bool_to_int(avaliacao.get('inicio_pre_natal_antes_12s')),
                avaliacao.get('inicio_pre_natal_semanas') if avaliacao.get('inicio_pre_natal_semanas') else None,
                (avaliacao.get('inicio_pre_natal_observacao') or '').strip() or None,
                int(avaliacao.get('consultas_pre_natal', 0)) if str(avaliacao.get('consultas_pre_natal', '')).isdigit() else 0,
                (avaliacao.get('vacinas_completas') or '') or None,
                bool_to_int(avaliacao.get('plano_parto')),
                bool_to_int(avaliacao.get('participou_grupos')),
                bool_to_int(avaliacao.get('avaliacao_odontologica')),
                bool_to_int(avaliacao.get('estratificacao')),
                (avaliacao.get('estratificacao_problema') or '').strip(),
                bool_to_int(avaliacao.get('cartao_pre_natal_completo')),
                bool_to_int(avaliacao.get('possui_bolsa_familia')),
                bool_to_int(avaliacao.get('tem_vacina_covid')),
                (avaliacao.get('plano_parto_entregue_por_unidade') or '').strip() or None,
                (avaliacao.get('dum') or '').strip() or None,
                (avaliacao.get('dpp') or '').strip() or None,
                bool_to_int(avaliacao.get('ganhou_kit')),
                (avaliacao.get('kit_tipo') or '').strip() or None,
                (avaliacao.get('proxima_avaliacao') or '').strip() or None,
                (avaliacao.get('proxima_avaliacao_hora') or '').strip() or None,
                bool_to_int(avaliacao.get('ja_ganhou_crianca')),
                (avaliacao.get('data_ganhou_crianca') or '').strip() or None,
                int(avaliacao.get('quantidade_filhos')) if str(avaliacao.get('quantidade_filhos', '')).isdigit() else None,
                (avaliacao.get('generos_filhos') or '').strip() or None,
                (avaliacao.get('metodo_preventivo') or '').strip() or None,
                (avaliacao.get('metodo_preventivo_outros') or '').strip() or None,
                arquivo_origem,
                pc_id,
                ultima_modificacao,
                versao,
                status
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

        if resultado['success']:
            proxima_avaliacao = (paciente_data.get('avaliacao', {}).get('proxima_avaliacao') or '').strip()
            proxima_avaliacao_hora = (paciente_data.get('avaliacao', {}).get('proxima_avaliacao_hora') or '').strip()
            
            # Verificar se paciente pode ser agendado (não pode se tem estratificação ou já ganhou)
            tem_estratificacao = paciente_data.get('avaliacao', {}).get('estratificacao') == True
            tem_ja_ganhou = paciente_data.get('avaliacao', {}).get('ja_ganhou_crianca') == True
            pode_agendar = not (tem_estratificacao or tem_ja_ganhou)

            if proxima_avaliacao and pode_agendar:
                try:
                    agendamentos_existentes = self.listar_agendamentos(
                        paciente_id=paciente_id,
                        data_inicio=proxima_avaliacao,
                        data_fim=proxima_avaliacao
                    )

                    ja_existe = False
                    if proxima_avaliacao_hora:
                        for agendamento in agendamentos_existentes:
                            if agendamento['hora_consulta'] == proxima_avaliacao_hora:
                                ja_existe = True
                                break
                    else:
                        ja_existe = len(agendamentos_existentes) > 0

                    if not ja_existe:
                        import uuid
                        agendamento_id = str(uuid.uuid4())
                        self.criar_agendamento(
                            agendamento_id=agendamento_id,
                            paciente_id=paciente_id,
                            data_consulta=proxima_avaliacao,
                            hora_consulta=proxima_avaliacao_hora or '08:00',
                            tipo_consulta='consulta_pre_natal',
                            observacoes='Agendamento automático da próxima avaliação',
                            status='agendado'
                        )
                except Exception as e:
                    # Não falhar o salvamento do paciente se o agendamento falhar
                    print(f"Erro ao criar agendamento automático: {e}")
        return resultado

    def buscar_paciente(self, paciente_id: str) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def buscar_pacientes(self, filtro: Optional[Dict] = None, incluir_removidos: bool = False) -> List[Dict]:
        query = "SELECT * FROM pacientes"
        params: Tuple[str, ...] = ()
        clauses = []
        
        if not incluir_removidos:
            clauses.append("(status IS NULL OR status != 'removido')")
        
        if filtro:
            if 'nome' in filtro:
                clauses.append("LOWER(nome_gestante) LIKE ?")
                params += (f"%{filtro['nome'].lower()}%",)
            if 'unidade_saude' in filtro:
                clauses.append("LOWER(unidade_saude) LIKE ?")
                params += (f"%{filtro['unidade_saude'].lower()}%",)
            if 'status' in filtro:
                clauses.append("status = ?")
                params += (filtro['status'],)
        
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def atualizar_paciente(self, paciente_id: str, paciente_data: Dict) -> Dict:
        paciente_existente = self.buscar_paciente(paciente_id)
        if not paciente_existente:
            return {'success': False, 'message': 'Paciente não encontrado'}

        versao_atual = paciente_existente.get('versao', 1)
        nova_versao = versao_atual + 1
        status_atual = paciente_existente.get('status', 'ativo')
        novo_status = status_atual if status_atual == 'conflito' else 'ativo'
        
        pc_id = paciente_data.get('pc_id') or self.pc_id
        ultima_modificacao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        resultado = self.inserir_registro(
            paciente_id, 
            paciente_data,
            pc_id=pc_id,
            ultima_modificacao=ultima_modificacao,
            versao=nova_versao,
            status=novo_status
        )

        if resultado['success']:
            self._gerenciar_agendamento_proxima_avaliacao(paciente_id, paciente_data, paciente_existente)

        return resultado

    def _gerenciar_agendamento_proxima_avaliacao(self, paciente_id: str, paciente_data: Dict, paciente_antigo: Dict = None):
        proxima_avaliacao = (paciente_data.get('avaliacao', {}).get('proxima_avaliacao') or '').strip()
        proxima_avaliacao_hora = (paciente_data.get('avaliacao', {}).get('proxima_avaliacao_hora') or '').strip()

        # Verificar se paciente pode ser agendado (não pode se tem estratificação ou já ganhou)
        tem_estratificacao = paciente_data.get('avaliacao', {}).get('estratificacao') == True
        tem_ja_ganhou = paciente_data.get('avaliacao', {}).get('ja_ganhou_crianca') == True
        pode_agendar = not (tem_estratificacao or tem_ja_ganhou)
        
        # Se não pode agendar, remover agendamentos existentes se houver
        if not pode_agendar:
            try:
                agendamentos_existentes = self.listar_agendamentos(paciente_id=paciente_id)
                for agendamento in agendamentos_existentes:
                    if agendamento['status'] == 'agendado':
                        self.atualizar_agendamento(
                            agendamento_id=agendamento['id'],
                            status='cancelado',
                            observacoes='Agendamento cancelado: paciente com risco ou já teve filho'
                        )
            except Exception as e:
                print(f"Erro ao cancelar agendamentos: {e}")
            return

        mudou_data = False
        if paciente_antigo:
            antiga_data = (paciente_antigo.get('avaliacao', {}).get('proxima_avaliacao') or '').strip()
            antiga_hora = (paciente_antigo.get('avaliacao', {}).get('proxima_avaliacao_hora') or '').strip()
            mudou_data = (proxima_avaliacao != antiga_data) or (proxima_avaliacao_hora != antiga_hora)

        if proxima_avaliacao and (not paciente_antigo or mudou_data):
            try:
                agendamentos_existentes = self.listar_agendamentos(
                    paciente_id=paciente_id,
                    data_inicio=proxima_avaliacao,
                    data_fim=proxima_avaliacao
                )

                agendamento_existente = None
                if proxima_avaliacao_hora:
                    for agendamento in agendamentos_existentes:
                        if agendamento['hora_consulta'] == proxima_avaliacao_hora:
                            agendamento_existente = agendamento
                            break
                elif agendamentos_existentes:
                    agendamento_existente = agendamentos_existentes[0]

                if agendamento_existente:
                    self.atualizar_agendamento(
                        agendamento_id=agendamento_existente['id'],
                        data_consulta=proxima_avaliacao,
                        hora_consulta=proxima_avaliacao_hora,
                        tipo_consulta='consulta_pre_natal',
                        observacoes='Agendamento automático da próxima avaliação (atualizado)',
                        status='agendado'
                    )
                else:
                    import uuid
                    agendamento_id = str(uuid.uuid4())
                    self.criar_agendamento(
                        agendamento_id=agendamento_id,
                        paciente_id=paciente_id,
                        data_consulta=proxima_avaliacao,
                        hora_consulta=proxima_avaliacao_hora or '08:00',
                        tipo_consulta='consulta_pre_natal',
                        observacoes='Agendamento automático da próxima avaliação',
                        status='agendado'
                    )
            except Exception as e:
                print(f"Erro ao gerenciar agendamento automático: {e}")

    def obter_todos_pacientes(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes ORDER BY data_salvamento DESC")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def obter_unidades_saude_unicas(self) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT unidade_saude FROM pacientes WHERE unidade_saude IS NOT NULL AND unidade_saude != '' ORDER BY unidade_saude")
        rows = cursor.fetchall()
        return [row['unidade_saude'] for row in rows if row['unidade_saude']]

    def deletar_paciente(self, paciente_id: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
        self.conn.commit()
        if cursor.rowcount == 0:
            return {'success': False, 'message': 'Paciente não encontrado'}
        return {'success': True, 'message': 'Paciente deletado com sucesso'}

    def remover_paciente_soft(self, paciente_id: str) -> Dict:
        try:
            paciente_existente = self.buscar_paciente(paciente_id)
            if not paciente_existente:
                return {'success': False, 'message': 'Paciente não encontrado'}
            
            removido_em = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE pacientes 
                SET status = 'removido', removido_em = ?, removido_por = ?,
                    ultima_modificacao = ?, versao = versao + 1
                WHERE id = ?
            """, (removido_em, self.pc_id, removido_em, paciente_id))
            self.conn.commit()
            return {'success': True, 'message': 'Paciente marcado como removido'}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao remover paciente: {str(e)}'}

    def remover_pacientes(self, paciente_ids: List[str]) -> Dict:
        try:
            if not paciente_ids:
                return {'success': False, 'message': 'Nenhum ID fornecido'}
            cursor = self.conn.cursor()
            placeholders = ','.join(['?'] * len(paciente_ids))
            cursor.execute(f"DELETE FROM pacientes WHERE id IN ({placeholders})", paciente_ids)
            self.conn.commit()
            return {'success': True, 'message': f'{cursor.rowcount} paciente(s) removido(s) com sucesso', 'removidos': cursor.rowcount}
        except Exception as e:
            return {'success': False, 'message': f'Erro ao remover pacientes: {str(e)}'}
