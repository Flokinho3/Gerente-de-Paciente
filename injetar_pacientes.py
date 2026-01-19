#!/usr/bin/env python3
"""
Script para injetar 400 pacientes de teste no banco de dados.
"""
import random
from datetime import datetime, timedelta
from database import db

# Nomes brasileiros comuns para gestantes
NOMES_GESTANTES = [
    "Maria Silva", "Ana Santos", "Francisca Oliveira", "Antônia Souza", "Adriana Rodrigues",
    "Juliana Alves", "Márcia Lima", "Patrícia Carvalho", "Luciana Pereira", "Verônica Gomes",
    "Beatriz Fernandes", "Gabriela Barbosa", "Camila Melo", "Isabela Rocha", "Rafaela Dias",
    "Larissa Ribeiro", "Carolina Moreira", "Fernanda Castro", "Amanda Costa", "Letícia Martins",
    "Cristina Azevedo", "Sandra Nunes", "Renata Correia", "Simone Cardoso", "Viviane Teixeira",
    "Daniela Mendes", "Bruna Lopes", "Eduarda Ramos", "Tatiana Vieira", "Carla Soares",
    "Cláudia Pinto", "Roberta Monteiro", "Vanessa Barros", "Marcela Figueiredo", "Natália Silva",
    "Juliana Santos", "Patrícia Oliveira", "Luciana Souza", "Gabriela Rodrigues", "Carolina Alves",
    "Isabela Lima", "Fernanda Carvalho", "Amanda Pereira", "Larissa Gomes", "Rafaela Fernandes",
    "Beatriz Barbosa", "Camila Melo", "Adriana Rocha", "Márcia Dias", "Francisca Ribeiro",
    "Ana Moreira", "Antônia Castro", "Maria Costa", "Juliana Martins", "Patrícia Azevedo",
    "Luciana Nunes", "Gabriela Correia", "Carolina Cardoso", "Isabela Teixeira", "Fernanda Mendes",
    "Amanda Lopes", "Larissa Ramos", "Rafaela Vieira", "Beatriz Soares", "Camila Pinto",
    "Adriana Monteiro", "Márcia Barros", "Francisca Figueiredo", "Ana Silva", "Antônia Santos",
    "Maria Oliveira", "Juliana Souza", "Patrícia Rodrigues", "Luciana Alves", "Gabriela Lima",
    "Carolina Carvalho", "Isabela Pereira", "Fernanda Gomes", "Amanda Fernandes", "Larissa Barbosa",
    "Rafaela Melo", "Beatriz Rocha", "Camila Dias", "Adriana Ribeiro", "Márcia Moreira",
    "Francisca Castro", "Ana Costa", "Antônia Martins", "Maria Azevedo", "Juliana Nunes",
    "Patrícia Correia", "Luciana Cardoso", "Gabriela Teixeira", "Carolina Mendes", "Isabela Lopes",
    "Fernanda Ramos", "Amanda Vieira", "Larissa Soares", "Rafaela Pinto", "Beatriz Monteiro",
    "Camila Barros", "Adriana Figueiredo", "Márcia Silva", "Francisca Santos", "Ana Oliveira",
    "Antônia Souza", "Maria Rodrigues", "Juliana Alves", "Patrícia Lima", "Luciana Carvalho",
    "Gabriela Pereira", "Carolina Gomes", "Isabela Fernandes", "Fernanda Barbosa", "Amanda Melo",
    "Larissa Rocha", "Rafaela Dias", "Beatriz Ribeiro", "Camila Moreira", "Adriana Castro",
    "Márcia Costa", "Francisca Martins", "Ana Azevedo", "Antônia Nunes", "Maria Correia",
    "Juliana Cardoso", "Patrícia Teixeira", "Luciana Mendes", "Gabriela Lopes", "Carolina Ramos",
    "Isabela Vieira", "Fernanda Soares", "Amanda Pinto", "Larissa Monteiro", "Rafaela Barros",
    "Beatriz Figueiredo", "Camila Silva", "Adriana Santos", "Márcia Oliveira", "Francisca Souza",
    "Ana Rodrigues", "Antônia Alves", "Maria Lima", "Juliana Carvalho", "Patrícia Pereira",
    "Luciana Gomes", "Gabriela Fernandes", "Carolina Barbosa", "Isabela Melo", "Fernanda Rocha",
    "Amanda Dias", "Larissa Ribeiro", "Rafaela Moreira", "Beatriz Castro", "Camila Costa",
    "Adriana Martins", "Márcia Azevedo", "Francisca Nunes", "Ana Correia", "Antônia Cardoso",
    "Maria Teixeira", "Juliana Mendes", "Patrícia Lopes", "Luciana Ramos", "Gabriela Vieira",
    "Carolina Soares", "Isabela Pinto", "Fernanda Monteiro", "Amanda Barros", "Larissa Figueiredo"
]

# Unidades de saúde fictícias mas realistas
UNIDADES_SAUDE = [
    "UBS Centro", "UBS Jardim América", "UBS São João", "UBS Bela Vista", "UBS Nova Esperança",
    "UBS Santa Maria", "UBS Jardim das Flores", "UBS Vila Nova", "UBS Parque São Jorge",
    "UBS Boa Vista", "UBS Jardim Primavera", "UBS São Pedro", "UBS Nossa Senhora",
    "UBS Vila Verde", "UBS Jardim Europa", "UBS São Paulo", "UBS Boa Esperança",
    "UBS Jardim Tropical", "UBS Vila Rica", "UBS São Luiz", "UBS Nossa Senhora Aparecida",
    "UBS Jardim Botânico", "UBS Vila São Francisco", "UBS São Miguel", "UBS Jardim do Lago",
    "UBS Vila Esperança", "UBS São José", "UBS Nossa Senhora da Conceição", "UBS Jardim dos Ipês",
    "UBS Vila Maria", "UBS São Sebastião", "UBS Nossa Senhora do Carmo", "UBS Jardim das Acácias"
]

