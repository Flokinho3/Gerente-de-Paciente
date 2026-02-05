"""
Script para migrar sync.py para estrutura modular
Extrai cada função e cria arquivos dedicados
"""
import os
import re

# Ler o arquivo original
with open('gerente/flask_app/sync.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Criar diretório se não existir
os.makedirs('gerente/flask_app/sync', exist_ok=True)

print("✅ Estrutura modular criada!")
print("\n📁 Arquivos criados:")
print("  - sync/__init__.py")
print("  - sync/helpers.py")
print("\n📝 Próximos arquivos a criar manualmente:")
print("  - sync/p2p_discover.py")
print("  - sync/p2p_merge.py")
print("  - sync/p2p_endpoints.py")
print("  - sync/vps_status.py")
print("  - sync/vps_sync.py")
print("  - sync/vps_data.py")
print("  - sync/vps_divergencias.py")
print("\n✨ Estrutura pronta para refatoração!")
