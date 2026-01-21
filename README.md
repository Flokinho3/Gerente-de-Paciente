# 🏥 Sistema de Gestão de Pacientes

> Sistema web profissional para gerenciamento completo de pacientes, desenvolvido em Python com Flask. Interface moderna e intuitiva para cadastro, acompanhamento e análise de dados de pacientes.

[![Versão](https://img.shields.io/badge/Versão-1.0.2-blue.svg)](https://github.com/seu-usuario/gerente-paciente)
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
- **Sistema Operacional**: Windows 10/11, Linux, macOS
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
├── 🐍 flask_app.py            # Aplicação Flask (v1.0.2)
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

**🏥 Sistema de Gestão de Pacientes v1.0.2**
*Desenvolvido com ❤️ usando Python + Flask + SQLite*

**Última atualização:** Janeiro 2026
