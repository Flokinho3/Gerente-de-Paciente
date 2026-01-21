# Comportamento dos Bancos de Dados com Múltiplos Servidores

## Situação Atual

Com a configuração padrão, **cada servidor em um PC diferente terá seu próprio banco de dados SQLite isolado**. Isso significa que:

- ✅ **Servidor 1 (PC 1)**: Banco em `data/pacientes.db` → dados próprios
- ✅ **Servidor 2 (PC 2)**: Banco em `data/pacientes.db` → dados próprios (diferentes do PC 1)

### Problemas com esta Abordagem

1. **Dados não sincronizados**: Alterações em um servidor não aparecem no outro
2. **Conflitos de dados**: Pacientes podem ser criados em ambos com o mesmo nome mas IDs diferentes
3. **Estatísticas inconsistentes**: Relatórios e estatísticas serão diferentes em cada servidor
4. **Perda de dados**: Se um servidor falhar, os dados locais podem ser perdidos

## Soluções Disponíveis

### Opção 1: Banco de Dados Compartilhado via Rede (NÃO RECOMENDADO)

Você pode configurar ambos os servidores para usar o mesmo arquivo SQLite compartilhado em uma pasta de rede:

#### Configuração Windows:

1. Compartilhe uma pasta na rede (ex: `\\SERVIDOR\banco_dados`)
2. No arquivo `.env` de ambos os servidores, configure:
   ```
   DB_PATH=\\SERVIDOR\banco_dados\pacientes.db
   ```
   ou se mapeado como unidade:
   ```
   DB_PATH=Z:\banco_dados\pacientes.db
   ```

#### Configuração Linux/Mac:

1. Monte um compartilhamento de rede
2. No arquivo `.env` de ambos os servidores:
   ```
   DB_PATH=/mnt/rede/pacientes.db
   ```

**⚠️ AVISOS IMPORTANTES:**
- SQLite via rede é **lento** e pode causar **bloqueios**
- Apenas **um servidor** deve escrever por vez (leitura simultânea funciona melhor)
- Pode causar **corrupção de dados** se houver muitos acessos simultâneos
- **Não é recomendado para produção**

### Opção 2: Sincronização Manual/Periódica (RECOMENDADO)

Manter bancos locais e sincronizar periodicamente usando a funcionalidade de exportar/importar:

1. **Servidor Principal**: Mantém o banco "oficial"
2. **Servidores Secundários**: Exportam seus dados periodicamente
3. **Servidor Principal**: Importa os dados dos secundários (mesclando/atualizando)

**Vantagens:**
- ✅ Cada servidor funciona independentemente (resiliência)
- ✅ Não há dependência de rede para operação normal
- ✅ Menos risco de corrupção de dados

**Desvantagens:**
- ❌ Não é em tempo real (dados podem estar desatualizados)
- ❌ Requer processo manual de sincronização

### Opção 3: Banco de Dados Centralizado (RECOMENDADO PARA PRODUÇÃO)

Migrar para PostgreSQL ou MySQL em um servidor central:

1. **Servidor Central**: Roda PostgreSQL/MySQL
2. **Todos os servidores**: Conectam-se ao banco central via rede

**Vantagens:**
- ✅ Dados sempre sincronizados em tempo real
- ✅ Suporta múltiplos acessos simultâneos
- ✅ Melhor performance e confiabilidade
- ✅ Transações ACID garantidas

**Desvantagens:**
- ❌ Requer servidor dedicado para o banco
- ❌ Requer modificação do código (`database.py`)
- ❌ Maior complexidade de configuração

## Recomendação

Para cenários de **2 servidores em PCs diferentes**:

1. **Curto Prazo**: Use a **Opção 2** (sincronização periódica)
   - Configure um servidor como "principal"
   - Faça sincronização manual diária/semanal usando export/import

2. **Longo Prazo**: Considere a **Opção 3** (banco centralizado)
   - Melhor solução para múltiplos servidores
   - Escalável e confiável

3. **Evite**: A **Opção 1** (SQLite compartilhado)
   - Apenas se for realmente necessário e com baixo tráfego

## Como Configurar

### Para usar banco compartilhado (Opção 1):

1. Edite o arquivo `.env` em ambos os PCs
2. Configure `DB_PATH` apontando para o mesmo arquivo na rede
3. Reinicie ambos os servidores

### Para sincronização (Opção 2):

1. Use a funcionalidade de **Exportar** no servidor secundário
2. Use a funcionalidade de **Importar/Restaurar** no servidor principal
3. Repita periodicamente conforme necessário

## Notas Técnicas

- O código agora suporta `DB_PATH` via variável de ambiente
- WAL mode está habilitado para melhor concorrência (quando suportado)
- Timeout aumentado para 30 segundos para bancos em rede
- O sistema detecta automaticamente se é caminho local ou de rede
