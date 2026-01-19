# 📋 Informações sobre o .gitignore

## ✅ Arquivo .gitignore criado!

Foi criado um arquivo `.gitignore` completo para o projeto **Gerente de Pacientes**.

---

## 📁 O que está sendo ignorado:

### 🐍 Python
- `__pycache__/` - Cache do Python
- `*.pyc`, `*.pyo` - Bytecode compilado
- `.venv/`, `venv/`, `env/` - Ambientes virtuais

### 🏗️ Build e Distribuição
- `build/` - Arquivos temporários do PyInstaller
- `dist/*.exe` - Executáveis gerados (ignora builds)
- `*.pkg`, `*.toc`, `*.pyz` - Arquivos temporários do build

### 💾 Banco de Dados
- `data/*.db` - Banco de dados SQLite
- `data/*.sqlite3` - Arquivos de banco
- `*.db-journal` - Logs do SQLite

### 🔧 IDEs e Editores
- `.vscode/` - Configurações do VS Code
- `.idea/` - Configurações do PyCharm
- `*.sublime-*` - Configurações do Sublime Text

### 🪟 Sistema Operacional
- `Thumbs.db` - Ícones do Windows
- `.DS_Store` - Metadados do macOS
- `Desktop.ini` - Configurações do Windows

### 📝 Arquivos Temporários
- `*.log` - Arquivos de log
- `*.bak`, `*.backup` - Backups
- `*.tmp` - Arquivos temporários

---

## ✅ O que está sendo versionado:

### 📄 Arquivos importantes:
- ✅ `requirements.txt` - Dependências do projeto
- ✅ `gerente_pacientes.spec` - Configuração do PyInstaller
- ✅ `main.py` - Código principal
- ✅ `database.py` - Código do banco de dados
- ✅ `templates/` - Templates HTML
- ✅ `static/` - CSS, JS e arquivos estáticos
- ✅ `build_exe.bat` - Script de build
- ✅ `testar_antes_build.py` - Script de teste
- ✅ `.gitignore` - Este arquivo de configuração
- ✅ `README.md` e documentação na pasta `DOKS/`

---

## 📂 Estrutura no Git:

```
Gerente-de-Paciente/
├── .gitignore              ✅ Versionado
├── requirements.txt         ✅ Versionado
├── gerente_pacientes.spec  ✅ Versionado
├── main.py                 ✅ Versionado
├── database.py             ✅ Versionado
├── build_exe.bat           ✅ Versionado
├── templates/              ✅ Versionado
├── static/                 ✅ Versionado
├── data/
│   └── .gitkeep            ✅ Versionado (mantém a pasta)
├── build/                  ❌ Ignorado
├── dist/                   ❌ Ignorado
├── __pycache__/            ❌ Ignorado
├── data/*.db               ❌ Ignorado (banco de dados)
└── venv/                   ❌ Ignorado (se existir)
```

---

## 🚀 Como usar:

### 1. **Verificar o que será ignorado:**
```bash
git status
```

### 2. **Adicionar arquivos importantes:**
```bash
git add .gitignore
git add requirements.txt
git add main.py
git add database.py
git add gerente_pacientes.spec
git add templates/
git add static/
# ... etc
```

### 3. **Verificar antes de commitar:**
```bash
git status
```

---

## 📝 Notas importantes:

### ⚠️ Banco de dados:
- O arquivo `data/pacientes.db` **NÃO** será versionado
- Isso é **intencional** - cada ambiente tem seu próprio banco
- O arquivo `.gitkeep` mantém a pasta `data/` no repositório

### ⚠️ Executáveis:
- Os arquivos `dist/*.exe` são ignorados
- Isso evita arquivos grandes no repositório
- Se precisar versionar um release, pode fazer manualmente

### ⚠️ Build:
- Toda a pasta `build/` é ignorada
- Os arquivos são recriados a cada build
- Não é necessário versionar arquivos temporários

---

## 🔧 Personalização:

Se precisar ajustar o `.gitignore`:

1. **Adicionar arquivo específico:**
   ```
   # No .gitignore, adicione:
   !nome_do_arquivo.txt
   ```

2. **Ignorar arquivo adicional:**
   ```
   # No .gitignore, adicione:
   nome_do_arquivo.ext
   ```

3. **Ignorar pasta específica:**
   ```
   # No .gitignore, adicione:
   nome_da_pasta/
   ```

---

## ✅ Checklist:

- [x] `.gitignore` criado
- [x] Arquivos Python ignorados (`__pycache__`, `*.pyc`)
- [x] Ambiente virtual ignorado (`venv/`, `.venv/`)
- [x] Build ignorado (`build/`, `dist/`)
- [x] Banco de dados ignorado (`data/*.db`)
- [x] Arquivos de IDE ignorados (`.vscode/`, `.idea/`)
- [x] Arquivos do sistema ignorados (`Thumbs.db`, `.DS_Store`)
- [x] Arquivos importantes mantidos (`requirements.txt`, `.spec`, etc.)

---

**Pronto!** O projeto está configurado corretamente para o Git! 🎉

---

*Última atualização: Janeiro 2026*
