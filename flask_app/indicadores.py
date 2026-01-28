"""
API: Indicadores, unidades de saúde, ranking, campos disponíveis, temporais.
"""
from flask import Blueprint, jsonify, request

from .db import db

bp = Blueprint("api_indicadores", __name__, url_prefix="/api")

NOMES_AMIGAVEIS = {
    "inicio_pre_natal_antes_12s": "Início pré-natal antes de 12 semanas",
    "inicio_pre_natal_semanas": "Semanas do início do pré-natal",
    "inicio_pre_natal_observacao": "Observação do início do pré-natal",
    "consultas_pre_natal": "Consultas de pré-natal",
    "vacinas_completas": "Vacinas completas",
    "plano_parto": "Plano de parto",
    "participou_grupos": "Participou de grupos",
    "avaliacao_odontologica": "Avaliação odontológica",
    "estratificacao": "Estratificação",
    "estratificacao_problema": "Problema de estratificação",
    "cartao_pre_natal_completo": "Cartão pré-natal completo",
    "possui_bolsa_familia": "Possui Bolsa Família",
    "tem_vacina_covid": "Tem vacina de COVID",
    "plano_parto_entregue_por_unidade": "Plano de parto entregue por unidade",
    "dum": "DUM (Data da Última Menstruação)",
    "dpp": "DPP (Data Provável do Parto)",
    "ganhou_kit": "Ganhou kit",
    "kit_tipo": "Tipo de kit",
    "proxima_avaliacao": "Próxima avaliação",
    "proxima_avaliacao_hora": "Hora da próxima avaliação",
    "ja_ganhou_crianca": "Já ganhou criança",
    "data_ganhou_crianca": "Data que ganhou criança",
    "quantidade_filhos": "Quantidade de filhos",
    "generos_filhos": "Gêneros dos filhos",
    "metodo_preventivo": "Método preventivo",
    "metodo_preventivo_outros": "Outro método preventivo",
}

CRITERIOS_VALIDOS = {
    "inicio_pre_natal_antes_12s": ("sim", "nao", "Início pré-natal antes de 12 sem."),
    "consultas_pre_natal": ("mais_6", "ate_6", "≥ 6 consultas"),
    "vacinas_completas": ("completa", ("incompleta", "nao_avaliado"), "Vacinas completas"),
    "plano_parto": ("sim", "nao", "Plano de parto"),
    "participou_grupos": ("sim", "nao", "Participou de grupos"),
    "possui_bolsa_familia": ("sim", "nao", "Possui Bolsa Família"),
    "tem_vacina_covid": ("sim", "nao", "Tem vacina de COVID"),
}

FILTROS_TEMPORAIS = [
    "inicio_pre_natal_antes_12s",
    "consultas_pre_natal",
    "vacinas_completas",
    "plano_parto",
    "participou_grupos",
    "possui_bolsa_familia",
    "tem_vacina_covid",
]


@bp.route("/indicadores", methods=["GET"])
def indicadores():
    try:
        unidade_saude = request.args.get("unidade_saude")
        stats = db.obter_estatisticas(unidade_saude=unidade_saude)
        return jsonify({
            "total": stats["total_pacientes"],
            "inicio_pre_natal_antes_12s": stats["inicio_pre_natal_antes_12s"],
            "consultas_pre_natal": stats["consultas_pre_natal"],
            "vacinas_completas": stats["vacinas_completas"],
            "plano_parto": stats["plano_parto"],
            "participou_grupos": stats["participou_grupos"],
            "possui_bolsa_familia": stats["possui_bolsa_familia"],
            "tem_vacina_covid": stats["tem_vacina_covid"],
        })
    except Exception:
        return jsonify({
            "total": 0,
            "inicio_pre_natal_antes_12s": {"sim": 0, "nao": 0},
            "consultas_pre_natal": {"ate_6": 0, "mais_6": 0},
            "vacinas_completas": {"completa": 0, "incompleta": 0, "nao_avaliado": 0},
            "plano_parto": {"sim": 0, "nao": 0},
            "participou_grupos": {"sim": 0, "nao": 0},
            "possui_bolsa_familia": {"sim": 0, "nao": 0},
            "tem_vacina_covid": {"sim": 0, "nao": 0},
        }), 500


