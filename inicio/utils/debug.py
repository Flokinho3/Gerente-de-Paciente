"""
Log de debug para análise do sistema de inicialização.
"""
import os
from datetime import datetime


def _raiz_projeto():
    """Retorna o diretório raiz do projeto (pasta onde está main.py)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def _log_debug(location, message, data=None, hypothesis_id=None):
    """Log de debug para análise"""
    try:
        import json
        raiz = _raiz_projeto()
        log_path = os.getenv('DEBUG_LOG_PATH', os.path.join(raiz, '.cursor', 'debug.log'))
        log_entry = {
            "sessionId": "debug-session",
            "runId": "run1",
            "hypothesisId": hypothesis_id or "A",
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception:
        pass
