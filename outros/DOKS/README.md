# 📚 Documentação Completa - Gerente de Pacientes

Este documento consolida toda a documentação do projeto **Gerente de Pacientes** em um único arquivo.

---

## 🚀 Início Rápido

### Seu executável está pronto!

```
📁 dist/
   └── 📦 Gerente_de_Pacientes.exe (16-30 MB)
```

### 3 Passos para Usar

1. **Abrir**: Clique duas vezes em `Gerente_de_Pacientes.exe`
2. **Confirmar**: Uma janela aparecerá → Clique em "OK"
3. **Usar**: O navegador abrirá automaticamente em `http://localhost:5000`

### Requisitos

| ✅ Funciona | ❌ Não Precisa |
|------------|---------------|
| Windows 10/11 | Python |
| Navegador web | Instalar bibliotecas |
| Porta 5000 livre | Configuração |

---

## 📦 Como Criar o Executável (.exe)

### Método 1: Script Automático (Recomendado)

```batch
build_exe.bat
```

O script irá:
- ✅ Verificar/instalar dependências
- ✅ Limpar builds anteriores
- ✅ Criar o executável
- ✅ Copiar arquivos necessários
- ✅ Preparar tudo para distribuição

### Método 2: Manual

1. **Instalar PyInstaller:**
   ```batch
   pip install pyinstaller
   ```

2. **Limpar builds anteriores:**
   ```batch
   rmdir /s /q build
   rmdir /s /q dist
   ```

3. **Criar o executável:**
   ```batch
   pyinstaller gerente_pacientes.spec --clean --noconfirm
   ```

### Localização do Executável

```
dist\Gerente_de_Pacientes.exe
```

### Configurações do Build

O arquivo `gerente_pacientes.spec` contém todas as configurações:
- **Modo Console:** Desabilitado (interface sem janela de comando)
- **Arquivos Incluídos:** Templates, static, data
- **Bibliotecas:** Flask, OpenPyXL, python-docx, tkinter
- **Compressão:** UPX habilitado
- **Tipo:** Executável único (--onefile)

---

## 🖥️ Tray Icon - Inicialização Automática

O **tray icon** é iniciado **automaticamente** junto com o `main.py` sempre que possível.

### ✅ Inicia Automaticamente quando:
- Executável (.exe) é executado
- Modo silencioso (`--silent` ou `SILENT_MODE=1`)
- Scripts `iniciar_silencioso.sh` ou `iniciar_background.sh`
- Variável `USE_TRAY=1` está definida
- Argumento `--tray` é passado

### ❌ Não Inicia quando:
- Argumento `--no-tray` é passado
- `pystray` não está instalado (fallback para modo normal)

### Modos de Execução

1. **Execução Normal** (com tray icon automático)
   ```bash
   python3 main.py
   ```

2. **Forçar Tray Icon**
   ```bash
   python3 main.py --tray
   ```

3. **Desabilitar Tray Icon**
   ```bash
   python3 main.py --no-tray
   ```

4. **Modo Silencioso** (sempre com tray)
   ```bash
   python3 main.py --silent
   # ou
   ./iniciar_silencioso.sh
   ```

### Instalação

```bash
# Instalar dependências
pip3 install pystray pillow

# Ou usar o script
./instalar_dependencias.sh
```

### Funcionalidades do Tray Icon

- ✅ **Ícone na Bandeja**: Aparece na área de notificação
- ✅ **Status em Tempo Real**: Mostra se está rodando (🟢) ou parado (🔴)
- ✅ **Porta Visível**: Exibe a porta em uso (padrão: 5000)
- ✅ **Menu de Ações**: 
  - 🌐 Abrir no Navegador
  - 🔄 Reiniciar
  - ❌ Sair

---

## 🚀 Execução Silenciosa - Sem Terminal Visível

### Opções de Execução

1. **Execução Silenciosa com Feedback** (Recomendado)
   ```bash
   ./iniciar_silencioso.sh
   ```
   - ✅ Inicia sem terminal visível
   - ✅ Mostra mensagens de status
   - ✅ Abre navegador automaticamente
   - ✅ Logs salvos em `logs/app.log`

