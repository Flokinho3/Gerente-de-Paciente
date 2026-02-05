from datetime import datetime
from typing import Optional, Dict, Tuple

class StatsMixin:
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
            'participou_grupos': {'sim': 0, 'nao': 0},
            'possui_bolsa_familia': {'sim': 0, 'nao': 0},
            'tem_vacina_covid': {'sim': 0, 'nao': 0}
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
            bf = row['possui_bolsa_familia'] if 'possui_bolsa_familia' in row.keys() else None
            stats['possui_bolsa_familia']['sim'] += 1 if bf == 1 else 0
            stats['possui_bolsa_familia']['nao'] += 1 if bf == 0 or bf is None else 0
            vc = row['tem_vacina_covid'] if 'tem_vacina_covid' in row.keys() else None
            stats['tem_vacina_covid']['sim'] += 1 if vc == 1 else 0
            stats['tem_vacina_covid']['nao'] += 1 if vc == 0 or vc is None else 0
        return stats

    def obter_contagem_dados_completos(
        self, unidade_saude: Optional[str] = None
    ) -> Tuple[int, int]:
        cursor = self.conn.cursor()
        base = "FROM pacientes"
        where = "WHERE LOWER(unidade_saude) = LOWER(?)" if unidade_saude else ""
        params = (unidade_saude,) if unidade_saude else ()
        sql = f"""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN
                inicio_pre_natal_antes_12s IN (0, 1)
                AND consultas_pre_natal IS NOT NULL
                AND vacinas_completas IS NOT NULL AND TRIM(COALESCE(vacinas_completas, '')) != ''
                AND plano_parto IN (0, 1)
                AND participou_grupos IN (0, 1)
                AND possui_bolsa_familia IS NOT NULL AND possui_bolsa_familia IN (0, 1)
                AND tem_vacina_covid IS NOT NULL AND tem_vacina_covid IN (0, 1)
            THEN 1 ELSE 0 END) AS completos
        """ + base + (" " + where if where else "")
        cursor.execute(sql, params)
        row = cursor.fetchone()
        total = int(row["total"]) if row else 0
        completos = int(row["completos"] or 0)
        return (total, completos)

    def obter_estatisticas_coluna(self, nome_coluna: str, unidade_saude: Optional[str] = None) -> Dict:
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(pacientes)")
            colunas_info = cursor.fetchall()
            colunas_existentes = {col['name'] for col in colunas_info}
            
            if nome_coluna not in colunas_existentes:
                return {'success': False, 'message': f'Coluna {nome_coluna} não encontrada', 'data': {'sim': 0, 'nao': 0}}
            
            coluna_info = next((col for col in colunas_info if col['name'] == nome_coluna), None)
            tipo_coluna = coluna_info['type'].upper() if coluna_info else 'TEXT'
            
            if unidade_saude:
                cursor.execute(f"SELECT {nome_coluna} FROM pacientes WHERE LOWER(unidade_saude) = LOWER(?)", (unidade_saude,))
            else:
                cursor.execute(f"SELECT {nome_coluna} FROM pacientes")
            rows = cursor.fetchall()
            
            stats = {'sim': 0, 'nao': 0}
            if 'INTEGER' in tipo_coluna:
                for row in rows:
                    valor = row[nome_coluna] if row[nome_coluna] is not None else 0
                    if valor == 1: stats['sim'] += 1
                    else: stats['nao'] += 1
            else:
                for row in rows:
                    valor = row[nome_coluna]
                    if valor and str(valor).strip(): stats['sim'] += 1
                    else: stats['nao'] += 1
            
            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'message': str(e), 'data': {'sim': 0, 'nao': 0}}

    def obter_estatisticas_temporais(self, filtro: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pacientes ORDER BY data_salvamento ASC")
        rows = cursor.fetchall()
        dados_por_data = {}
        for row in rows:
            data_salvamento = row['data_salvamento']
            if not data_salvamento: continue
            data = data_salvamento.split(' ')[0] if ' ' in data_salvamento else data_salvamento
            if data not in dados_por_data:
                dados_por_data[data] = {
                    'inicio_pre_natal_antes_12s': {'sim': 0, 'nao': 0},
                    'consultas_pre_natal': {'ate_6': 0, 'mais_6': 0},
                    'vacinas_completas': {'completa': 0, 'incompleta': 0, 'nao_avaliado': 0},
                    'plano_parto': {'sim': 0, 'nao': 0},
                    'participou_grupos': {'sim': 0, 'nao': 0},
                    'possui_bolsa_familia': {'sim': 0, 'nao': 0},
                    'tem_vacina_covid': {'sim': 0, 'nao': 0}
                }
            s = dados_por_data[data]
            s['inicio_pre_natal_antes_12s']['sim'] += 1 if row['inicio_pre_natal_antes_12s'] == 1 else 0
            s['inicio_pre_natal_antes_12s']['nao'] += 1 if row['inicio_pre_natal_antes_12s'] == 0 else 0
            nc = row['consultas_pre_natal'] or 0
            s['consultas_pre_natal']['mais_6'] += 1 if nc >= 6 else 0
            s['consultas_pre_natal']['ate_6'] += 1 if nc < 6 else 0
            v = (row['vacinas_completas'] or '').lower()
            if 'completa' in v: s['vacinas_completas']['completa'] += 1
            elif 'incompleta' in v: s['vacinas_completas']['incompleta'] += 1
            else: s['vacinas_completas']['nao_avaliado'] += 1
            s['plano_parto']['sim'] += 1 if row['plano_parto'] == 1 else 0
            s['plano_parto']['nao'] += 1 if row['plano_parto'] == 0 else 0
            s['participou_grupos']['sim'] += 1 if row['participou_grupos'] == 1 else 0
            s['participou_grupos']['nao'] += 1 if row['participou_grupos'] == 0 else 0
            bf = row['possui_bolsa_familia'] if 'possui_bolsa_familia' in row.keys() else None
            s['possui_bolsa_familia']['sim'] += 1 if bf == 1 else 0
            s['possui_bolsa_familia']['nao'] += 1 if bf == 0 or bf is None else 0
            vc = row['tem_vacina_covid'] if 'tem_vacina_covid' in row.keys() else None
            s['tem_vacina_covid']['sim'] += 1 if vc == 1 else 0
            s['tem_vacina_covid']['nao'] += 1 if vc == 0 or vc is None else 0

        datas = sorted(dados_por_data.keys())
        valores = {}
        for data in datas:
            s = dados_por_data[data]
            valores[data] = {}
            if filtro == 'inicio_pre_natal_antes_12s':
                valores[data]['Sim'], valores[data]['Não'] = s[filtro]['sim'], s[filtro]['nao']
            elif filtro == 'consultas_pre_natal':
                valores[data]['≥ 6 consultas'], valores[data]['< 6 consultas'] = s[filtro]['mais_6'], s[filtro]['ate_6']
            elif filtro == 'vacinas_completas':
                valores[data]['Completo'], valores[data]['Incompleto'], valores[data]['Não avaliado'] = s[filtro]['completa'], s[filtro]['incompleta'], s[filtro]['nao_avaliado']
            elif filtro == 'plano_parto':
                valores[data]['Sim'], valores[data]['Não'] = s[filtro]['sim'], s[filtro]['nao']
            elif filtro == 'participou_grupos':
                valores[data]['Participou'], valores[data]['Não participou'] = s[filtro]['sim'], s[filtro]['nao']
            elif filtro == 'possui_bolsa_familia':
                valores[data]['Sim'], valores[data]['Não'] = s[filtro]['sim'], s[filtro]['nao']
            elif filtro == 'tem_vacina_covid':
                valores[data]['Sim'], valores[data]['Não'] = s[filtro]['sim'], s[filtro]['nao']
        return {'datas': datas, 'valores': valores}