@bp.route("/unidades_saude", methods=["GET"])
def listar_unidades_saude():
    try:
        unidades = db.obter_unidades_saude_unicas()
        return jsonify({"success": True, "unidades": unidades})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@bp.route("/ranking_unidades", methods=["GET"])
def ranking_unidades():
    try:
        criterio = request.args.get("criterio", "inicio_pre_natal_antes_12s")
        limite_raw = int(request.args.get("limite", 10))
        limite = 0 if limite_raw <= 0 else min(limite_raw, 50)
        unidades_param = (request.args.get("unidades") or "").strip()
        criterio_hardcoded = criterio in CRITERIOS_VALIDOS
        if criterio_hardcoded:
            cfg = CRITERIOS_VALIDOS[criterio]
            pos_key = cfg[0]
            neg_keys = (cfg[1],) if isinstance(cfg[1], str) else cfg[1]
            label = cfg[2]
        else:
            col_check = db.obter_estatisticas_coluna(criterio)
            if not col_check.get("success"):
                return jsonify({
                    "success": False,
                    "message": col_check.get("message", "Filtro inválido"),
                    "ranking": [],
                }), 400
            label = criterio

        unidades = db.obter_unidades_saude_unicas()
        if unidades_param:
            req_list = [x.strip() for x in unidades_param.split(",") if x.strip()]
            req_set = set((x or "").lower() for x in req_list)
            unidades = [u for u in unidades if (u or "").strip().lower() in req_set]
        ranking = []
        for u in unidades:
            if criterio_hardcoded:
                s = db.obter_estatisticas(unidade_saude=u)
                total = s["total_pacientes"]
                if criterio == "vacinas_completas":
                    d = s["vacinas_completas"]
                    pos = d.get("completa", 0)
                    den = d.get("completa", 0) + d.get("incompleta", 0) + d.get("nao_avaliado", 0)
                    pct = (pos / den * 100) if den else 0
                elif criterio == "consultas_pre_natal":
                    d = s["consultas_pre_natal"]
                    pos = d.get("mais_6", 0)
                    den = d.get("mais_6", 0) + d.get("ate_6", 0)
                    pct = (pos / den * 100) if den else 0
                else:
                    d = s.get(criterio, {})
                    pos = d.get(pos_key, 0)
                    den = pos + sum(d.get(k, 0) for k in neg_keys)
                    pct = (pos / den * 100) if den else 0
            else:
                stats = db.obter_estatisticas_coluna(criterio, unidade_saude=u)
                pos = stats["data"].get("sim", 0)
                den = pos + stats["data"].get("nao", 0)
                total = den
                pct = (pos / den * 100) if den else 0
            ranking.append({"unidade": u, "total": total, "percentual": round(pct, 1), "criterio_label": label})
        ranking.sort(key=lambda x: (-x["percentual"], -x["total"]))
        if unidades_param or limite <= 0:
            resultado = ranking
        else:
            resultado = ranking[:limite]
        return jsonify({"success": True, "ranking": resultado})
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "ranking": []}), 500


@bp.route("/indicadores_coluna/<nome_coluna>", methods=["GET"])
def obter_indicador_coluna(nome_coluna):
    try:
        resultado = db.obter_estatisticas_coluna(nome_coluna)
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "data": {"sim": 0, "nao": 0}}), 500


@bp.route("/campos_disponiveis", methods=["GET"])
def listar_campos_disponiveis():
    try:
        excluidos = {"id", "nome_gestante", "unidade_saude", "data_salvamento", "arquivo_origem"}
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(pacientes)")
        colunas = cursor.fetchall()
        if not colunas:
            return jsonify({"success": False, "message": "Nenhuma coluna encontrada", "campos": []}), 500
        campos = []
        for col in colunas:
            nome = col["name"]
            if nome in excluidos:
                continue
            campos.append({
                "campo": nome,
                "label": NOMES_AMIGAVEIS.get(nome, nome.replace("_", " ").title()),
                "tipo": col["type"],
            })
        return jsonify({"success": True, "campos": campos})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"success": False, "message": str(e), "campos": []}), 500


