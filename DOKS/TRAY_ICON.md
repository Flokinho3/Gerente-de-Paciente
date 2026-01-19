# 🖥️ Tray Icon (Ícone na Bandeja do Sistema)

Sistema de ícone na bandeja do sistema com controle completo da aplicação.

## ✨ Funcionalidades

- ✅ **Ícone na Bandeja**: Aparece na área de notificação
- ✅ **Status em Tempo Real**: Mostra se está rodando (🟢) ou parado (🔴)
- ✅ **Porta Visível**: Exibe a porta em uso (padrão: 5000)
- ✅ **Menu de Ações**: Três botões principais

## 🎯 Botões do Menu

### 🌐 Abrir no Navegador
- Abre automaticamente o navegador na URL da aplicação
- URL: `http://localhost:5000`

### 🔄 Reiniciar
- Para o servidor Flask atual
- Libera a porta
- Reinicia o servidor
- Abre o navegador automaticamente

### ❌ Sair
- Encerra completamente a aplicação
- Garante que a porta seja liberada
- Remove o ícone da bandeja

## 📋 Informações Exibidas

O menu mostra:
- **Status**: 🟢 Rodando ou 🔴 Parado
- **Porta**: Número da porta em uso
- **URL**: Link completo para acesso

## 🚀 Como Usar

### Instalação

```bash
# Instalar dependências (inclui pystray e Pillow)
./instalar_dependencias.sh

# Ou manualmente
pip3 install -r requirements.txt
```

### Execução com Tray Icon

```bash
# Modo silencioso com tray icon (recomendado)
./iniciar_silencioso.sh

# Modo totalmente em background com tray icon
./iniciar_background.sh

# Ou diretamente
python3 main.py --tray
```

### Execução Manual

```bash
# Com variável de ambiente
USE_TRAY=1 python3 main.py

# Com argumento
python3 main.py --tray
```

## 🖼️ Ícone

O ícone é gerado automaticamente:
- **Formato**: 64x64 pixels
- **Design**: Círculo azul com cruz branca (símbolo médico)
- **Cor**: Azul (#2196F3) - cor do sistema de saúde

## 🔧 Configuração

### Alterar Porta

```bash
# Via variável de ambiente
PORT=8080 python3 main.py --tray

# Ou edite tray_icon.py e main.py
```

### Desabilitar Tray Icon

```bash
# Modo desenvolvimento (sem tray)
python3 main.py

# Modo silencioso sem tray
python3 main.py --silent
```

## 🐛 Troubleshooting

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

### Problema: "pystray não está instalado"

```bash
pip3 install pystray pillow
```

### Problema: Ícone não atualiza status

- O status é atualizado automaticamente a cada 5 segundos
- Clique com botão direito no ícone para ver menu atualizado

## 📝 Notas Técnicas

- **Threading**: Flask roda em thread separada
- **Atualização**: Status atualizado a cada 5 segundos
- **Porta**: Verificada via socket antes de iniciar
- **Shutdown**: Usa Werkzeug server para shutdown limpo

## 🎨 Personalização

Para personalizar o ícone, edite `tray_icon.py`:

```python
def criar_icone(self):
    # Modifique cores, tamanho, design aqui
    image = Image.new('RGB', (64, 64), color='white')
    # ... seu código personalizado
```

## ✅ Compatibilidade

- ✅ **Linux**: Funciona com AppIndicator (GNOME, KDE, etc.)
- ✅ **Windows**: Funciona nativamente
- ✅ **macOS**: Requer configuração adicional

## 🔒 Segurança

- Aplicação roda apenas em `127.0.0.1` (localhost)
- Não expõe portas externamente
- Shutdown limpo libera recursos