# Status das vacinas
VACINAS_STATUS = [
    "Completa", "Incompleta", "Não avaliado", ""
]

def gerar_paciente_aleatorio():
    """Gera dados aleatórios para um paciente."""
    nome = random.choice(NOMES_GESTANTES)
    unidade = random.choice(UNIDADES_SAUDE)

    # Dados de identificação
    identificacao = {
        'nome_gestante': nome,
        'unidade_saude': unidade
    }

    # Dados de avaliação com distribuições realistas
    avaliacao = {
        'inicio_pre_natal_antes_12s': random.choices([True, False], weights=[0.75, 0.25])[0],  # 75% iniciou antes de 12 semanas
        'consultas_pre_natal': random.choices([4, 5, 6, 7, 8, 9], weights=[0.1, 0.15, 0.25, 0.25, 0.15, 0.1])[0],
        'vacinas_completas': random.choice(VACINAS_STATUS),
        'plano_parto': random.choices([True, False], weights=[0.6, 0.4])[0],  # 60% têm plano de parto
        'participou_grupos': random.choices([True, False], weights=[0.45, 0.55])[0],  # 45% participaram de grupos
        'avaliacao_odontologica': random.choices([True, False], weights=[0.7, 0.3])[0],  # 70% fizeram avaliação odontológica
        'estratificacao': random.choices([True, False], weights=[0.8, 0.2])[0],  # 80% foram estratificadas
        'cartao_pre_natal_completo': random.choices([True, False], weights=[0.85, 0.15])[0]  # 85% têm cartão completo
    }

    return {
        'identificacao': identificacao,
        'avaliacao': avaliacao
    }

def gerar_data_salvamento_aleatoria():
    """Gera uma data de salvamento aleatória nos últimos 365 dias."""
    dias_atras = random.randint(0, 365)
    data = datetime.now() - timedelta(days=dias_atras)
    return data.strftime('%Y-%m-%d %H:%M:%S')

def injetar_pacientes(num_pacientes=400):
    """Injeta o número especificado de pacientes no banco de dados."""
    print(f"Iniciando injeção de {num_pacientes} pacientes no banco de dados...")

    pacientes_inseridos = 0
    pacientes_com_erro = 0

    for i in range(num_pacientes):
        try:
            # Gera dados do paciente
            paciente_data = gerar_paciente_aleatorio()

            # Adiciona data de salvamento aleatória
            paciente_data['data_salvamento'] = gerar_data_salvamento_aleatoria()

            # Insere no banco de dados
            resultado = db.adicionar_paciente(paciente_data)

            if resultado['success']:
                pacientes_inseridos += 1
                if (i + 1) % 50 == 0:  # Mostra progresso a cada 50 pacientes
                    print(f"Progresso: {i + 1}/{num_pacientes} pacientes inseridos")
            else:
                pacientes_com_erro += 1
                print(f"Erro ao inserir paciente {i + 1}: {resultado.get('message', 'Erro desconhecido')}")

        except Exception as e:
            pacientes_com_erro += 1
            print(f"Erro inesperado ao inserir paciente {i + 1}: {str(e)}")

    print("\n" + "="*50)
    print("RESUMO DA INJEÇÃO:")
    print(f"Total de pacientes a inserir: {num_pacientes}")
    print(f"Pacientes inseridos com sucesso: {pacientes_inseridos}")
    print(f"Pacientes com erro: {pacientes_com_erro}")
    print("="*50)

    # Mostra estatísticas finais
    try:
        stats = db.obter_estatisticas()
        print("\nESTATÍSTICAS APÓS INSERÇÃO:")
        print(f"Total de pacientes no banco: {stats['total_pacientes']}")
        print(f"Início pré-natal antes 12s: {stats['inicio_pre_natal_antes_12s']}")
        print(f"Consultas pré-natal: {stats['consultas_pre_natal']}")
        print(f"Vacinas completas: {stats['vacinas_completas']}")
        print(f"Plano de parto: {stats['plano_parto']}")
        print(f"Participou de grupos: {stats['participou_grupos']}")
    except Exception as e:
        print(f"Erro ao obter estatísticas: {str(e)}")

    return pacientes_inseridos, pacientes_com_erro

if __name__ == "__main__":
    # Verifica se há pacientes existentes e pergunta se quer limpar
    try:
        stats = db.obter_estatisticas()
        total_existente = stats['total_pacientes']

        if total_existente > 0:
            resposta = input(f"Já existem {total_existente} pacientes no banco. Deseja limpar os dados existentes antes de injetar novos? (s/n): ").lower().strip()
            if resposta in ['s', 'sim', 'y', 'yes']:
                print("Limpando dados existentes...")
                db.limpar_todos_dados()
                print("Dados limpos com sucesso.")
            else:
                resposta = input("Continuar injetando dados (serão adicionados aos existentes)? (s/n): ").lower().strip()
                if resposta not in ['s', 'sim', 'y', 'yes']:
                    print("Operação cancelada.")
                    exit(0)

        # Injeta os pacientes
        inseridos, erros = injetar_pacientes(400)

        if erros == 0:
            print("\n✅ Injeção concluída com sucesso!")
        else:
            print(f"\n⚠️ Injeção concluída com {erros} erros.")

    except KeyboardInterrupt:
        print("\n\nOperação interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro durante a execução: {str(e)}")
    finally:
        # Fecha a conexão com o banco
        db.close()