"""
Injeta 2.000 pacientes com dados aleatórios no banco.
Uso: python seed_pacientes_2k.py

Requer .env carregado (DB_PATH) ou usa data/pacientes.db por padrão.
"""
from __future__ import annotations

import os
import random
import uuid
from datetime import datetime, timedelta

# Carregar .env antes de importar database
import env_loader

env_loader.load_env()

from database import Database

N = 2_000
ARQUIVO_ORIGEM = "seed_injecao_2k"

NOMES = (
    "Ana", "Maria", "Juliana", "Fernanda", "Patricia", "Camila", "Amanda", "Bruna",
    "Carla", "Daniela", "Eliane", "Fatima", "Gabriela", "Helena", "Izabel", "Joana",
    "Luciana", "Marcia", "Natasha", "Olivia", "Paula", "Renata", "Sandra", "Tatiana",
    "Vanessa", "Aline", "Beatriz", "Cristina", "Denise", "Elena", "Franciele", "Gisele",
    "Larissa", "Michele", "Natalia", "Priscila", "Raquel", "Simone", "Thais", "Viviane",
)
SOBRENOMES = (
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Rocha", "Almeida",
    "Nascimento", "Araujo", "Melo", "Barbosa", "Castro", "Dias", "Moreira", "Nunes",
    "Teixeira", "Correia", "Monteiro", "Cardoso", "Lopes", "Freitas", "Mendes", "Vieira",
)

UNIDADES = (
    "UBS Centro", "UBS Bela Vista", "UBS Jardim América", "UBS Vila Nova", "UBS São José",
    "UBS Santa Maria", "UBS Kennedy", "UBS Industrial", "UBS Aeroporto", "UBS Cohab",
    "UBS Planalto", "UBS Boa Esperança", "UBS Progresso", "UBS Alto da Serra", "UBS Recanto",
)

VACINAS = ("completa", "incompleta", "nao_avaliado")
KIT_TIPOS = ("Enxoval básico", "Kit bebê", "Kit gestante", "Misto", None)
METODOS = ("Pílula", "DIU", "Implante", "Preservativo", "Laqueadura", "Nenhum", None)
GENEROS_FILHOS = ("M", "F", "M,F", "F,M", "M,M", "F,F", "M,F,M", "")


def _randdate(start: datetime, end: datetime) -> str:
    d = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    return d.strftime("%Y-%m-%d")


def _randtime() -> str:
    h = random.randint(7, 17)
    m = random.choice((0, 15, 30, 45))
    return f"{h:02d}:{m:02d}"


def _gerar_paciente(i: int) -> tuple[str, dict]:
    """Retorna (id único, paciente_data para inserir_registro)."""
    pid = f"inj_{i}_{uuid.uuid4().hex[:12]}"
    nome = f"{random.choice(NOMES)} {random.choice(SOBRENOMES)}"
    unidade = random.choice(UNIDADES)
    hoje = datetime.now()
    ano_atras = hoje - timedelta(days=400)
    ano_frente = hoje + timedelta(days=120)

    qtd_filhos = random.randint(0, 5)
    generos = random.choice(GENEROS_FILHOS) if qtd_filhos else ""
    ja_ganhou = qtd_filhos > 0 or random.random() < 0.3
    data_ganhou = _randdate(ano_atras, ano_atras + timedelta(days=600)) if ja_ganhou and random.random() < 0.7 else None

    # DUM/DPP: gestação ~40 sem
    dum = _randdate(ano_atras, hoje - timedelta(days=60))
    d = datetime.strptime(dum, "%Y-%m-%d")
    dpp = (d + timedelta(days=280)).strftime("%Y-%m-%d")

    sem_inicio = random.randint(4, 20)
    inicio_antes_12 = 1 if sem_inicio < 12 else 0
    obs_inicio = random.choice(("", "Sem intercorrências.", "Encaminhada.", "Acompanhamento rotineiro.", None))

    consultas = random.randint(0, 14)
    vacinas = random.choices(VACINAS, weights=[50, 30, 20], k=1)[0]
    plano = random.choice((0, 1))
    grupos = random.choice((0, 1))
    odonto = random.choice((0, 1))
    estrat = random.choice((0, 1))
    prob_estrat = random.choice(("", "Nenhum.", "Risco baixo.", None)) if estrat else None
    cartao = random.choice((0, 1))
    bolsa = random.choice((0, 1))
    covid = random.choice((0, 1))
    plano_entregue = random.choice(("Sim", "Não", "Em análise", None))
    ganhou_kit = random.choice((0, 1))
    kit_tipo = random.choice(KIT_TIPOS) if ganhou_kit else None
    metodo = random.choice(METODOS)
    metodo_outros = random.choice(("", "Outro método.", None)) if random.random() < 0.1 else None

    prox_aval = _randdate(hoje, ano_frente) if random.random() < 0.6 else None
    prox_hora = _randtime() if prox_aval and random.random() < 0.7 else None

    data_salv = (hoje - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d %H:%M:%S")

    identificacao = {
        "nome_gestante": nome,
        "unidade_saude": unidade,
    }
    avaliacao = {
        "inicio_pre_natal_antes_12s": bool(inicio_antes_12),
        "inicio_pre_natal_semanas": sem_inicio,
        "inicio_pre_natal_observacao": obs_inicio,
        "consultas_pre_natal": consultas,
        "vacinas_completas": vacinas,
        "plano_parto": bool(plano),
        "participou_grupos": bool(grupos),
        "avaliacao_odontologica": bool(odonto),
        "estratificacao": bool(estrat),
        "estratificacao_problema": prob_estrat,
        "cartao_pre_natal_completo": bool(cartao),
        "possui_bolsa_familia": bool(bolsa),
        "tem_vacina_covid": bool(covid),
        "plano_parto_entregue_por_unidade": plano_entregue,
        "dum": dum,
        "dpp": dpp,
        "ganhou_kit": bool(ganhou_kit),
        "kit_tipo": kit_tipo,
        "proxima_avaliacao": prox_aval,
        "proxima_avaliacao_hora": prox_hora,
        "ja_ganhou_crianca": ja_ganhou,
        "data_ganhou_crianca": data_ganhou,
        "quantidade_filhos": qtd_filhos,
        "generos_filhos": generos,
        "metodo_preventivo": metodo,
        "metodo_preventivo_outros": metodo_outros,
    }
    paciente_data = {"identificacao": identificacao, "avaliacao": avaliacao}

    return pid, paciente_data, data_salv


def main() -> None:
    db = Database()
    print(f"Injetando {N} pacientes em {db.db_path} ...")
    ok = 0
    err = 0
    for i in range(1, N + 1):
        try:
            pid, paciente_data, data_salv = _gerar_paciente(i)
            db.inserir_registro(
                pid,
                paciente_data,
                arquivo_origem=ARQUIVO_ORIGEM,
                data_salvamento=data_salv,
            )
            ok += 1
            if i % 250 == 0:
                print(f"  {i}/{N} ...")
        except Exception as e:
            err += 1
            print(f"  Erro ao inserir paciente {i}: {e}")
    print(f"Concluído: {ok} inseridos, {err} erros.")


if __name__ == "__main__":
    main()
