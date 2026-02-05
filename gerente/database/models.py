import sqlite3
from typing import Optional, Dict, List, Any

def bool_to_int(value: Optional[bool]) -> int:
    return 1 if value else 0

def int_to_bool(value: Optional[int]) -> bool:
    return bool(value)

class ModelsMixin:
    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        # Helper to safely get value from row keys
        def get_val(key: str, default: Any = None) -> Any:
            try:
                if key in row.keys():
                    return row[key]
            except (KeyError, IndexError):
                pass
            return default

        estratificacao_problema = get_val('estratificacao_problema', '') or ''
        arquivo_origem = get_val('arquivo_origem')
        inicio_pre_natal_semanas = get_val('inicio_pre_natal_semanas')
        inicio_pre_natal_observacao = get_val('inicio_pre_natal_observacao', '') or ''
        proxima_avaliacao = get_val('proxima_avaliacao')
        proxima_avaliacao_hora = get_val('proxima_avaliacao_hora')
        dum = get_val('dum')
        dpp = get_val('dpp')
        ganhou_kit = int_to_bool(get_val('ganhou_kit')) if get_val('ganhou_kit') is not None else None
        kit_tipo = get_val('kit_tipo')
        ja_ganhou_crianca = int_to_bool(get_val('ja_ganhou_crianca')) if get_val('ja_ganhou_crianca') is not None else None
        data_ganhou_crianca = get_val('data_ganhou_crianca')
        quantidade_filhos = get_val('quantidade_filhos')
        generos_filhos = get_val('generos_filhos')
        metodo_preventivo = get_val('metodo_preventivo')
        metodo_preventivo_outros = get_val('metodo_preventivo_outros')

        result = {
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
                'possui_bolsa_familia': int_to_bool(get_val('possui_bolsa_familia')) if get_val('possui_bolsa_familia') is not None else None,
                'tem_vacina_covid': int_to_bool(get_val('tem_vacina_covid')) if get_val('tem_vacina_covid') is not None else None,
                'plano_parto_entregue_por_unidade': get_val('plano_parto_entregue_por_unidade'),
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
        
        # Adicionar campos de sincronização se existirem
        sync_fields = ['pc_id', 'ultima_modificacao', 'versao', 'status', 'removido_em', 'removido_por']
        for field in sync_fields:
            val = get_val(field)
            if val is not None:
                result[field] = val
        
        return result

    def _normalizar_valor_comparacao(self, valor) -> Any:
        """Normaliza valores para comparação consistente."""
        if valor is None:
            return None
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, int):
            return valor
        if isinstance(valor, float):
            return int(valor) if valor == int(valor) else valor
        if isinstance(valor, str):
            # Normalizar strings: strip e converter vazio/"None"/"null"/"NULL" para None
            valor_strip = valor.strip()
            if not valor_strip or valor_strip.lower() in ('none', 'null', 'nan'):
                return None
            # Tentar converter para int ou float
            try:
                if '.' in valor_strip:
                    f = float(valor_strip)
                    return int(f) if f == int(f) else f
                return int(valor_strip)
            except (ValueError, TypeError):
                pass
            return valor_strip
        return valor

    def _comparar_registros_detalhado(self, db_record: Dict, backup_record: Dict) -> List[Dict]:
        """
        Compara dois registros de paciente campo por campo.
        """
        diferencas = []
        
        campos_comparacao = [
            ('nome_gestante', ['identificacao', 'nome_gestante']),
            ('unidade_saude', ['identificacao', 'unidade_saude']),
            ('inicio_pre_natal_antes_12s', ['avaliacao', 'inicio_pre_natal_antes_12s']),
            ('inicio_pre_natal_semanas', ['avaliacao', 'inicio_pre_natal_semanas']),
            ('inicio_pre_natal_observacao', ['avaliacao', 'inicio_pre_natal_observacao']),
            ('consultas_pre_natal', ['avaliacao', 'consultas_pre_natal']),
            ('vacinas_completas', ['avaliacao', 'vacinas_completas']),
            ('plano_parto', ['avaliacao', 'plano_parto']),
            ('participou_grupos', ['avaliacao', 'participou_grupos']),
            ('avaliacao_odontologica', ['avaliacao', 'avaliacao_odontologica']),
            ('estratificacao', ['avaliacao', 'estratificacao']),
            ('estratificacao_problema', ['avaliacao', 'estratificacao_problema']),
            ('cartao_pre_natal_completo', ['avaliacao', 'cartao_pre_natal_completo']),
            ('possui_bolsa_familia', ['avaliacao', 'possui_bolsa_familia']),
            ('tem_vacina_covid', ['avaliacao', 'tem_vacina_covid']),
            ('plano_parto_entregue_por_unidade', ['avaliacao', 'plano_parto_entregue_por_unidade']),
            ('dum', ['avaliacao', 'dum']),
            ('dpp', ['avaliacao', 'dpp']),
            ('ganhou_kit', ['avaliacao', 'ganhou_kit']),
            ('kit_tipo', ['avaliacao', 'kit_tipo']),
            ('proxima_avaliacao', ['avaliacao', 'proxima_avaliacao']),
            ('proxima_avaliacao_hora', ['avaliacao', 'proxima_avaliacao_hora']),
            ('ja_ganhou_crianca', ['avaliacao', 'ja_ganhou_crianca']),
            ('data_ganhou_crianca', ['avaliacao', 'data_ganhou_crianca']),
            ('quantidade_filhos', ['avaliacao', 'quantidade_filhos']),
            ('generos_filhos', ['avaliacao', 'generos_filhos']),
            ('metodo_preventivo', ['avaliacao', 'metodo_preventivo']),
            ('metodo_preventivo_outros', ['avaliacao', 'metodo_preventivo_outros']),
            ('data_salvamento', ['data_salvamento']),
            ('arquivo_origem', ['arquivo_origem']),
            ('pc_id', ['pc_id']),
            ('ultima_modificacao', ['ultima_modificacao']),
            ('versao', ['versao']),
            ('status', ['status']),
        ]
        
        for campo_nome, campo_path in campos_comparacao:
            # Obter valor do DB
            valor_db = db_record
            for key in campo_path:
                if isinstance(valor_db, dict) and key in valor_db:
                    valor_db = valor_db[key]
                else:
                    valor_db = None
                    break
            
            # Obter valor do Backup
            valor_backup = backup_record
            for key in campo_path:
                if isinstance(valor_backup, dict) and key in valor_backup:
                    valor_backup = valor_backup[key]
                else:
                    valor_backup = None
                    break
            
            valor_db_normalizado = self._normalizar_valor_comparacao(valor_db)
            valor_backup_normalizado = self._normalizar_valor_comparacao(valor_backup)
            
            if valor_db_normalizado != valor_backup_normalizado:
                diferencas.append({
                    'campo': campo_nome,
                    'valor_db': valor_db,
                    'valor_backup': valor_backup,
                    'path': campo_path
                })
        
        return diferencas
