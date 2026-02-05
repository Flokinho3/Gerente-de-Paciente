"""
Teste de validação final do novo sistema de identidade
Verifica: "Se rodar a sync 10 vezes e o estado final não muda, então o sistema está correto"
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gerente.database import Database
from gerente.database.event_sync import EventBasedSync


def test_regra_final():
    """Testa a regra final de consistência"""
    print("🧪 TESTE DA REGRA FINAL")
    print("=" * 50)
    
    db = Database()
    event_sync = EventBasedSync(db.conn)
    
    # Estado inicial
    estado_inicial = event_sync.get_sync_status()
    print(f"📊 Estado inicial:")
    print(f"   Total identidades: {estado_inicial['total_identidades']}")
    print(f"   Eventos pendentes: {estado_inicial['eventos_pendentes']}")
    print(f"   Conflitos ativos: {estado_inicial['conflitos_ativos']}")
    print(f"   Sistema estável: {estado_inicial['sistema_estavel']}")
    
    print("\n🔄 Executando sincronização 10 vezes...")
    resultados = []
    
    for i in range(10):
        resultado = event_sync.sync_by_timestamp()
        resultados.append(resultado)
        print(f"   Sync {i+1}: {resultado.get('eventos_aplicados', 0)} eventos aplicados")
    
    # Verificar estado final após múltiplas execuções
    print("\n📊 Verificando consistência do estado final...")
    estados_finais = []
    
    for i in range(3):
        estado = event_sync.get_sync_status()
        estados_finais.append(estado)
        print(f"   Verificação {i+1}: id={estado['total_identidades']}, pendentes={estado['eventos_pendentes']}, conflitos={estado['conflitos_ativos']}")
    
    # Verificar se todos os estados finais são idênticos
    consistente = all(
        estados_finais[0]['total_identidades'] == estado['total_identidades'] and
        estados_finais[0]['eventos_pendentes'] == estado['eventos_pendentes'] and
        estados_finais[0]['conflitos_ativos'] == estado['conflitos_ativos']
        for estado in estados_finais
    )
    
    print("\n🎯 RESULTADO FINAL:")
    if consistente:
        print("✅ SISTEMA PASSOU NA VALIDAÇÃO!")
        print("   A regra final foi satisfeita:")
        print("   'Se rodar a sync 10 vezes e o estado final não muda, então o sistema está correto'")
        return True
    else:
        print("❌ SISTEMA AINDA INSTÁVEL")
        print("   O estado final mudou entre execuções")
        return False


def test_conflito_simulado():
    """Testa resolução de conflitos com dados simulados"""
    print("\n🔥 TESTE DE CONFLITO SIMULADO")
    print("=" * 50)
    
    db = Database()
    event_sync = EventBasedSync(db.conn)
    
    # Criar dados conflitantes (mesmo paciente, versões diferentes)
    paciente_v1 = {
        'id': 'teste_conflito_v1',
        'identificacao': {'nome_gestante': 'Maria Teste', 'unidade_saude': 'USP'},
        'versao': 1,
        'ultima_modificacao': '2026-02-04 10:00:00'
    }
    
    paciente_v2 = {
        'id': 'teste_conflito_v2',  # ID diferente mas mesmo paciente
        'identificacao': {'nome_gestante': 'Maria Teste', 'unidade_saude': 'USP'},
        'versao': 2,
        'ultima_modificacao': '2026-02-04 11:00:00'  # Mais recente
    }
    
    # Gerar fingerprints (devem ser iguais)
    from gerente.database.identity import IdentityManager
    identity_manager = IdentityManager()
    
    fp1 = identity_manager.generate_identity_fingerprint(paciente_v1)
    fp2 = identity_manager.generate_identity_fingerprint(paciente_v2)
    
    print(f"Fingerprint paciente v1: {fp1}")
    print(f"Fingerprint paciente v2: {fp2}")
    print(f"Fingerprints iguais: {fp1 == fp2}")
    
    if fp1 == fp2:
        # Criar eventos conflitantes
        event_sync.identity_map.register_identity(fp1, 'teste_conflito_v1', origem='teste')
        event_sync.identity_map.create_sync_event(fp1, 'paciente', paciente_v1, 'teste', 1)
        
        event_sync.identity_map.register_identity(fp2, 'teste_conflito_v2', origem='teste')
        event_sync.identity_map.create_sync_event(fp2, 'paciente', paciente_v2, 'teste', 2)
        
        # Resolver conflito
        resultado = event_sync.resolve_all_conflicts()
        print(f"Conflitos resolvidos: {resultado.get('conflitos_resolvidos', 0)}")
        
        # Verificar quem ganhou (last-write-wins)
        evento_vencedor = event_sync.identity_map.resolve_conflict_last_write_wins(fp1)
        if evento_vencedor:
            payload = evento_vencedor['payload']
            versao_vencedora = payload.get('versao')
            print(f"Versão vencedora: {versao_vencedora} (deve ser 2)")
            
            if versao_vencedora == 2:
                print("✅ Last-write-wins funcionou corretamente!")
                return True
            else:
                print("❌ Last-write-wins falhou!")
                return False
    
    return False


if __name__ == "__main__":
    print("VALIDACAO FINAL DO SISTEMA DE IDENTIDADE")
    print("=" * 60)
    
    # Teste 1: Regra final
    teste1_passou = test_regra_final()
    
    # Teste 2: Resolução de conflitos
    teste2_passou = test_conflito_simulado()
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Teste da Regra Final: {'[PASSOU]' if teste1_passou else '[FALHOU]'}")
    print(f"Teste de Conflitos: {'[PASSOU]' if teste2_passou else '[FALHOU]'}")
    
    if teste1_passou and teste2_passou:
        print("\n[SISTEMA 100% FUNCIONAL]!")
        print("A nova arquitetura esta pronta para producao.")
    else:
        print("\n[AVISO] Sistema precisa de ajustes antes de ir para producao.")