#!/bin/bash
# Script para parar o Gerente de Pacientes

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/logs/app.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Aplicação não está rodando (arquivo PID não encontrado)."
    exit 1
fi

PID=$(cat "$PID_FILE")

if ps -p $PID > /dev/null 2>&1; then
    echo "Parando aplicação (PID: $PID)..."
    kill $PID
    
    # Aguardar encerramento
    sleep 2
    
    # Se ainda estiver rodando, forçar
    if ps -p $PID > /dev/null 2>&1; then
        echo "Forçando encerramento..."
        kill -9 $PID
    fi
    
    rm -f "$PID_FILE"
    echo "Aplicação encerrada."
else
    echo "Processo não encontrado. Limpando arquivo PID."
    rm -f "$PID_FILE"
fi
