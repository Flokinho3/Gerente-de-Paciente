"""
Script de teste para sincronização de bancos de dados
Testa as funcionalidades de sincronização entre servidores
"""
import requests
import json
import sys
from datetime import datetime

# Configurações
LOCAL_URL = "http://127.0.0.1:5000"
REMOTE_URL = None  # Será detectado automaticamente ou pode ser configurado

def print_section(title):
    """Imprime um cabeçalho de seção"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_success(message):
    """Imprime mensagem de sucesso"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime mensagem de erro"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {message}")

def test_server_connection(url):
    """Testa conexão com o servidor"""
    try:
        response = requests.get(f"{url}/api/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        return False, None
    except Exception as e:
        return False, str(e)

def test_discover_servers(base_url):
    """Testa descoberta de servidores na rede"""
    print_section("Teste 1: Descobrir Servidores")
    
    try:
        response = requests.get(f"{base_url}/api/sync/discover", timeout=30)
        
        if response.status_code != 200:
            print_error(f"Erro ao descobrir servidores: {response.status_code}")
            return None
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"Falha na descoberta: {data.get('message', 'Erro desconhecido')}")
            return None
        
        print_success(f"Servidor local: {data.get('local_ip')}:{data.get('port')}")
        
        servers = data.get('servers', [])
        if servers:
            print_success(f"Encontrados {len(servers)} servidor(es) na rede:")
            for i, server in enumerate(servers, 1):
                print_info(f"  {i}. {server.get('hostname', 'Desconhecido')} - {server.get('ip')}:{server.get('port')}")
        else:
            print_info("Nenhum servidor adicional encontrado na rede")
            print_info("Nota: Certifique-se de que outro servidor está rodando na mesma rede")
        
        return servers[0] if servers else None
        
    except Exception as e:
        print_error(f"Erro ao descobrir servidores: {str(e)}")
        return None

def test_get_sync_data(url):
    """Testa obtenção de dados para sincronização"""
    print_section("Teste 2: Obter Dados para Sincronização")
    
    try:
        response = requests.get(f"{url}/api/sync/data", timeout=10)
        
        if response.status_code != 200:
            print_error(f"Erro ao obter dados: {response.status_code}")
            return None
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"Falha ao obter dados: {data.get('message', 'Erro desconhecido')}")
            return None
        
        pacientes = data.get('pacientes', [])
        agendamentos = data.get('agendamentos', [])
        
        print_success(f"Dados obtidos com sucesso:")
        print_info(f"  - Pacientes: {len(pacientes)}")
        print_info(f"  - Agendamentos: {len(agendamentos)}")
        
        return data
        
    except Exception as e:
        print_error(f"Erro ao obter dados: {str(e)}")
        return None

def test_sync_merge(base_url, sync_data):
    """Testa merge de dados de sincronização"""
    print_section("Teste 3: Sincronizar Dados (Merge)")
    
    try:
        # Preparar dados para sincronização
        payload = {
            'pacientes': sync_data.get('pacientes', []),
            'agendamentos': sync_data.get('agendamentos', [])
        }
        
        response = requests.post(
            f"{base_url}/api/sync/merge",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code != 200:
            print_error(f"Erro ao sincronizar: {response.status_code}")
            print_error(f"Resposta: {response.text}")
            return None
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"Falha na sincronização: {data.get('message', 'Erro desconhecido')}")
            return None
        
        stats = data.get('stats', {})
        pacientes_removidos = data.get('pacientes_removidos', [])
        
        print_success("Sincronização concluída com sucesso!")
        print_info(f"  - Pacientes adicionados: {stats.get('pacientes_adicionados', 0)}")
        print_info(f"  - Pacientes atualizados: {stats.get('pacientes_atualizados', 0)}")
        print_info(f"  - Agendamentos adicionados: {stats.get('agendamentos_adicionados', 0)}")
        print_info(f"  - Agendamentos atualizados: {stats.get('agendamentos_atualizados', 0)}")
        
        if pacientes_removidos:
            print_info(f"  - Pacientes removidos detectados: {len(pacientes_removidos)}")
            print_info("  Lista de pacientes removidos:")
            for paciente in pacientes_removidos[:5]:  # Mostrar apenas os 5 primeiros
                nome = paciente.get('nome_gestante', 'Sem nome')
                print_info(f"    - {nome} (ID: {paciente.get('id', 'N/A')})")
            if len(pacientes_removidos) > 5:
                print_info(f"    ... e mais {len(pacientes_removidos) - 5} paciente(s)")
        
        return data
        
    except Exception as e:
        print_error(f"Erro ao sincronizar: {str(e)}")
        import traceback
        print_error(f"Traceback: {traceback.format_exc()}")
        return None

