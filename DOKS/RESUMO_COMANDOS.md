# 🚀 Resumo Rápido - Comandos Essenciais

## 📋 Comandos Principais

### 1. Testar Dependências
```batch
python testar_antes_build.py
```
Verifica se todas as bibliotecas necessárias estão instaladas.

---

### 2. Criar o Executável
```batch
build_exe.bat
```
**OU**
```batch
pyinstaller gerente_pacientes.spec --clean --noconfirm
```
Cria o arquivo `.exe` na pasta `dist/`.

---

### 3. Testar o Executável
```batch
testar_exe.bat
```
Verifica se o `.exe` foi criado corretamente e permite testá-lo.

---

### 4. Executar em Modo Desenvolvimento
```batch
python main.py
```
Executa o projeto diretamente com Python (sem criar .exe).

---

### 5. Instalar Dependências
```batch
pip install -r requirements.txt
```
Instala todas as bibliotecas necessárias.

---

## 📂 Estrutura de Arquivos Criados

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
├── 📖 COMO_CRIAR_EXE.txt       # Guia simplificado
├── 📖 README_WINDOWS_EXE.md    # Documentação completa
├── 📖 DISTRIBUICAO.md          # Guia de distribuição
├── 📖 RESUMO_COMANDOS.md       # Este arquivo
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

## ⚡ Fluxo de Trabalho Completo

### Primeira Vez:
```batch
1. pip install -r requirements.txt
2. python testar_antes_build.py
3. build_exe.bat
4. testar_exe.bat
```

### Após Modificações no Código:
```batch
1. Teste com: python main.py
2. Se OK: build_exe.bat
3. Teste: testar_exe.bat
```

---

## 🎯 Comandos PyInstaller Úteis

### Criar executável básico:
```batch
pyinstaller main.py
```

### Criar executável em arquivo único:
```batch
pyinstaller --onefile main.py
```

### Sem janela de console:
```batch
pyinstaller --onefile --noconsole main.py
```

### Com ícone personalizado:
```batch
pyinstaller --onefile --icon=icone.ico main.py
```

### Usando arquivo .spec (recomendado):
```batch
pyinstaller gerente_pacientes.spec --clean --noconfirm
```

---

## 🛠️ Comandos de Manutenção

### Limpar builds antigos:
```batch
rmdir /s /q build
rmdir /s /q dist
```

### Atualizar PyInstaller:
```batch
pip install --upgrade pyinstaller
```

### Ver versão do PyInstaller:
```batch
pyinstaller --version
```

### Listar imports do projeto:
```batch
pipreqs . --force
```

---

## 🐛 Comandos de Debug

### Executar com console visível:
Edite `gerente_pacientes.spec`:
```python
console=True
```

### Ver detalhes do build:
```batch
pyinstaller gerente_pacientes.spec --clean --log-level DEBUG
```

### Verificar dependências faltando:
```batch
python testar_antes_build.py
```

---

## 📦 Distribuição

### Compactar para distribuição:
```batch
cd dist
tar -a -c -f Gerente_Pacientes_v1.0.zip Gerente_de_Pacientes.exe data
```

### Calcular hash do arquivo (verificação):
```batch
certutil -hashfile dist\Gerente_de_Pacientes.exe SHA256
```

---

## 🔑 Atalhos de Teclado Úteis

- `Ctrl + C` - Parar o servidor Flask
- `Ctrl + Shift + R` - Recarregar página (ignorar cache)
- `F5` - Recarregar página
- `F12` - Abrir DevTools do navegador

---

## 📞 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| PyInstaller não encontrado | `pip install pyinstaller` |
| Erro ao importar módulo | `pip install -r requirements.txt` |
| Porta 5000 em uso | Fechar outros programas ou mudar porta |
| Antivírus bloqueia .exe | Adicionar exceção |
| .exe não abre | Executar como Administrador |

---

## 🎓 Dicas Profissionais

1. **Sempre teste em máquina limpa** (sem Python instalado)
2. **Use controle de versão** (Git) para o código-fonte
3. **Documente mudanças** em cada versão
4. **Faça backup** do banco de dados antes de updates
5. **Teste todas as funcionalidades** após criar o .exe

---

## 📚 Recursos Adicionais

- [Documentação PyInstaller](https://pyinstaller.org/)
- [Documentação Flask](https://flask.palletsprojects.com/)
- [Python Packaging Guide](https://packaging.python.org/)

---

**Última atualização:** Janeiro 2026
