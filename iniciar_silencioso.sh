#!/bin/bash
# Script para iniciar o Gerente de Pacientes sem terminal visível
# Executa em background e abre o navegador automaticamente

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Gerente de Pacientes${NC}"
echo -e "${BLUE}  Iniciando em modo silencioso...${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Obter diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python3 não encontrado!"
    exit 1
fi

# Verificar se as dependências estão instaladas
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Instalando dependências..."
    pip3 install -r requirements.txt
fi

# Criar arquivo de log se não existir
LOG_FILE="$SCRIPT_DIR/logs/app.log"
mkdir -p "$SCRIPT_DIR/logs"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "Encerrando servidor..."
    kill $PID 2>/dev/null
    wait $PID 2>/dev/null
    echo "Servidor encerrado."
    exit 0
}

# Capturar sinais de interrupção
trap cleanup SIGINT SIGTERM

# Iniciar servidor Flask em background sem output visível com tray icon
echo -e "${GREEN}✓${NC} Iniciando servidor Flask com tray icon..."
USE_TRAY=1 python3 main.py --tray > "$LOG_FILE" 2>&1 &
PID=$!

# Aguardar servidor iniciar
sleep 3

# Verificar se o servidor está rodando
if ps -p $PID > /dev/null; then
    echo -e "${GREEN}✓${NC} Servidor iniciado com sucesso! (PID: $PID)"
    echo -e "${GREEN}✓${NC} Abrindo navegador..."
    
    # Aguardar mais um pouco para garantir que o servidor está pronto
    sleep 2
    
    # Abrir navegador
    if command -v xdg-open &> /dev/null; then
        xdg-open 'http://localhost:5000' > /dev/null 2>&1 &
    elif command -v gnome-open &> /dev/null; then
        gnome-open 'http://localhost:5000' > /dev/null 2>&1 &
    elif command -v firefox &> /dev/null; then
        firefox 'http://localhost:5000' > /dev/null 2>&1 &
    else
        echo "Navegador não encontrado. Acesse manualmente: http://localhost:5000"
    fi
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Sistema rodando em: http://localhost:5000${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Pressione Ctrl+C para encerrar o servidor."
    echo ""
    
    # Manter script rodando
    wait $PID
else
    echo "Erro: Falha ao iniciar o servidor!"
    echo "Verifique o log em: $LOG_FILE"
    exit 1
fi
