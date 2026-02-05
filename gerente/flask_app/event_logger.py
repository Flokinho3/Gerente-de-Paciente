from datetime import datetime
from flask import Blueprint, jsonify, request
import threading

# Blueprint para API
bp = Blueprint('event_logger', __name__, url_prefix='/api/events')

class EventLogger:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventLogger, cls).__new__(cls)
                cls._instance.events = []
                cls._instance.max_events = 50
        return cls._instance
    
    def add_event(self, message: str, type: str = 'info'):
        """
        Adiciona um evento ao log.
        Types: 'info', 'success', 'warning', 'error', 'working'
        """
        event = {
            'id': int(datetime.now().timestamp() * 1000),
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'type': type
        }
        
        with self._lock:
            self.events.append(event)
            # Manter apenas os últimos N eventos
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
        
        return event

    def get_events(self, since_id: int = 0):
        """Retorna eventos após um determinado ID"""
        with self._lock:
            if since_id == 0:
                # Se 0, retorna os últimos 5
                return self.events[-5:]
            
            return [e for e in self.events if e['id'] > since_id]

# Instância Global
logger = EventLogger()

@bp.route('/poll', methods=['GET'])
def poll_events():
    try:
        since_id = int(request.args.get('since', 0))
        events = logger.get_events(since_id)
        return jsonify({
            'success': True,
            'events': events
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Helper function para usar em outros módulos
def log_event(message, type='info'):
    logger.add_event(message, type)
