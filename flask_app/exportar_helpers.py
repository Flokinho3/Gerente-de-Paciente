"""
Helpers para exportação: colunas, formatters, filtros.
"""
import io
from datetime import datetime

from flask import jsonify, make_response, send_file


def formatar_boolean(valor):
    if valor is True:
        return "Sim"
    if valor is False:
        return "Não"
    return "Não informado"


def formatar_vacinas(valor):
    return valor if valor else "Não avaliado"


def formatar_valor_opcional(valor):
    if valor is None or valor == "":
        return "Não informado"
    return str(valor)


def verificar_status_vacinas(status, filtro):
    if filtro == "completa":
        return "complet" in status and "incomplet" not in status
    if filtro == "incompleta":
        return "incomplet" in status
    if filtro == "nao_avaliado":
        return status == "" or "nao" in status or "não" in status
    return True


COLUNAS_CONFIG = [
    {"key": "identificacao.nome_gestante", "label": "Nome da Gestante"},
    {"key": "identificacao.unidade_saude", "label": "Unidade de Saúde"},
    {"key": "data_salvamento", "label": "Data de Cadastro"},
    {"key": "avaliacao.inicio_pre_natal_antes_12s", "label": "Início pré-natal antes de 12 semanas", "formatter": formatar_boolean},
    {"key": "avaliacao.inicio_pre_natal_semanas", "label": "Semanas de início do pré-natal"},
    {"key": "avaliacao.inicio_pre_natal_observacao", "label": "Observação do início pré-natal"},
    {"key": "avaliacao.consultas_pre_natal", "label": "Consultas de pré-natal"},
    {"key": "avaliacao.vacinas_completas", "label": "Vacinas completas", "formatter": formatar_vacinas},
    {"key": "avaliacao.plano_parto", "label": "Plano de parto", "formatter": formatar_boolean},
    {"key": "avaliacao.participou_grupos", "label": "Participou de grupos", "formatter": formatar_boolean},
    {"key": "avaliacao.avaliacao_odontologica", "label": "Avaliação odontológica", "formatter": formatar_boolean},
    {"key": "avaliacao.estratificacao", "label": "Estratificação", "formatter": formatar_boolean},
    {"key": "avaliacao.estratificacao_problema", "label": "Problema de estratificação"},
    {"key": "avaliacao.cartao_pre_natal_completo", "label": "Cartão pré-natal completo", "formatter": formatar_boolean},
    {"key": "avaliacao.possui_bolsa_familia", "label": "Possui Bolsa Família", "formatter": formatar_boolean},
    {"key": "avaliacao.tem_vacina_covid", "label": "Tem vacina de COVID", "formatter": formatar_boolean},
    {"key": "avaliacao.plano_parto_entregue_por_unidade", "label": "Plano de parto entregue por unidade"},
    {"key": "avaliacao.dum", "label": "DUM (Data da Última Menstruação)"},
    {"key": "avaliacao.dpp", "label": "DPP (Data Provável do Parto)"},
    {"key": "avaliacao.ganhou_kit", "label": "Ganhou kit", "formatter": formatar_boolean},
    {"key": "avaliacao.kit_tipo", "label": "Tipo de kit"},
    {"key": "avaliacao.proxima_avaliacao", "label": "Próxima avaliação (data)"},
    {"key": "avaliacao.proxima_avaliacao_hora", "label": "Próxima avaliação (hora)"},
    {"key": "avaliacao.ja_ganhou_crianca", "label": "Já ganhou criança", "formatter": formatar_boolean},
    {"key": "avaliacao.data_ganhou_crianca", "label": "Data que ganhou criança"},
    {"key": "avaliacao.quantidade_filhos", "label": "Quantidade de filhos"},
    {"key": "avaliacao.generos_filhos", "label": "Gêneros dos filhos"},
    {"key": "avaliacao.metodo_preventivo", "label": "Método preventivo"},
    {"key": "avaliacao.metodo_preventivo_outros", "label": "Método preventivo (outros)"},
]


def obter_colunas_config(colunas_personalizadas):
    if colunas_personalizadas:
        sel = [c for c in COLUNAS_CONFIG if c["key"] in colunas_personalizadas]
        if sel:
            return sel
    return COLUNAS_CONFIG


def obter_valor_coluna(paciente, coluna):
    valor = paciente
    for parte in coluna["key"].split("."):
        if isinstance(valor, dict):
            valor = valor.get(parte, "")
        else:
            valor = ""
    formatter = coluna.get("formatter")
    if callable(formatter):
        return formatter(valor)
    return "" if valor is None else valor


def aplicar_filtros_exportacao(pacientes, filtros):
    if not any(filtros.values()):
        return pacientes
    resultados = []
    for p in pacientes:
        av = p.get("avaliacao", {})
        if filtros.get("inicio_pre_natal") and not av.get("inicio_pre_natal_antes_12s"):
            continue
        if filtros.get("plano_parto") and not av.get("plano_parto"):
            continue
        if filtros.get("participou_grupos") and not av.get("participou_grupos"):
            continue
        if filtros.get("possui_bolsa_familia") and not av.get("possui_bolsa_familia"):
            continue
        if filtros.get("tem_vacina_covid") and not av.get("tem_vacina_covid"):
            continue
        if filtros.get("vacinas"):
            st = (av.get("vacinas_completas") or "").lower()
            if not verificar_status_vacinas(st, filtros["vacinas"]):
                continue
        resultados.append(p)
    return resultados