2. **Execução Totalmente em Background**
   ```bash
   ./iniciar_background.sh
   ```
   - ✅ Executa completamente em background
   - ✅ Sem nenhuma janela visível
   - ✅ Ideal para iniciar automaticamente
   - ✅ Logs em `logs/app.log` e `logs/error.log`

3. **Parar Aplicação**
   ```bash
   ./parar.sh
   ```
   - ✅ Encerra a aplicação em background
   - ✅ Limpa arquivos PID

### Estrutura de Logs

```
logs/
├── app.log      # Log geral da aplicação
├── error.log    # Log de erros (apenas background)
└── app.pid      # Arquivo PID (apenas background)
```

### Configuração para Windows (.exe)

O arquivo `gerente_pacientes.spec` já está configurado com `console=False`:
- ✅ Executável não mostra console
- ✅ Execução silenciosa
- ✅ Apenas janela informativa do Tkinter

---

## 📤 Como Distribuir o Aplicativo

### 1️⃣ Distribuição Simples (Arquivo Único)

**Vantagens:**
- ✅ Mais fácil de compartilhar
- ✅ Usuário só precisa baixar um arquivo
- ✅ Funciona imediatamente

**Como fazer:**
```
Compartilhe apenas:
  dist\Gerente_de_Pacientes.exe
```

**Tamanho:** ~25-30 MB

### 2️⃣ Distribuição Completa (com Dados)

**Vantagens:**
- ✅ Inclui banco de dados de exemplo
- ✅ Estrutura de pastas organizada

**Como fazer:**
```
Compartilhe toda a pasta dist/:
  dist\
  ├── Gerente_de_Pacientes.exe
  └── data\
      └── pacientes.db
```

### 3️⃣ Criar Instalador Profissional (Avançado)

Usando **Inno Setup** (Recomendado):
1. Baixe o Inno Setup: https://jrsoftware.org/isinfo.php
2. Crie um script de instalação (`setup.iss`)
3. Compile o instalador

**Resultado:**
- ✅ Instalador profissional (`.exe`)
- ✅ Ícone na área de trabalho
- ✅ Menu Iniciar
- ✅ Desinstalador automático

### 4️⃣ Portabilizar (USB/Pendrive)

1. Copie a pasta `dist` completa para o pendrive
2. Renomeie para algo amigável: `Gerente_Pacientes_Portatil`
3. Crie um atalho para o .exe na raiz

**Vantagens:**
- ✅ Funciona sem instalação
- ✅ Dados ficam no pendrive
- ✅ Use em qualquer computador

### Checklist Antes de Distribuir

**Testes Essenciais:**
- [ ] Testado em máquina limpa (sem Python)
- [ ] Testado no Windows 10
- [ ] Testado no Windows 11
- [ ] Porta 5000 disponível
- [ ] Navegador abre automaticamente
- [ ] Todas as funcionalidades funcionam

---

## 🌐 Múltiplos Servidores

### Situação Atual

Com a configuração padrão, **cada servidor em um PC diferente terá seu próprio banco de dados SQLite isolado**.

### Problemas com esta Abordagem

1. **Dados não sincronizados**: Alterações em um servidor não aparecem no outro
2. **Conflitos de dados**: Pacientes podem ser criados em ambos com o mesmo nome mas IDs diferentes
3. **Estatísticas inconsistentes**: Relatórios e estatísticas serão diferentes em cada servidor
4. **Perda de dados**: Se um servidor falhar, os dados locais podem ser perdidos

### Soluções Disponíveis

#### Opção 1: Banco de Dados Compartilhado via Rede (NÃO RECOMENDADO)

⚠️ **AVISOS IMPORTANTES:**
- SQLite via rede é **lento** e pode causar **bloqueios**
- Apenas **um servidor** deve escrever por vez
- Pode causar **corrupção de dados** se houver muitos acessos simultâneos
- **Não é recomendado para produção**

