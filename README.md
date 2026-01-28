# 🏥 Sistema de Gestão de Pacientes

> Sistema web profissional para gerenciamento completo de pacientes, desenvolvido em Python com Flask. Interface moderna e intuitiva para cadastro, acompanhamento, alertas de conflitos e análise visual de indicadores.

[![Versão](https://img.shields.io/badge/Versão-1.0.3-blue.svg)](https://github.com/seu-usuario/gerente-paciente)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://sqlite.org)

## ✨ Funcionalidades

### 👥 Gestão de Pacientes
- Cadastro completo com dados pessoais, gestacionais, sociais e anexos
- Estratificação de risco automática e alertas para pacientes fora do cronograma
- Histórico médico organizado com marcação de conflitos para revisão manual
- Exportação de registros para Excel, Word e TXT

### 📅 Sistema de Agendamentos
- Calendário interativo com tipos de consulta, filtros e busca por paciente
- Alertas automáticos para consultas próximas ou com pendências
- Histórico de agendamentos e log de mudanças com status atualizado
- Integração com rankings e indicadores para monitorar desempenho

### 📊 Painel e Relatórios
- Dashboard responsivo com Chart.js, comparação entre períodos e filtros dinâmicos
- Indicadores por unidade de saúde, ranking geral e filtros temporais
- Exportação de relatórios personalizados e comparação lado a lado de pacientes
- Possibilidade de ajustar temas (cores, fontes e contraste)

### 🔧 Operações Avançadas
- Execução standalone (PyInstaller) com modo silencioso, tray icon e console opcional
- Modo duplo para rodar dois servidores simultâneos e sincronização automática
- Backup automático, download e restauração via APIs
- Descoberta de servidores via Zeroconf ou scan em rede local, com resolução de conflitos
- Monitoramento de health checks e integração com firewall/rede via `inicio/rede`

## 📋 Requisitos do Sistema

### Requisitos mínimos
- **Sistema Operacional**: Windows 10/11, Linux ou macOS
- **Python**: 3.8 ou superior (somente para desenvolvimento)
- **Memória RAM**: 512 MB
- **Espaço em disco**: 50 MB livres
- **Navegador**: Chrome, Firefox ou Edge (qualquer navegador moderno)

### Dependências Python (veja `requirements.txt`)
- `Flask==2.3.3` – framework web
- `waitress==3.0.0` – servidor WSGI usado em produção
- `openpyxl==3.1.2` – exportação Excel
- `python-docx==1.1.0` – exportação Word
- `pyinstaller==6.3.0` – criação do executável
- `pystray==0.19.5` + `Pillow==10.1.0` – ícone na bandeja do sistema
- `python-dotenv==1.0.0` – carregamento de `.env`
- `requests==2.31.0` – chamadas HTTP internas
- `zeroconf>=0.131.0` – descoberta mDNS na LAN

## 🚀 Instalação e Execução

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd gerente-paciente
   ```
2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copie `env.example.txt` para `.env`** e ajuste portas, discovery e log conforme necessário
4. **Execute**
   ```bash
   python main.py
   ```
5. **Abra o navegador**
   ```
   http://localhost:5000
   ```

### 🎯 Modos de inicialização

```bash
# Modo desenvolvimento com reload
python main.py

# Força o tray icon em modo dev
python main.py --tray

# Execução silenciosa (sem interface)
python main.py --silent

# Modo sem tray icon mesmo no exe
python main.py --no-tray

# Modo duplo: duas portas (PORT e PORT2)
python main.py --duplo
```

Os modos também respeitam as variáveis `SILENT_MODE`, `USE_TRAY` e `DUPLO_SERVIDOR`. Use `PORT`/`PORT2` para customizar portas.

## 🌐 Rede, Descoberta e Sincronização

- **DISCOVERY=zeroconf** (padrão): anuncia `_gerentepaciente._http._tcp.local.` e descobre automaticamente peers na LAN.
- **DISCOVERY=scan**: executa varredura /24, `SYNC_TARGETS` ou `SYNC_SCAN_CIDRS` e registra peers no líder via `/register`.
- A API `/api/sync/*` expõe descoberta (`discover`), exportação (`data`), merge (`merge`) e resolução de conflitos (`conflitos`).
- `inicio/rede` gerencia verificação e liberação de portas, zeroconf e sincronização contínua.

## 🏗️ Arquitetura do Projeto

```
gerente-paciente/
├── data/                      # Banco SQLite (pacientes.db e arquivos auxiliares)
├── flask_app/                 # Pacote Flask com blueprints, APIs e helpers
├── inicio/                    # Inicializadores: opções, rede e modos de servidor
│   ├── opcoes/                # Flags, env vars e handlers de sinal
│   ├── rede/                  # Zeroconf, scan, sincronização e portas
│   └── servidores/            # Modos tray, silencioso, duplo e dev
├── static/                    # CSS/JS por módulo (home, agendamentos, exportar etc.)
├── templates/                 # Views HTML (Home, pacientes, agendamentos, ranks etc.)
├── outros/                    # Scripts auxiliares e documentação
├── main.py                    # Orquestrador: validações, modos e tray icon
├── tray_icon.py              # Gerencia o ícone na bandeja com pystray
├── database.py                # Classe Database usada pelo pacote Flask
├── env_loader.py              # Localiza e carrega `.env`
├── config.py                  # Leituras extras (PC_ID, recursos específicos)
├── requirements.txt           # Dependências do projeto
├── build_gerente.py           # Helper Python para PyInstaller
├── build_gerente.bat          # Wrapper Windows para o helper
├── gerente_pacientes.spec     # Configuração do PyInstaller
└── README.md                  # Esta documentação
```

## 📦 Build do Executável

1. Ajuste o `.env` (garanta `FLASK_DEBUG=false` para esconder console no exe)
2. Execute:
   ```bash
   python build_gerente.py
   ```
   ou
   ```bash
   build_gerente.bat
   ```
3. O script limpa `build/`, ajusta `console` no `.spec` e invoca `pyinstaller build_gerente.spec --clean --noconfirm`.

### 📤 Distribuição

```
dist/Gerente.exe          # Executável pronto
dist.zip                 # Opcional: inclui dist/ + data/
```

Adicione também:

```
dist/Launcher.exe        # Launcher que verifica updates e abre o Gerente
```

O `Launcher.exe` deve ser o ponto de entrada do sistema: ele imprime mensagens simples para o usuário, chama `outros/atualizador_github.py` (que baixa o zip mais recente se houver) e, por fim, inicia `Gerente.exe`. Todo detalhe técnico sai só no log (`updates/launcher.log`), nunca na UI principal.

### Launcher: a interface humana

Crie o arquivo `launcher.py` (já presente no projeto) e o compile com PyInstaller para gerar `Launcher.exe`. O fluxo ideal é:

1. `Launcher.exe` mostra mensagens como “Verificando atualizações…” e “Atualização pronta. Reinicie o sistema.”.
2. Ele chama `outros/atualizador_github.py` e redireciona o stdout/stderr para o log `updates/launcher.log`.
3. Se tudo rodar bem, ele inicia `Gerente.exe` (o app principal `main.py`) com os argumentos originais.

Assim você entrega dois artefatos: o Launcher, responsável por atualizações seguras, e o Gerente, que roda a aplicação. Nunca execute o Gerente diretamente no cliente sem passar pelo Launcher.

## 📡 Atualizações via GitHub Releases

Trate o repositório como a fonte oficial das versões e deixe o launcher fazer o download. O próximo script é o cliente recomendado para rodar fora do `.exe`.

### Arquivo `version.json`

- `version` (string): versão oficial exibida na tela de login/README.
- `build_date` (string): data/hora da release, usada para auditoria.
- `asset_template` (string): modelo como `GerenteApp_{version}.zip` para derivar o zip do release.

Atualize este arquivo antes de criar um release; ele é lido tanto pelo backend (`flask_app/constants.py`) quanto pelo launcher (`outros/atualizador_github.py`).

### Script `outros/atualizador_github.py`

Use-o para consultar o último release público, comparar com a versão local e baixar o `.zip` segurando o SHA256:

```bash
python outros/atualizador_github.py --repo SeuUsuario/gerente-paciente
```

Opções úteis:

- `--check-only`: apenas verifica versões.
- `--asset-name`: sobrescreve o nome do zip se o template mudar.
- `--download-dir`: pasta onde o zip será salvo (padrão `updates/`).
- `--token`: GitHub token opcional para evitar limites de API.

O script:

1. Lê a versão atual em `version.json`.
2. Pergunta o release mais recente ao GitHub.
3. Compara semanticamente as versões e só baixa quando `remoto > local` (ou `--force`).
4. Valida o hash SHA256 antes de concluir.

### Fluxo sugerido para publicar uma release

1. Atualize `version.json` com a nova versão e data.
2. Gere o executável e o zip (`dist.zip` ou `GerenteApp_X.Y.Z.zip`) incluindo a pasta `data/`.
3. Crie um arquivo `sha256.txt` com o hash do zip.
4. No GitHub Releases, envie o `.zip`, `version.json` e `sha256.txt`.
5. Deixe o launcher baixar o release e aplicar as instruções de substituição (parar o serviço, extrair em pasta temporária, validar antes de substituir a instalação).

### Uma camada humana

O `atualizador_github.py` é uma peça técnica que fala direto com o launcher/log de manutenção. A interface com o usuário deve ser simples, por exemplo:

```
Verificando atualizações…
Atualização disponível (v1.2.0)
Baixando…
Atualização pronta. Reinicie o sistema.
```

Evite expor termos como SHA256, release ou API para quem só precisa saber que está seguro. O launcher pode traduzir qualquer detalhe técnico em um log interno ou mensagens curtas para administradores.

### 🧪 Testes

```bash
python outros/testar_antes_build.py
```

Para testes adicionais, confira `outros/testar_loading.py`.

## 🔧 Configuração Avançada

### `.env` sugerido

```
PORT=5000
PORT2=5001
FLASK_HOST=0.0.0.0
FLASK_DEBUG=false
WAITRESS_THREADS=8
SILENT_MODE=0
USE_TRAY=1
DUPLO_SERVIDOR=0
DEBUG_LOG_PATH=./Debug/debug.log
DB_PATH=data/pacientes.db
DISCOVERY=zeroconf
ZEROCONF_SERVICE_TYPE=_gerentepaciente._http._tcp.local.
SYNC_TARGETS=
SYNC_SCAN_CIDRS=192.168.1.0/24
SYNC_MAX_TARGETS=1024
LEADER_SCAN_INTERVAL=15
PC_ID=
```

### Personalização

- **Ícone**: acrescente `icone.ico` na raiz e defina `icon='icone.ico'` em `gerente_pacientes.spec`.
- **Tema**: edite `static/css/variables.css` ou consulte `outros/DOKS/PALETA_CORES.md`.

## 📖 Documentação Complementar

| Documento | Descrição |
|-----------|-----------|
| `outros/README.md` | Visão geral dos scripts auxiliares |
| `outros/DOKS/README.md` | Documentação completa e mapas mentais |
| `flask_app/README.md` | Responsabilidades dos blueprints e APIs |
| `env.example.txt` | Modelo comentado do `.env` |
| `outros/MAPA_MENTAL_VISUAL.md` | Fluxo visual das funcionalidades |
| `outros/COMO_USAR.txt` | Manual rápido em texto |

## 📊 API e rotas principais

### Rotas HTML

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Dashboard principal |
| `GET` | `/pacientes` | Lista e detalhes de pacientes |
| `GET` | `/novo_paciente` | Formulário guiado passo a passo |
| `GET` | `/agendamentos` | Agenda, alertas e histórico |
| `GET` | `/exportar` | Exportação Excel/Word/TXT |
| `GET` | `/bd` | Controle e limpeza do banco |
| `GET` | `/conflitos` | Tela para resolver conflitos |
| `GET` | `/aparencia` | Preferências visuais |
| `GET` | `/ajuda` | Central de ajuda e atalhos |
| `GET` | `/ranks` | Rankings e métricas por unidade |

### APIs REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/version` | Versão e build |
| `GET` | `/api/health` | Health check (DISCOVERY=scan) |
| `POST` | `/register` | Registro de peers (DISCOVERY=scan) |
| `GET` | `/api/sync/discover` | Descoberta de servidores na rede |
| `GET` | `/api/sync/data` | Exporta pacientes e agendamentos |
| `POST` | `/api/sync/merge` | Merge automático de dados remotos |
| `GET` | `/api/sync/conflitos` | Conflitos detectados |
| `POST` | `/api/sync/conflitos/resolver` | Resolve conflito manualmente |
| `POST` | `/api/sync/remover_pacientes` | Remove pacientes confirmados |
| `GET` | `/api/backup/criar` | Gera backup JSON |
| `GET` | `/api/backup/download` | Baixa backup |
| `POST` | `/api/backup/restaurar` | Restaura backup enviado |
| `DELETE` | `/api/backup/limpar` | Limpa o banco de dados |
| `GET` | `/api/abrir_ajuda` | Abre `COMO_USAR.txt` no Notepad |

Consulte `flask_app/README.md` para o catálogo completo de endpoints (indicadores, exportação, tema e alertas).

## 🤝 Contribuição

### Como contribuir

1. **Fork** o repositório
2. **Crie** uma branch (`git checkout -b feature/qualquer-coisa`)
3. **Commit** com mensagem explicativa (`git commit -m "feat: ..."`)
4. **Push** para o repositório remoto
5. **Abra** um Pull Request e descreva os testes realizados

### Padrões de código

- **PEP 8** – Formatação Python
- **Docstrings em português**
- **Type hints** quando necessário
- **Testes e scripts auxiliares** em `outros/`

---

## 📞 Suporte

1. 📖 Leia `outros/DOKS/README.md`
2. 🐛 Confira `Debug/debug.log`
3. 🧪 Execute `python main.py` em modo desenvolvimento

**Contato:** Consulte o responsável técnico.

---

**🏥 Sistema de Gestão de Pacientes v1.0.3**  
*Desenvolvido com ❤️ usando Python + Flask + SQLite*

**Última atualização:** Janeiro 2026
# 🏥 Sistema de Gestão de Pacientes

> Sistema web profissional para gerenciamento completo de pacientes, desenvolvido em Python com Flask. Interface moderna e intuitiva para cadastro, acompanhamento e análise de dados de pacientes.

[![Versão](https://img.shields.io/badge/Versão-1.0.3-blue.svg)](https://github.com/seu-usuario/gerente-paciente)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue.svg)](https://sqlite.org)

## ✨ Funcionalidades

### 👥 Gestão de Pacientes
- **Cadastro completo** de pacientes com dados detalhados
- **Acompanhamento pré-natal** com indicadores específicos
- **Estratificação de risco** automática
- **Histórico médico** organizado

### 📅 Sistema de Agendamentos
- **Calendário interativo** para agendamentos
- **Alertas e notificações** automáticas
- **Controle de consultas** e acompanhamentos
- **Histórico de agendamentos**

### 📊 Dashboard e Relatórios
- **Indicadores visuais** em tempo real
- **Gráficos e estatísticas** detalhadas
- **Comparativos** entre períodos
- **Exportação de dados** (Excel, Word)

### 🔧 Recursos Avançados
- **Interface responsiva** para desktop e mobile
- **Modo executável** standalone (sem instalar Python)
- **Ícone na bandeja** do sistema
- **Execução silenciosa** em background
- **Backup automático** do banco de dados

## 📋 Requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional**: Windows 10/11, Linux
- **Python**: 3.8 ou superior (apenas para desenvolvimento)
- **Memória RAM**: 512 MB
- **Espaço em Disco**: 50 MB
- **Navegador**: Chrome, Firefox, Edge (qualquer navegador moderno)

### Dependências Python
```
Flask==2.3.3          # Framework web
openpyxl==3.1.2       # Exportação Excel
python-docx==1.1.0    # Exportação Word
pyinstaller==6.3.0    # Criar executáveis
pystray==0.19.5       # Ícone na bandeja
Pillow==10.1.0        # Manipulação de imagens
python-dotenv==1.0.0  # Variáveis de ambiente
```

## 🚀 Instalação e Execução

### 📥 Instalação Rápida

1. **Clone o repositório**
   ```bash
   git clone <url-do-repositorio>
   cd gerente-paciente
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute o sistema**
   ```bash
   python main.py
   ```

### 🎯 Modos de Execução

#### Modo Desenvolvimento
```bash
# Modo normal com recarregamento automático
python main.py

# Com tray icon
python main.py --tray

# Modo silencioso (background)
python main.py --silent

# Sem tray icon
python main.py --no-tray
```

#### Modo Executável (Standalone)
```bash
# Usar o executável pronto (Windows)
./dist/Gerente_de_Pacientes.exe

# Ou criar seu próprio executável
./outros/build_exe.bat
```

### 🌐 Acesso ao Sistema

Após iniciar, abra no navegador:
```
http://localhost:5000
```

## 🏗️ Arquitetura do Projeto

```
gerente-paciente/
│
├── 📁 data/                    # Banco de dados SQLite
│   └── pacientes.db
│
├── 📁 static/                  # Recursos estáticos
│   ├── 📁 agendamentos/        # CSS/JS para agendamentos
│   ├── 📁 home/               # CSS/JS para dashboard
│   ├── 📁 pacientes/          # CSS/JS para pacientes
│   ├── 📁 novo_paciente/      # CSS/JS para formulários
│   └── 📁 img/                # Imagens e ícones
│
├── 📁 templates/               # Templates HTML
│   ├── Home.html              # Dashboard principal
│   ├── pacientes.html         # Lista de pacientes
│   ├── novo_paciente.html     # Formulário de cadastro
│   ├── agendamentos.html      # Sistema de agendamentos
│   ├── exportar.html          # Exportação de dados
│   └── bd.html                # Gerenciamento do BD
│
├── 📁 outros/                  # Scripts e documentação
│   ├── 📁 build/              # Arquivos temporários PyInstaller
│   ├── 📁 dist/               # Executável final
│   ├── 📁 DOKS/               # Documentação completa
│   ├── build_exe.bat          # Script de build
│   └── README.md              # Documentação adicional
│
├── 🐍 main.py                  # Ponto de entrada principal
├── 🐍 flask_app.py            # Aplicação Flask (v1.0.3)
├── 🐍 database.py             # Camada de banco de dados
├── 🐍 tray_icon.py            # Gerenciador do tray icon
├── 📋 requirements.txt        # Dependências Python
├── ⚙️ gerente_pacientes.spec   # Configuração PyInstaller
├── 🔒 env.example.txt         # Exemplo de configuração
└── 📖 README.md               # Esta documentação
```

## 📦 Build do Executável

### 🛠️ Criar Executável Windows

```bash
# Método 1: Usar script pronto
./outros/build_exe.bat

# Método 2: Comando manual
pyinstaller gerente_pacientes.spec --clean --noconfirm

# Método 3: Build básico
pyinstaller --onefile --windowed main.py
```

### 📤 Distribuição

**Arquivo único (recomendado):**
```
dist/Gerente_de_Pacientes.exe (≈16 MB)
```

**Pacote completo:**
```
dist.zip (contém .exe + pasta data/)
```

### 🧪 Testes

```bash
# Testar dependências antes do build
python outros/testar_antes_build.py

# Testar executável criado
./outros/testar_exe.bat
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente (.env)

```bash
# Porta do servidor (padrão: 5000)
PORT=5000

# Host do Flask (padrão: 127.0.0.1)
# Use 0.0.0.0 para aceitar conexões de outros PCs (Descobrir Servidores na rede)
FLASK_HOST=127.0.0.1

# Modo silencioso (0/1)
SILENT_MODE=0

# Usar tray icon (0/1)
USE_TRAY=1

# Caminho do log de debug
DEBUG_LOG_PATH=./Debug/debug.log
```

### Personalização

**Ícone personalizado:**
1. Adicione `icone.ico` na raiz do projeto
2. Edite `gerente_pacientes.spec`:
   ```python
   exe = EXE(
       # ... outros parâmetros
       icon='icone.ico'
   )
   ```

**Tema e cores:**
- Edite `static/css/variables.css`
- Consulte `outros/DOKS/PALETA_CORES.md`

## 📖 Documentação Completa

### 📚 Guias Disponíveis

| Documento | Descrição |
|-----------|-----------|
| `INICIO_RAPIDO.md` | Guia rápido para começar |
| `README_WINDOWS_EXE.md` | Executável Windows detalhado |
| `DISTRIBUICAO.md` | Como distribuir o sistema |
| `RESUMO_COMANDOS.md` | Comandos essenciais |
| `TRAY_ICON.md` | Configuração do tray icon |
| `PALETA_CORES.md` | Personalização visual |

### 🆘 Solução de Problemas

**Problemas comuns:**
- **Porta 5000 ocupada**: Sistema mata processos antigos automaticamente
- **Antivírus bloqueia**: Adicione exceção para o executável
- **PyInstaller falha**: Execute `pip install --upgrade pyinstaller`
- **Tray icon não funciona**: Instale `pip install pystray pillow`
- **Não encontra outros servidores na rede**: Em cada PC, defina `FLASK_HOST=0.0.0.0` no `.env` e reinicie. Permita o Gerente no Firewall do Windows (redes privadas).

## 🔧 Tecnologias Utilizadas

### Backend
- **Python 3.8+**: Linguagem principal
- **Flask 2.3.3**: Framework web
- **SQLite**: Banco de dados local
- **SQLAlchemy**: ORM para banco de dados

### Frontend
- **HTML5**: Estrutura das páginas
- **CSS3**: Estilização responsiva
- **JavaScript (Vanilla)**: Interatividade
- **Chart.js**: Gráficos e indicadores

### Build & Deploy
- **PyInstaller**: Criar executáveis
- **Tkinter**: Interface nativa (diálogos)
- **Pystray**: Ícone na bandeja do sistema

### Desenvolvimento
- **python-dotenv**: Variáveis de ambiente
- **openpyxl**: Exportação Excel
- **python-docx**: Exportação Word

## 📊 API Endpoints

### Principais Rotas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/` | Dashboard principal |
| `GET` | `/pacientes` | Lista de pacientes |
| `GET` | `/novo_paciente` | Formulário de cadastro |
| `GET` | `/agendamentos` | Sistema de agendamentos |
| `GET` | `/exportar` | Exportação de dados |
| `POST` | `/api/salvar_paciente` | Salvar paciente |
| `GET` | `/api/pacientes` | Buscar pacientes |
| `POST` | `/api/agendamento` | Criar agendamento |

### Informações do Sistema

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/version` | Versão e data do build |
| `GET /api/health` | Status do sistema |

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o projeto
2. **Crie** uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. **Abra** um Pull Request

### Padrões de Código

- **PEP 8**: Padrão Python para formatação
- **Docstrings**: Documentação em português
- **Type Hints**: Indicação de tipos
- **Testes**: Validar funcionalidades

## 📝 Licença

Este projeto é de **uso privado**. Todos os direitos reservados.

---

## 📞 Suporte

**Para suporte técnico:**

1. 📖 Consulte a documentação em `outros/DOKS/`
2. 🐛 Verifique `Debug/debug.log` para erros
3. 🧪 Teste em modo desenvolvimento: `python main.py`

**Contato:** Para questões específicas, consulte o desenvolvedor responsável.

---

**🏥 Sistema de Gestão de Pacientes v1.0.3**
*Desenvolvido com ❤️ usando Python + Flask + SQLite*

**Última atualização:** Janeiro 2026
