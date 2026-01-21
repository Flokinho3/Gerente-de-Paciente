# Guia de Teste - Sincronização de Bancos de Dados

Este guia explica como usar o script de teste `test_sync.py` para testar a funcionalidade de sincronização entre servidores.

## Pré-requisitos

1. Instalar a biblioteca `requests` (se ainda não estiver instalada):
```bash
pip install requests
```

2. Certifique-se de que o servidor Flask está rodando:
```bash
python main.py
```

## Uso Básico

### Executar testes básicos:
```bash
python test_sync.py
```

O script irá:
- Testar conexão com o servidor local
- Tentar descobrir outros servidores na rede
- Executar testes de sincronização

### Especificar servidor local customizado:
```bash
python test_sync.py http://127.0.0.1:5000
```

### Especificar servidor local e remoto:
```bash
python test_sync.py http://127.0.0.1:5000 http://192.168.1.100:5000
```

## Cenários de Teste

### Cenário 1: Teste Local (Um servidor)
```bash
python test_sync.py
```

Testa:
- ✅ Conexão com servidor local
- ✅ Obtenção de dados para sincronização
- ✅ Merge de dados (mesclando consigo mesmo)

**Resultado esperado:** Dados mesclados com sucesso, sem pacientes novos ou removidos.

### Cenário 2: Teste com Dois Servidores

**Passo 1:** Inicie o primeiro servidor (PC 1):
```bash
python main.py
```

**Passo 2:** Inicie o segundo servidor (PC 2) em outra máquina ou porta:
```bash
# Em outra máquina ou terminal
python main.py
# Ou configure PORT=5001 no .env
```

**Passo 3:** Execute o teste no PC 1:
```bash
python test_sync.py
```

**Passo 4:** Execute o teste no PC 2:
```bash
python test_sync.py http://IP_DO_PC_2:5000
```

**Resultado esperado:**
- ✅ Descoberta de servidores na rede
- ✅ Sincronização bidirecional de dados
- ✅ Detecção de pacientes removidos (se houver)
- ✅ Opção de remover pacientes removidos em outro servidor

## Testes Realizados

O script executa os seguintes testes:

### Teste 1: Descobrir Servidores
- Envia requisição para `/api/sync/discover`
- Verifica se encontra outros servidores na rede local
- Lista servidores encontrados

### Teste 2: Obter Dados para Sincronização
- Envia requisição para `/api/sync/data`
- Obtém lista de pacientes e agendamentos
- Verifica estrutura dos dados retornados

### Teste 3: Sincronizar Dados (Merge)
- Envia dados remotos para `/api/sync/merge`
- Verifica adição de novos pacientes
- Verifica atualização de pacientes existentes
- Verifica detecção de pacientes removidos

### Teste 4: Remover Pacientes
- Remove pacientes após confirmação
- Envia requisição para `/api/sync/remover_pacientes`
- Verifica remoção bem-sucedida

## Exemplo de Saída

```
============================================================
  TESTE COMPLETO DE SINCRONIZAÇÃO
============================================================
ℹ️  Verificando conexão com servidor local...
✅ Servidor local conectado - Versão: 1.0.2

============================================================
  Teste 1: Descobrir Servidores
============================================================
✅ Servidor local: 192.168.1.50:5000
✅ Encontrados 1 servidor(es) na rede:
ℹ️   1. PC-SECUNDARIO - 192.168.1.100:5000

============================================================
  Teste 2: Obter Dados para Sincronização
============================================================
✅ Dados obtidos com sucesso:
ℹ️    - Pacientes: 15
ℹ️    - Agendamentos: 8

============================================================
  Teste 3: Sincronizar Dados (Merge)
============================================================
✅ Sincronização concluída com sucesso!
ℹ️    - Pacientes adicionados: 5
ℹ️    - Pacientes atualizados: 3
ℹ️    - Agendamentos adicionados: 2
ℹ️    - Agendamentos atualizados: 1
ℹ️    - Pacientes removidos detectados: 2
ℹ️    Lista de pacientes removidos:
ℹ️      - Maria Silva (ID: Maria_Silva_20240115_143022)
ℹ️      - João Santos (ID: Joao_Santos_20240114_091530)

============================================================
  Teste 4: Remover Pacientes Removidos
============================================================
Deseja testar a remoção de 2 paciente(s)? (s/n): s
ℹ️  Removendo 2 paciente(s)...
✅ 2 paciente(s) removido(s) com sucesso!

============================================================
TESTE CONCLUÍDO
============================================================
✅ Todos os testes foram executados!
```

## Solução de Problemas

### Erro: "Não foi possível conectar ao servidor local"
- **Causa:** Servidor Flask não está rodando
- **Solução:** Inicie o servidor com `python main.py`

### Erro: "Nenhum servidor adicional encontrado na rede"
- **Causa:** Outro servidor não está rodando ou não está na mesma rede
- **Solução:** 
  1. Verifique se outro servidor está rodando
  2. Verifique se ambos estão na mesma rede local
  3. Verifique firewall/antivírus que possam bloquear conexões

### Erro: "Erro ao sincronizar: Timeout"
- **Causa:** Rede lenta ou servidor remoto não responde
- **Solução:** 
  1. Aumente o timeout no script (linha `timeout=30`)
  2. Verifique conexão de rede
  3. Verifique se o servidor remoto está acessível

### Erro: "requests module not found"
- **Causa:** Biblioteca requests não instalada
- **Solução:** Execute `pip install requests`

## Testes Manuais na Interface Web

Também é possível testar através da interface web:

1. Acesse `http://localhost:5000/bd`
2. Clique no botão "🔄 Sincronizar BD"
3. Clique em "🔍 Descobrir Servidores"
4. Selecione um servidor encontrado
5. Aguarde a sincronização
6. Se houver pacientes removidos, selecione e confirme a remoção

## Notas Importantes

- ⚠️ **Cuidado:** O teste de remoção remove dados reais do banco de dados
- ✅ Sempre faça backup antes de testar remoções
- 🔒 O script usa apenas requisições HTTP, não acessa diretamente o banco de dados
- 🌐 A descoberta de servidores funciona apenas na mesma rede local (mesma sub-rede)
