"""
Sincronização de dados entre servidores (modo duplo).
"""
import json
import urllib.request


def sincronizar_servidores(porta_origem, porta_destino):
    """Sincroniza dados entre dois servidores"""
    try:
        print(f"Sincronizando servidor {porta_origem} -> {porta_destino}...")

        url_data = f'http://127.0.0.1:{porta_origem}/api/sync/data'
        req_data = urllib.request.Request(url_data)
        response_data = urllib.request.urlopen(req_data, timeout=10)
        sync_data = json.loads(response_data.read().decode())

        if not sync_data.get('success'):
            print(f"ERRO: Não foi possível obter dados do servidor {porta_origem}")
            return False

        url_merge = f'http://127.0.0.1:{porta_destino}/api/sync/merge'
        data_json = json.dumps({
            'pacientes': sync_data.get('pacientes', []),
            'agendamentos': sync_data.get('agendamentos', [])
        }).encode('utf-8')

        req_merge = urllib.request.Request(
            url_merge,
            data=data_json,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response_merge = urllib.request.urlopen(req_merge, timeout=30)
        merge_result = json.loads(response_merge.read().decode())

        if merge_result.get('success'):
            stats = merge_result.get('stats', {})
            print(f"SUCESSO: Sincronização {porta_origem} -> {porta_destino} concluída")
            print(f"  - Pacientes adicionados: {stats.get('pacientes_adicionados', 0)}")
            print(f"  - Pacientes atualizados: {stats.get('pacientes_atualizados', 0)}")
            print(f"  - Agendamentos adicionados: {stats.get('agendamentos_adicionados', 0)}")
            print(f"  - Agendamentos atualizados: {stats.get('agendamentos_atualizados', 0)}")
            return True

        print(f"ERRO: Falha na sincronização: {merge_result.get('message', 'Erro desconhecido')}")
        return False

    except Exception as e:
        print(f"ERRO ao sincronizar servidores: {e}")
        return False
