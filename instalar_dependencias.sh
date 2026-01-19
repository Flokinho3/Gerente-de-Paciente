#!/bin/bash
# Script para instalar dependências do Gerente de Pacientes

echo "=========================================="
echo "  Instalando Dependências"
echo "=========================================="
echo ""

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "Erro: pip3 não encontrado!"
    exit 1
fi

echo "Instalando dependências do requirements.txt..."
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "  Instalação Concluída!"
echo "=========================================="
echo ""
echo "Dependências instaladas:"
echo "  - Flask"
echo "  - openpyxl"
echo "  - python-docx"
echo "  - pyinstaller"
echo "  - pystray (Tray Icon)"
echo "  - Pillow (Imagens)"
echo ""
echo "Agora você pode executar:"
echo "  ./iniciar_silencioso.sh"
echo ""