@bp.route("/indicadores/temporais/<filtro>", methods=["GET"])
def indicadores_temporais(filtro):
    try:
        if filtro not in FILTROS_TEMPORAIS:
            return jsonify({"error": "Filtro inválido"}), 400
        return jsonify(db.obter_estatisticas_temporais(filtro))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Critérios usados no ranking geral (score = média dos % positivos, ou média ponderada com travas)
CRITERIOS_RANKING_GERAL = [
    "inicio_pre_natal_antes_12s",
    "consultas_pre_natal",
    "vacinas_completas",
    "plano_parto",
    "participou_grupos",
    "possui_bolsa_familia",
    "tem_vacina_covid",
]

# --- Travas (quando ?trava=1, padrão) ---
# 1ª trava: tamanho mínimo. Participa se (total >= MIN_PACIENTES) OU (completos/total >= MIN_PCT_COMPLETOS/100)
MIN_PACIENTES = 50
MIN_PCT_COMPLETOS = 70

# 2ª trava: piso mínimo por critério essencial. Quem não atingir em qualquer um não pode ser 1º.
PISOS_CRITERIOS = {
    "inicio_pre_natal_antes_12s": 40,
    "consultas_pre_natal": 50,
    "vacinas_completas": 60,
}

# 3ª trava: pesos (score = média ponderada)
PESOS_CRITERIOS = {
    "inicio_pre_natal_antes_12s": 2,
    "consultas_pre_natal": 2,
    "vacinas_completas": 1,
    "plano_parto": 1,
    "participou_grupos": 0.5,
    "possui_bolsa_familia": 0.5,
    "tem_vacina_covid": 0.5,
}

# 4ª trava: penalidade por dado ausente. Se % ausente > LIMITE_PCT_AUSENTE em qualquer critério: -PENALIDADE_AUSENTE % no score.
LIMITE_PCT_AUSENTE = 20
PENALIDADE_AUSENTE = 5


def _percentual_positivo(s, criterio):
    """Retorna o percentual positivo (0–100) para um critério nas stats s."""
    if criterio == "vacinas_completas":
        d = s.get("vacinas_completas", {})
        pos = d.get("completa", 0)
        den = pos + d.get("incompleta", 0) + d.get("nao_avaliado", 0)
        return (pos / den * 100) if den else 0
    if criterio == "consultas_pre_natal":
        d = s.get("consultas_pre_natal", {})
        pos = d.get("mais_6", 0)
        den = pos + d.get("ate_6", 0)
        return (pos / den * 100) if den else 0
    cfg = CRITERIOS_VALIDOS.get(criterio)
    if not cfg:
        return 0
    pos_key = cfg[0]
    neg_keys = (cfg[1],) if isinstance(cfg[1], str) else cfg[1]
    d = s.get(criterio, {})
    pos = d.get(pos_key, 0)
    den = pos + sum(d.get(k, 0) for k in neg_keys)
    return (pos / den * 100) if den else 0


def _denominador_criterio(s, criterio):
    """Retorna o denominador (total com dado válido) para o critério."""
    if criterio == "vacinas_completas":
        d = s.get("vacinas_completas", {})
        return d.get("completa", 0) + d.get("incompleta", 0) + d.get("nao_avaliado", 0)
    if criterio == "consultas_pre_natal":
        d = s.get("consultas_pre_natal", {})
        return d.get("mais_6", 0) + d.get("ate_6", 0)
    cfg = CRITERIOS_VALIDOS.get(criterio)
    if not cfg:
        return 0
    pos_key = cfg[0]
    neg_keys = (cfg[1],) if isinstance(cfg[1], str) else cfg[1]
    d = s.get(criterio, {})
    return d.get(pos_key, 0) + sum(d.get(k, 0) for k in neg_keys)