#### Opção 2: Sincronização Manual/Periódica (RECOMENDADO)

Manter bancos locais e sincronizar periodicamente usando a funcionalidade de exportar/importar.

**Vantagens:**
- ✅ Cada servidor funciona independentemente (resiliência)
- ✅ Não há dependência de rede para operação normal
- ✅ Menos risco de corrupção de dados

**Desvantagens:**
- ❌ Não é em tempo real (dados podem estar desatualizados)
- ❌ Requer processo manual de sincronização

#### Opção 3: Banco de Dados Centralizado (RECOMENDADO PARA PRODUÇÃO)

Migrar para PostgreSQL ou MySQL em um servidor central.

**Vantagens:**
- ✅ Dados sempre sincronizados em tempo real
- ✅ Suporta múltiplos acessos simultâneos
- ✅ Melhor performance e confiabilidade
- ✅ Transações ACID garantidas

**Desvantagens:**
- ❌ Requer servidor dedicado para o banco
- ❌ Requer modificação do código (`database.py`)
- ❌ Maior complexidade de configuração

---

## ✅ Correção: Erro de Thread no Flask

### Problema Encontrado

Quando executava o `.exe`, aparecia o erro:
```
ValueError: signal only works in main thread of the main interpreter
```

### Causa do Problema

O Flask estava configurado para rodar com `debug=True` em uma **thread separada**. O **reloader do Werkzeug** precisa rodar na **thread principal**, não em uma thread separada.

### Solução Implementada

**Modo Executável:**
- ✅ `debug=False` - Desabilita modo debug
- ✅ `use_reloader=False` - Desabilita reloader automático
- ✅ Pode rodar em thread separada sem problemas
- ✅ Performance melhor (sem overhead do debug)

**Modo Desenvolvimento:**
- ✅ `debug=True` - Mantém modo debug
- ✅ `use_reloader=True` - Mantém reloader automático
- ✅ Roda na thread principal (seguro)
- ✅ Hot-reload funciona (atualiza código automaticamente)

---

## 🛠️ Solução de Problemas

### Problema: Executável não inicia

**Solução:**
1. Verifique o antivírus (pode bloquear executáveis Python)
2. Execute como Administrador
3. Verifique se a porta 5000 está disponível

### Problema: Erro ao abrir o navegador

**Solução:**
- O aplicativo ainda estará rodando
- Abra manualmente: `http://localhost:5000`

### Problema: Banco de dados não encontrado

**Solução:**
- A pasta `data` será criada automaticamente
- Se necessário, crie manualmente: `mkdir data`

### Problema: Antivírus detecta como ameaça

**Solução:**
- Falso positivo comum em executáveis PyInstaller
- Adicione exceção no antivírus
- Ou execute diretamente com Python: `python main.py`

### Problema: Tray icon não aparece

**Linux:**
```bash
# Verificar se pystray está instalado
pip3 show pystray

# Instalar dependências do sistema
sudo apt-get install python3-gi python3-gi-cairo gir1.2-appindicator3-0.1
```

**Windows:**
- Tray icon funciona nativamente
- Certifique-se de que pystray está instalado

### Problema: Porta 5000 já em uso

```bash
# Encontrar processo
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Parar processo
kill <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

---

## 📋 Comandos Essenciais

### 1. Testar Dependências
```batch
python testar_antes_build.py
```

### 2. Criar o Executável
```batch
build_exe.bat
```
**OU**
```batch
pyinstaller gerente_pacientes.spec --clean --noconfirm
```

### 3. Testar o Executável
```batch
testar_exe.bat
```

### 4. Executar em Modo Desenvolvimento
```batch
python main.py
```

### 5. Instalar Dependências
```batch
pip install -r requirements.txt
```

### Limpar builds antigos:
```batch
rmdir /s /q build
rmdir /s /q dist
```

### Atualizar PyInstaller:
```batch
pip install --upgrade pyinstaller
```

---

## 🎨 Personalização Avançada

### Adicionar Ícone ao Executável

1. Coloque um arquivo `.ico` na pasta do projeto
2. Edite `gerente_pacientes.spec`:
   ```python
   icon='meu_icone.ico'
   ```
3. Recrie o executável

### Habilitar Console (para debug)

Edite `gerente_pacientes.spec`:
```python
console=True  # Altere False para True
```

### Adicionar Splash Screen

Instale `pyi-splash`:
```batch
pip install pyi-splash
```

E adicione ao `.spec`:
```python
splash = Splash('splash.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=(10, 50),
                text_size=12,
                text_color='black')
