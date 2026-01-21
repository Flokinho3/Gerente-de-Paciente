#!/usr/bin/env python3
"""
Script para injetar um agendamento de teste para testar o sistema de alertas
"""

import sys
import os
from datetime import datetime, timedelta
import uuid

# Adicionar o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(__file__))

from database import Database

def injetar_agendamento_teste():
    """Injeta um agendamento de teste para hoje"""
    db = Database()
    
    try:
        # Buscar um paciente existente
        pacientes = db.obter_todos_pacientes()
        
        if not pacientes:
            print("[ERRO] Nenhum paciente encontrado no banco de dados!")
            print("Por favor, cadastre pelo menos um paciente primeiro.")
            return False
        
        # Usar o primeiro paciente
        paciente = pacientes[0]
        paciente_id = paciente['id']
        nome_paciente = paciente.get('identificacao', {}).get('nome_gestante', 'Paciente Teste')
        
        print(f"[INFO] Usando paciente: {nome_paciente} (ID: {paciente_id})")
        
        # Data de hoje
        hoje = datetime.now()
        data_consulta = hoje.strftime('%Y-%m-%d')
        
        # Hora futura (2 horas a partir de agora, ou 14:00 se já passou das 14h)
        hora_atual = hoje.hour
        if hora_atual < 14:
            hora_consulta = "14:00"
        else:
            # Se já passou das 14h, usar 2 horas a partir de agora
            hora_futura = hoje + timedelta(hours=2)
            hora_consulta = hora_futura.strftime('%H:%M')
        
        # Criar ID único para o agendamento
        agendamento_id = str(uuid.uuid4())
        
        # Criar agendamento
        resultado = db.criar_agendamento(
            agendamento_id=agendamento_id,
            paciente_id=paciente_id,
            data_consulta=data_consulta,
            hora_consulta=hora_consulta,
            tipo_consulta='consulta_pre_natal',
            observacoes='Agendamento de teste para sistema de alertas',
            status='agendado'
        )
        
        if resultado['success']:
            print(f"[OK] Agendamento criado com sucesso!")
            print(f"   Data: {data_consulta}")
            print(f"   Hora: {hora_consulta}")
            print(f"   Paciente: {nome_paciente}")
            print(f"   Tipo: Consulta Pre-Natal")
            print(f"   ID: {agendamento_id}")
            print(f"\n[INFO] O alerta deve aparecer na pagina de agendamentos!")
            return True
        else:
            print(f"[ERRO] Erro ao criar agendamento: {resultado['message']}")
            return False
            
    except Exception as e:
        print(f"[ERRO] Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Injetando Agendamento de Teste")
    print("=" * 60)
    print()
    
    sucesso = injetar_agendamento_teste()
    
    print()
    print("=" * 60)
    if sucesso:
        print("[OK] Processo concluido com sucesso!")
    else:
        print("[ERRO] Processo concluido com erros.")
    print("=" * 60)
