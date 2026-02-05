# Pacote Flask – Sistema de Gestão de Pacientes

A aplicação Flask foi modularizada neste pacote. Cada funcionalidade fica em um arquivo.

## Estrutura

| Arquivo | Responsabilidade |
|---------|------------------|
| `__init__.py` | Cria o app, registra blueprints, `run_flask`, `cleanup_flask`, exporta `app`, `db`, `get_db`, etc. |
| `constants.py` | `VERSION`, `BUILD_DATE` |
| `db.py` | Proxy do banco, `get_db`, `_get_db_for_port`, estado de discovery (scan), `atualizar_discovery_peers` |
| `paginas.py` | Rotas HTML: `/`, `/novo_paciente`, `/pacientes`, `/exportar`, `/bd`, `/conflitos`, `/agendamentos`, `/aparencia`, `/ajuda` |
| `api_version.py` | `GET /api/version` |
| `discovery.py` | `GET /health`, `POST /register` |
| `pacientes.py` | CRUD de pacientes: salvar, listar, atualizar, deletar |
| `agendamentos.py` | CRUD de agendamentos |
| `sync.py` | `/api/sync/discover`, `/api/sync/data`, `/api/sync/merge`, conflitos, remover pacientes |
| `backup.py` | Backup: criar, download, restaurar, validar, limpar |
| `indicadores.py` | Indicadores, unidades, ranking, campos disponíveis, temporais |
| `tema.py` | API de tema: obter, salvar, padrão, salvar CSS |
| `exportar.py` | Exportação Excel/Word/TXT |
| `exportar_helpers.py` | Colunas, formatadores e filtros da exportação |
| `ajuda.py` | `GET /api/abrir_ajuda` (abre COMO_USAR no Bloco de Notas) |

## Uso

Imports externos permanecem iguais:

```python
from flask_app import app, run_flask, cleanup_flask, get_db, db, atualizar_discovery_peers, VERSION, BUILD_DATE
```