```

---

## 📁 Estrutura de Arquivos

```
Projeto/
│
├── 📄 main.py                    # Código principal
├── 📄 database.py                # Gerenciamento do banco de dados
├── 📄 requirements.txt           # Dependências Python
├── 📄 gerente_pacientes.spec    # Configuração PyInstaller
│
├── 🔧 build_exe.bat             # Script para criar .exe
├── 🔧 testar_antes_build.py    # Testar dependências
├── 🔧 testar_exe.bat           # Testar executável
│
├── 📁 templates/                # Templates HTML
├── 📁 static/                   # CSS, JS, imagens
├── 📁 data/                     # Banco de dados
│
├── 📁 build/                    # Arquivos temporários (pode deletar)
└── 📁 dist/                     # ⭐ EXECUTÁVEL FINAL AQUI
    └── Gerente_de_Pacientes.exe
```

---

## ✨ Funcionalidades Incluídas

- ✅ **Gerenciamento completo de pacientes**
- ✅ **Interface web moderna e responsiva**
- ✅ **Banco de dados SQLite integrado**
- ✅ **Exportação para Excel (.xlsx)**
- ✅ **Exportação para Word (.docx)**
- ✅ **Exportação para texto (.txt)**
- ✅ **Estatísticas e indicadores visuais**
- ✅ **Sistema de backup e restauração**
- ✅ **Tray icon para controle**
- ✅ **Execução silenciosa**

---

## 🎯 Diferenças entre Executável e Versão Python

| Aspecto | Executável | Python |
|---------|-----------|---------|
| Instalação Python | ❌ Não necessário | ✅ Requerido |
| Dependências | ❌ Não necessário | ✅ pip install -r requirements.txt |
| Tamanho | ~30 MB | ~5 MB (+ Python) |
| Velocidade Inicial | Mais lento | Mais rápido |
| Portabilidade | ✅ Alta | ⚠️ Requer ambiente |
| Debugging | ⚠️ Limitado | ✅ Completo |

---

## 📝 Notas Importantes

### Por que não usar debug no executável?

1. **Performance:** Modo debug é mais lento
2. **Segurança:** Não é necessário em produção
3. **Threading:** Reloader não funciona em threads
4. **Estabilidade:** Melhor para usuários finais

### Modo Debug vs Produção

- **Desenvolvimento:** Use `python main.py` (com debug)
- **Distribuição:** Use `.exe` (sem debug, mais rápido)

### Banco de Dados

- O arquivo `data/pacientes.db` **NÃO** será versionado no Git
- Isso é **intencional** - cada ambiente tem seu próprio banco
- O arquivo `.gitkeep` mantém a pasta `data/` no repositório

---

## 🔒 Segurança

- Aplicação roda apenas em `127.0.0.1` (localhost)
- Não expõe portas externamente
- Shutdown limpo libera recursos

---

## 📞 Suporte

Em caso de problemas:
1. Verifique a seção "Solução de Problemas"
2. Execute com console habilitado para ver erros
3. Teste primeiro com `python main.py`

---

## 🎉 Pronto para Usar!

Seu sistema de gerenciamento de pacientes agora é um executável profissional!

**Teste agora:**
```
dist\Gerente_de_Pacientes.exe
```

---

*Desenvolvido com ❤️ usando Python + Flask + PyInstaller*

**Última atualização:** Janeiro 2026