def test_remove_patients(base_url, paciente_ids):
    """Testa remoção de pacientes após confirmação"""
    print_section("Teste 4: Remover Pacientes")
    
    if not paciente_ids:
        print_info("Nenhum paciente para remover (teste ignorado)")
        return True
    
    try:
        payload = {
            'paciente_ids': paciente_ids[:3]  # Remover apenas os 3 primeiros para teste
        }
        
        print_info(f"Removendo {len(payload['paciente_ids'])} paciente(s)...")
        
        response = requests.post(
            f"{base_url}/api/sync/remover_pacientes",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code != 200:
            print_error(f"Erro ao remover pacientes: {response.status_code}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print_error(f"Falha ao remover: {data.get('message', 'Erro desconhecido')}")
            return False
        
        removidos = data.get('removidos', 0)
        print_success(f"{removidos} paciente(s) removido(s) com sucesso!")
        
        return True
        
    except Exception as e:
        print_error(f"Erro ao remover pacientes: {str(e)}")
        return False

def test_full_sync_flow(local_url, remote_url=None):
    """Testa o fluxo completo de sincronização"""
    print_section("TESTE COMPLETO DE SINCRONIZAÇÃO")
    
    # Verificar conexão com servidor local
    print_info("Verificando conexão com servidor local...")
    connected, data = test_server_connection(local_url)
    if not connected:
        print_error(f"Não foi possível conectar ao servidor local: {data}")
        print_error("Certifique-se de que o servidor Flask está rodando!")
        return False
    
    if isinstance(data, dict):
        print_success(f"Servidor local conectado - Versão: {data.get('version', 'N/A')}")
    
    # Teste 1: Descobrir servidores
    remote_server = test_discover_servers(local_url)
    
    # Se não encontrou servidor remoto e foi fornecido manualmente, usar esse
    if not remote_server and remote_url:
        remote_server = {'ip': remote_url.split('//')[1].split(':')[0], 'port': int(remote_url.split(':')[-1])}
        print_info(f"Usando servidor remoto manual: {remote_url}")
    
    # Teste 2: Obter dados do servidor remoto (se disponível)
    if remote_server:
        remote_url_full = f"http://{remote_server['ip']}:{remote_server['port']}"
        print_info(f"\nConectando ao servidor remoto: {remote_url_full}")
        
        remote_data = test_get_sync_data(remote_url_full)
        
        if remote_data:
            # Teste 3: Sincronizar dados
            sync_result = test_sync_merge(local_url, remote_data)
            
            if sync_result:
                pacientes_removidos = sync_result.get('pacientes_removidos', [])
                if pacientes_removidos:
                    # Perguntar se deseja testar remoção
                    print_section("Teste 4: Remover Pacientes Removidos")
                    resposta = input(f"Deseja testar a remoção de {len(pacientes_removidos)} paciente(s)? (s/n): ")
                    if resposta.lower() == 's':
                        paciente_ids = [p.get('id') for p in pacientes_removidos]
                        test_remove_patients(local_url, paciente_ids)
                    else:
                        print_info("Teste de remoção ignorado pelo usuário")
        else:
            print_error("Não foi possível obter dados do servidor remoto")
    else:
        print_info("\n⚠️  Nenhum servidor remoto encontrado para sincronização completa")
        print_info("Para testar sincronização completa:")
        print_info("  1. Inicie outro servidor em outro PC ou porta diferente")
        print_info("  2. Execute este script novamente")
        print_info("\nTestando apenas merge local...")
        
        # Obter dados locais para teste
        local_data = test_get_sync_data(local_url)
        if local_data:
            test_sync_merge(local_url, local_data)
    
    print_section("TESTE CONCLUÍDO")
    print_success("Todos os testes foram executados!")
    
    return True

def main():
    """Função principal"""
    print("="*60)
    print("  SCRIPT DE TESTE - SINCRONIZAÇÃO DE BANCOS DE DADOS")
    print("="*60)
    
    # Obter URLs dos argumentos ou usar padrões
    local_url = sys.argv[1] if len(sys.argv) > 1 else LOCAL_URL
    remote_url = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"\nConfiguração:")
    print(f"  Servidor Local: {local_url}")
    if remote_url:
        print(f"  Servidor Remoto: {remote_url}")
    else:
        print(f"  Servidor Remoto: Auto-detectar")
    
    # Executar testes
    try:
        test_full_sync_flow(local_url, remote_url)
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print_error(f"Erro fatal: {str(e)}")
        import traceback
        print_error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
