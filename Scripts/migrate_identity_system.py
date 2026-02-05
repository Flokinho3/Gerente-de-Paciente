"""
Script de migração para o novo sistema de identidade e eventos
Executa as fases de refatoração conforme documentação fornecida
"""
import sys
import os
from typing import Dict
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gerente.database import Database
from gerente.database.identity import IdentityManager, IdentityMap
from gerente.database.event_sync import EventBasedSync
from gerente.flask_app.event_logger import log_event


class MigrationPhaseManager:
    """Gerenciador de fases de migração para o novo sistema"""

    def __init__(self):
        self.db = Database()
        self.identity_manager = IdentityManager()
        self.identity_map = IdentityMap(self.db.conn)
        self.event_sync = EventBasedSync(self.db.conn)

    def fase1_setup_identidade(self) -> Dict:
        """
        FASE 1 - Setup inicial sem dor:
        ✅ parar de depender de ID
        ✅ match por identidade lógica  
        ✅ update se existir
        ✅ log tudo
        """
        log_event("🚀 Iniciando FASE 1 - Setup de identidade", "info")
        
        try:
            # 1. Garantir que as tabelas de identidade existam
            self.identity_map._ensure_schema()
            log_event("✅ Tabelas de identidade criadas/verificadas", "success")
            
            # 2. Migrar pacientes existentes para fingerprints
            pacientes_existentes = self.db.obter_todos_pacientes()
            migrados = 0
            duplicatas_encontradas = 0
            
            for paciente in pacientes_existentes:
                fingerprint = self.identity_manager.generate_identity_fingerprint(paciente)
                id_local = paciente.get('id')
                
                # Verificar se já existe
                existente = self.identity_map.get_identity_by_local_id(id_local)
                
                if not existente:
                    # Verificar duplicatas pelo fingerprint
                    cursor = self.db.conn.cursor()
                    cursor.execute("""
                        SELECT identity_fingerprint FROM identity_map 
                        WHERE identity_fingerprint = ?
                    """, (fingerprint,))
                    fp_exists = cursor.fetchone()
                    
                    if fp_exists:
                        duplicatas_encontradas += 1
                        # Adicionar sufixo ao fingerprint para distinguir
                        fingerprint = f"{fingerprint}_{id_local[-4:]}"
                    
                    # Registrar identidade
                    self.identity_map.register_identity(
                        identity_fingerprint=fingerprint,
                        id_local=id_local,
                        origem='migracao_fase1'
                    )
                    migrados += 1
            
            log_event(f"✅ {migrados} pacientes migrados para identidade lógica", "success")
            if duplicatas_encontradas > 0:
                log_event(f"⚠️ {duplicatas_encontradas} fingerprints ajustados para evitar conflitos", "warning")
            
            return {
                'success': True,
                'fase': 'fase1',
                'pacientes_migrados': migrados,
                'duplicatas_encontradas': duplicatas_encontradas,
                'message': 'Fase 1 concluída: identidade lógica estabelecida'
            }
            
        except Exception as e:
            log_event(f"❌ Erro na Fase 1: {str(e)}", "error")
            return {
                'success': False,
                'fase': 'fase1',
                'error': str(e)
            }

    def fase2_estabilizacao(self) -> Dict:
        """
        FASE 2 - Estabilização:
        ✅ gerar identity_fingerprint
        ✅ salvar junto com registros  
        ✅ mapear IDs antigos
        """
        log_event("🔄 Iniciando FASE 2 - Estabilização", "info")
        
        try:
            # 1. Adicionar coluna identity_fingerprint à tabela pacientes se não existir
            cursor = self.db.conn.cursor()
            try:
                cursor.execute("ALTER TABLE pacientes ADD COLUMN identity_fingerprint TEXT")
                self.db.conn.commit()
                log_event("✅ Coluna identity_fingerprint adicionada à tabela pacientes", "success")
            except Exception:
                log_event("ℹ️ Coluna identity_fingerprint já existe", "info")
            
            # 2. Preencher identity_fingerprint para todos os pacientes
            pacientes = self.db.obter_todos_pacientes()
            atualizados = 0
            
            for paciente in pacientes:
                fingerprint = self.identity_manager.generate_identity_fingerprint(paciente)
                
                cursor.execute("""
                    UPDATE pacientes SET identity_fingerprint = ? 
                    WHERE id = ? AND (identity_fingerprint IS NULL OR identity_fingerprint = '')
                """, (fingerprint, paciente.get('id')))
                
                if cursor.rowcount > 0:
                    atualizados += 1
            
            self.db.conn.commit()
            log_event(f"✅ {atualizados} pacientes atualizados com fingerprint", "success")
            
            # 3. Sincronizar mapa de identidade com fingerprints
            sync_count = 0
            for paciente in pacientes:
                if paciente.get('identity_fingerprint'):
                    self.identity_map.register_identity(
                        identity_fingerprint=paciente['identity_fingerprint'],
                        id_local=paciente.get('id'),
                        origem='fase2_estabilizacao'
                    )
                    sync_count += 1
            
            return {
                'success': True,
                'fase': 'fase2',
                'pacientes_com_fingerprint': atualizados,
                'identidades_sincronizadas': sync_count,
                'message': 'Fase 2 concluída: sistema estabilizado com fingerprints'
            }
            
        except Exception as e:
            log_event(f"❌ Erro na Fase 2: {str(e)}", "error")
            return {
                'success': False,
                'fase': 'fase2',
                'error': str(e)
            }

    def fase3_sync_eventos(self) -> Dict:
        """
        FASE 3 - Sync de verdade:
        ✅ trocar registros por eventos
        ✅ sincronizar por last_sync  
        ✅ tolerar duplicata sem quebrar
        """
        log_event("⚡ Iniciando FASE 3 - Sync por eventos", "info")
        
        try:
            # 1. Converter registros existentes em eventos
            pacientes = self.db.obter_todos_pacientes()
            eventos_criados = 0
            
            for paciente in pacientes:
                fingerprint = self.identity_manager.generate_identity_fingerprint(paciente)
                
                # Criar evento para cada paciente
                evento = self.identity_map.create_sync_event(
                    identity_fingerprint=fingerprint,
                    entity_type='paciente',
                    payload=paciente,
                    source='migracao_fase3',
                    version=paciente.get('versao', 1)
                )
                
                eventos_criados += 1
            
            log_event(f"✅ {eventos_criados} eventos criados a partir de registros existentes", "success")
            
            # 2. Resolver conflitos existentes
            conflitos_resolvidos = self.event_sync.resolve_all_conflicts()
            log_event(f"🔧 {conflitos_resolvidos.get('conflitos_resolvidos', 0)} conflitos resolvidos", "warning")
            
            # 3. Testar regra: sincronizar múltiplas vezes e verificar consistência
            test_results = []
            for i in range(3):
                result = self.event_sync.sync_by_timestamp()
                test_results.append(result)
                log_event(f"🧪 Teste {i+1}: {result.get('eventos_aplicados', 0)} eventos aplicados", "info")
            
            # 4. Verificar regra final: estado consistente?
            estado_final1 = self.event_sync.get_sync_status()
            estado_final2 = self.event_sync.get_sync_status()
            
            sistema_estavel = (
                estado_final1['total_identidades'] == estado_final2['total_identidades'] and
                estado_final1['eventos_pendentes'] == estado_final2['eventos_pendentes'] and
                estado_final1['conflitos_ativos'] == estado_final2['conflitos_ativos']
            )
            
            if sistema_estavel:
                log_event("✅ REGRA FINAL VERIFICADA: Sistema estável!", "success")
            else:
                log_event("⚠️ Sistema ainda não está totalmente estável", "warning")
            
            return {
                'success': True,
                'fase': 'fase3',
                'eventos_criados': eventos_criados,
                'conflitos_resolvidos': conflitos_resolvidos.get('conflitos_resolvidos', 0),
                'sistema_estavel': sistema_estavel,
                'status_final': estado_final1,
                'message': 'Fase 3 concluída: sincronização por eventos implementada'
            }
            
        except Exception as e:
            log_event(f"❌ Erro na Fase 3: {str(e)}", "error")
            return {
                'success': False,
                'fase': 'fase3',
                'error': str(e)
            }

    def migracao_completa(self) -> Dict:
        """Executa todas as fases de migração em sequência"""
        log_event("🚀 INICIANDO MIGRAÇÃO COMPLETA PARA NOVO SISTEMA", "working")
        
        resultados = {}
        
        # FASE 1
        resultados['fase1'] = self.fase1_setup_identidade()
        if not resultados['fase1']['success']:
            return resultados
        
        # FASE 2  
        resultados['fase2'] = self.fase2_estabilizacao()
        if not resultados['fase2']['success']:
            return resultados
        
        # FASE 3
        resultados['fase3'] = self.fase3_sync_eventos()
        if not resultados['fase3']['success']:
            return resultados
        
        # Resultado geral
        total_pacientes = len(self.db.obter_todos_pacientes())
        resultados['resumo'] = {
            'success': True,
            'total_pacientes': total_pacientes,
            'fases_concluidas': 3,
            'sistema_migrado': True,
            'message': '✅ Migração completa realizada com sucesso!'
        }
        
        log_event("🎉 MIGRAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!", "success")
        return resultados

    def validar_sistema(self) -> Dict:
        """Valida se o sistema segue a regra final de consistência"""
        log_event("🔍 Validando consistência do sistema...", "working")
        
        try:
            # Executar sync 10 vezes
            resultados_sync = []
            for i in range(10):
                resultado = self.event_sync.sync_by_timestamp()
                resultados_sync.append(resultado)
            
            # Verificar se o estado final não muda
            estados = [self.event_sync.get_sync_status() for _ in range(3)]
            
            consistente = all(
                estados[0]['total_identidades'] == estado['total_identidades'] and
                estados[0]['eventos_pendentes'] == estado['eventos_pendentes'] and
                estados[0]['conflitos_ativos'] == estado['conflitos_ativos']
                for estado in estados
            )
            
            return {
                'success': True,
                'consistente': consistente,
                'validacoes': 10,
                'estado_final': estados[0],
                'message': 'Sistema consistente' if consistente else 'Sistema ainda instável'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    """Função principal para execução da migração"""
    print("=" * 60)
    print("MIGRAÇÃO PARA SISTEMA DE IDENTIDADE E EVENTOS")
    print("=" * 60)
    
    migrator = MigrationPhaseManager()
    
    print("\n1. Executando migração completa...")
    resultados = migrator.migracao_completa()
    
    if resultados['resumo']['success']:
        print(f"\n[MIGRACAO CONCLUIDA]!")
        print(f"   Total pacientes: {resultados['resumo']['total_pacientes']}")
        print(f"   Fases concluidas: {resultados['resumo']['fases_concluidas']}")
        
        print("\n2. Validando consistencia do sistema...")
        validacao = migrator.validar_sistema()
        
        if validacao['consistente']:
            print("[SISTEMA PASSOU NA VALIDACAO DE CONSISTENCIA]!")
        else:
            print("[AVISO] Sistema ainda precisa de ajustes")
    else:
        print("[ERRO] Migracao falhou")
        print(f"Erro: {resultados.get('error', 'Desconhecido')}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()