def _unidade_atende_trava1(total: int, completos: int) -> bool:
    """1ª trava: tamanho mínimo. True se (total >= MIN) ou (≥70% com dados completos)."""
    if total == 0:
        return False
    return total >= MIN_PACIENTES or (completos / total * 100) >= MIN_PCT_COMPLETOS


def _atinge_pisos(pcts_by_criterio: dict) -> bool:
    """2ª trava: atinge piso em todos os critérios essenciais."""
    for c, piso in PISOS_CRITERIOS.items():
        if (pcts_by_criterio.get(c) or 0) < piso:
            return False
    return True


def _score_com_pesos(pcts_by_criterio: dict) -> float:
    """3ª trava: score = média ponderada pelos PESOS_CRITERIOS."""
    num = sum((pcts_by_criterio.get(c) or 0) * PESOS_CRITERIOS.get(c, 1) for c in CRITERIOS_RANKING_GERAL)
    den = sum(PESOS_CRITERIOS.get(c, 1) for c in CRITERIOS_RANKING_GERAL)
    return (num / den) if den else 0


def _aplicar_penalidade_ausencia(s, total: int) -> float:
    """4ª trava: se % ausente > 20% em qualquer critério, redutor de 5% no score."""
    if total == 0:
        return 0
    for c in CRITERIOS_RANKING_GERAL:
        den = _denominador_criterio(s, c)
        ausentes = total - den
        pct_ausente = (ausentes / total * 100) if total else 0
        if pct_ausente > LIMITE_PCT_AUSENTE:
            return PENALIDADE_AUSENTE
    return 0


@bp.route("/ranking_unidades_geral", methods=["GET"])
def ranking_unidades_geral():
    """Ranking geral. Com ?trava=1 (padrão): travas ativas. Com ?trava=0: ranking simples (média, sem filtros)."""
    try:
        trava = request.args.get("trava", "1").strip().lower() in ("1", "true", "sim", "on", "yes")
        unidades = db.obter_unidades_saude_unicas()
        ranking = []

        for u in unidades:
            s = db.obter_estatisticas(unidade_saude=u)
            total = s["total_pacientes"]
            if total == 0:
                continue

            if trava:
                total_db, completos = db.obter_contagem_dados_completos(unidade_saude=u)
                if not _unidade_atende_trava1(total_db, completos):
                    continue

            pcts = {c: _percentual_positivo(s, c) for c in CRITERIOS_RANKING_GERAL}
            if trava:
                score_raw = _score_com_pesos(pcts)
                penal = _aplicar_penalidade_ausencia(s, total)
                score = max(0, round(score_raw - penal, 1))
                elegivel_1o = _atinge_pisos(pcts)
            else:
                score = round(sum(pcts[c] for c in CRITERIOS_RANKING_GERAL) / len(CRITERIOS_RANKING_GERAL), 1)
                elegivel_1o = True

            ranking.append({
                "unidade": u,
                "total": total,
                "score": score,
                "posicao": 0,
                "elegivel_1o_lugar": elegivel_1o,
            })

        # Ordenar: com trava, elegíveis primeiro (por score), depois não elegíveis; sem trava, só por score.
        if trava:
            ranking.sort(key=lambda x: (-int(x["elegivel_1o_lugar"]), -x["score"], -x["total"]))
        else:
            ranking.sort(key=lambda x: (-x["score"], -x["total"]))

        for i, r in enumerate(ranking, 1):
            r["posicao"] = i

        # Destaque: 1º do ranking. Com trava, só elegível pode ser destaque; se nenhum elegível, sem destaque.
        if trava:
            candidato = next((r for r in ranking if r["elegivel_1o_lugar"]), None)
            unidade_destaque = candidato
        else:
            unidade_destaque = ranking[0] if ranking else None

        return jsonify({
            "success": True,
            "ranking_geral": ranking,
            "unidade_destaque": unidade_destaque,
            "com_trava": trava,
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "ranking_geral": [], "unidade_destaque": None}), 500
