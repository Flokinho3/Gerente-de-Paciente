#!/usr/bin/env python3
"""
Script para injetar 200 pacientes no banco de dados
Gera dados variados e realistas para testes
"""

import random
from datetime import datetime, timedelta
from database import db

# Lista de nomes brasileiros comuns
NOMES_GESTANTES = [
    "Ana", "Maria", "Juliana", "Fernanda", "Patricia", "Beatriz", "Carolina",
    "Amanda", "Bruna", "Camila", "Carla", "Cristina", "Daniela", "Eduarda",
    "Eliane", "Fabiana", "Gabriela", "Helena", "Isabela", "Jessica", "Larissa",
    "Leticia", "Luciana", "Marcia", "Mariana", "Monica", "Natasha", "Paula",
    "Rafaela", "Renata", "Roberta", "Sandra", "Simone", "Tatiana", "Vanessa",
    "Viviane", "Adriana", "Aline", "Andrea", "Angela", "Antonia", "Barbara",
    "Bianca", "Cecilia", "Claudia", "Daniele", "Diana", "Elisa", "Erica",
    "Flavia", "Gisele", "Glauce", "Iara", "Irene", "Janaina", "Joana",
    "Karina", "Kelly", "Lais", "Larissa", "Laura", "Leonor", "Lilian",
    "Lorena", "Luana", "Lucia", "Luiza", "Magali", "Marcela", "Margarida",
    "Marta", "Michelle", "Milena", "Miriam", "Natalia", "Nayara", "Nicole",
    "Olivia", "Priscila", "Raquel", "Regina", "Rejane", "Rita", "Sabrina",
    "Samantha", "Sara", "Sheila", "Silvia", "Sonia", "Sueli", "Suzana",
    "Talita", "Tania", "Teresa", "Thais", "Valeria", "Vania", "Vera",
    "Viviana", "Yara", "Yasmin", "Adriana", "Alexandra", "Alessandra",
    "Andressa", "Angela", "Anita", "Anna", "Anne", "Antonela", "Aparecida"
]

# Lista de unidades de saúde
UNIDADES_SAUDE = [
    "UBS Centro", "UBS Norte", "UBS Sul", "UBS Leste", "UBS Oeste",
    "Centro de Saúde Central", "Posto de Saúde Jardim Primavera",
    "Posto de Saúde Vila Nova", "Posto de Saúde São José",
    "Centro de Saúde Bom Pastor", "UBS São Sebastião",
    "Posto de Saúde Santa Maria", "Centro de Saúde Progresso",
    "UBS Bela Vista", "Posto de Saúde Morumbi",
    "Centro de Saúde Copacabana", "UBS Ipanema",
    "Posto de Saúde Tijuca", "Centro de Saúde Leblon",
    "UBS Botafogo", "Posto de Saúde Flamengo",
    "Centro de Saúde Centro", "UBS Lapa",
    "Posto de Saúde Catete", "Centro de Saúde Glória"
]

# Opções de vacinas
VACINAS_OPCOES = ["Completa", "Incompleta", "Não avaliado", ""]

def gerar_data_aleatoria():
    """Gera uma data aleatória nos últimos 6 meses"""
    dias_atras = random.randint(0, 180)
    data = datetime.now() - timedelta(days=dias_atras)
    return data

def gerar_paciente_aleatorio(numero):
    """Gera dados aleatórios para um paciente"""
    
    # Escolher nome aleatório, com variação para evitar duplicatas exatas
    nome_base = random.choice(NOMES_GESTANTES)
    if random.random() < 0.3:  # 30% de chance de adicionar sobrenome
        sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Pereira", "Rodrigues"]
        nome = f"{nome_base} {random.choice(sobrenomes)}"
    else:
        nome = nome_base
    
    # Adicionar número para garantir unicidade se necessário
    if random.random() < 0.1:  # 10% de chance de adicionar número
        nome = f"{nome} {numero}"
    
    # Gerar dados de identificação
    identificacao = {
        "nome_gestante": nome,
        "unidade_saude": random.choice(UNIDADES_SAUDE)
    }
    
    # Gerar dados de avaliação com distribuição realista
    # Mais pacientes têm valores True para alguns campos
    avaliacao = {
        "inicio_pre_natal_antes_12s": random.random() < 0.6,  # 60% True
        "consultas_pre_natal": random.randint(0, 20),
        "vacinas_completas": random.choice(VACINAS_OPCOES),
        "plano_parto": random.random() < 0.5,  # 50% True
        "participou_grupos": random.random() < 0.4,  # 40% True
        "avaliacao_odontologica": random.random() < 0.7,  # 70% True
        "estratificacao": random.random() < 0.6,  # 60% True
        "cartao_pre_natal_completo": random.random() < 0.8  # 80% True
    }
    
    # Ajustar consultas para serem mais realistas (maioria entre 4-12)
    if random.random() < 0.7:
        avaliacao["consultas_pre_natal"] = random.randint(4, 12)
    
    # Ajustar vacinas para distribuição mais realista
    if random.random() < 0.6:
        avaliacao["vacinas_completas"] = random.choice(["Completa", "Incompleta"])
    
    paciente_data = {
        "identificacao": identificacao,
        "avaliacao": avaliacao
    }
    
    return paciente_data

def injetar_pacientes(quantidade=200):
    """Injeta pacientes no banco de dados"""
    
    print(f"Iniciando injeção de {quantidade} pacientes no banco de dados...")
    print("-" * 60)
    
    sucessos = 0
    erros = 0
    
    for i in range(1, quantidade + 1):
        try:
            # Gerar dados do paciente
            paciente_data = gerar_paciente_aleatorio(i)
            
            # Adicionar ao banco de dados
            resultado = db.adicionar_paciente(paciente_data)
            
            if resultado.get('success'):
                sucessos += 1
                if i % 50 == 0 or i == quantidade:
                    print(f"Progresso: {i}/{quantidade} pacientes adicionados...")
            else:
                erros += 1
                print(f"Erro ao adicionar paciente {i}: {resultado.get('message', 'Erro desconhecido')}")
        
        except Exception as e:
            erros += 1
            print(f"Erro ao adicionar paciente {i}: {str(e)}")
    
    print("-" * 60)
    print(f"Injeção concluída!")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Erros: {erros}")
    print(f"📊 Total processado: {quantidade}")
    
    # Mostrar estatísticas do banco
    try:
        stats = db.obter_estatisticas()
        print(f"\n📈 Estatísticas do banco de dados:")
        print(f"   Total de pacientes: {stats['total_pacientes']}")
        print(f"   Última atualização: {stats['ultima_atualizacao']}")
    except Exception as e:
        print(f"\n⚠️  Não foi possível obter estatísticas: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("SCRIPT DE INJEÇÃO DE PACIENTES NO BANCO DE DADOS")
    print("=" * 60)
    print()
    
    # Perguntar quantidade (ou usar padrão 200)
    try:
        resposta = input("Quantos pacientes deseja injetar? (pressione Enter para 200): ").strip()
        quantidade = int(resposta) if resposta else 200
    except ValueError:
        print("Valor inválido. Usando 200 como padrão.")
        quantidade = 200
    
    if quantidade <= 0:
        print("Quantidade deve ser maior que zero. Usando 200 como padrão.")
        quantidade = 200
    
    print()
    confirmar = input(f"Tem certeza que deseja injetar {quantidade} pacientes? (s/N): ").strip().lower()
    
    if confirmar == 's' or confirmar == 'sim':
        print()
        injetar_pacientes(quantidade)
    else:
        print("Operação cancelada.")
