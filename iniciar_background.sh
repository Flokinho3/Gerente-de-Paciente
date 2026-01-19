#!/bin/bash
# Script para iniciar o Gerente de Pacientes completamente em background
# Sem terminal visível - ideal para iniciar automaticamente

# Obter diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Criar diretório de logs
mkdir -p "$SCRIPT_DIR/logs"

# Arquivo PID para controle
PID_FILE="$SCRIPT_DIR/logs/app.pid"
LOG_FILE="$SCRIPT_DIR/logs/app.log"
ERROR_LOG="$SCRIPT_DIR/logs/error.log"

# Verificar se já está rodando
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Aplicação já está rodando (PID: $OLD_PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Iniciar em background completamente silencioso com tray icon
USE_TRAY=1 nohup python3 main.py --tray > "$LOG_FILE" 2> "$ERROR_LOG" &
NEW_PID=$!

# Salvar PID
echo $NEW_PID > "$PID_FILE"

# Aguardar um pouco para verificar se iniciou corretamente
sleep 3

if ps -p $NEW_PID > /dev/null 2>&1; then
    echo "Aplicação iniciada em background (PID: $NEW_PID)"
    echo "Acesse: http://localhost:5000"
    echo "Logs em: $LOG_FILE"
    echo "Para parar: kill $NEW_PID ou execute: ./parar.sh"
else
    echo "Erro ao iniciar aplicação!"
    echo "Verifique os logs: $ERROR_LOG"
    rm -f "$PID_FILE"
    exit 1
fi
