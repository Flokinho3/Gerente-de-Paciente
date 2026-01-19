# 🏥 Gerente de Pacientes - Versão Executável para Windows

## 📦 Como Criar o Executável (.exe)

### Método 1: Script Automático (Recomendado)

1. **Execute o script de build:**
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

1. **Instalar PyInstaller (se ainda não estiver instalado):**
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

4. **Copiar banco de dados (opcional):**
   ```batch
   xcopy /E /I data dist\data
   ```

## 🚀 Como Usar o Executável

### Localização:
```
dist\Gerente_de_Pacientes.exe
```

### Execução:
1. Vá até a pasta `dist`
2. Execute o arquivo `Gerente_de_Pacientes.exe`
3. Uma janela informativa aparecerá
4. O navegador abrirá automaticamente em `http://localhost:5000`

### Distribuição:
Para distribuir o aplicativo, copie toda a pasta `dist` ou apenas o arquivo `.exe` (ele é autocontido).

## ✨ Funcionalidades Incluídas

- ✅ **Gerenciamento completo de pacientes**
- ✅ **Interface web moderna e responsiva**
- ✅ **Banco de dados SQLite integrado**
- ✅ **Exportação para Excel (.xlsx)**
- ✅ **Exportação para Word (.docx)**
- ✅ **Exportação para texto (.txt)**
- ✅ **Estatísticas e indicadores visuais**
- ✅ **Sistema de backup e restauração**

## 💻 Requisitos do Sistema

- **Sistema Operacional:** Windows 10/11 (64-bit)
- **Memória RAM:** Mínimo 2GB
- **Espaço em Disco:** ~50MB
- **Navegador:** Chrome, Firefox, Edge ou similar

**Importante:** O executável NÃO requer instalação de Python ou outras dependências!

## 📁 Estrutura de Arquivos

```
dist/
├── Gerente_de_Pacientes.exe  (executável principal - ~25-30MB)
└── data/                       (pasta do banco de dados - criada automaticamente)
    └── pacientes.db
```

## 🔧 Configurações do Build

O arquivo `gerente_pacientes.spec` contém todas as configurações:

- **Modo Console:** Desabilitado (interface sem janela de comando)
- **Arquivos Incluídos:** Templates, static, data
- **Bibliotecas:** Flask, OpenPyXL, python-docx, tkinter
- **Compressão:** UPX habilitado
- **Tipo:** Executável único (--onefile)

## ⚠️ Solução de Problemas

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

## 🎯 Diferenças entre Executável e Versão Python

| Aspecto | Executável | Python |
|---------|-----------|---------|
| Instalação Python | ❌ Não necessário | ✅ Requerido |
| Dependências | ❌ Não necessário | ✅ pip install -r requirements.txt |
| Tamanho | ~30 MB | ~5 MB (+ Python) |
| Velocidade Inicial | Mais lento | Mais rápido |
| Portabilidade | ✅ Alta | ⚠️ Requer ambiente |
| Debugging | ⚠️ Limitado | ✅ Completo |

## 🛠️ Personalização Avançada

### Adicionar Ícone ao Executável:

1. Coloque um arquivo `.ico` na pasta do projeto
2. Edite `gerente_pacientes.spec`:
   ```python
   icon='meu_icone.ico'
   ```
3. Recrie o executável

### Habilitar Console (para debug):

Edite `gerente_pacientes.spec`:
```python
console=True  # Altere False para True
```

### Adicionar Splash Screen:

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

## 📞 Suporte

Em caso de problemas:
1. Verifique a seção "Solução de Problemas"
2. Execute com console habilitado para ver erros
3. Teste primeiro com `python main.py`

## 🎉 Pronto para Distribuir!

Após criar o executável:
1. Teste em outra máquina Windows
2. Crie um instalador (NSIS, Inno Setup) se desejar
3. Distribua a pasta `dist` ou apenas o `.exe`

---

**Desenvolvido com ❤️ usando Python + Flask + PyInstaller**
