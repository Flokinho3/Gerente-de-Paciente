from .base import DatabaseBase
from .schema import SchemaMixin
from .models import ModelsMixin
from .pacientes import PacienteMixin
from .agendamentos import AgendamentoMixin
from .stats import StatsMixin
from .sync import SyncMixin
from .backup import BackupMixin

class Database(
    DatabaseBase,
    SchemaMixin,
    ModelsMixin,
    PacienteMixin,
    AgendamentoMixin,
    StatsMixin,
    SyncMixin,
    BackupMixin
):
    """
    Modular Database class combining all mixins.
    """
    pass

# Global instance for backward compatibility
db = Database()
