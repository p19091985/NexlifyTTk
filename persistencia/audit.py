"""Local audit and transactional outbox; no credentials in event payloads."""
from datetime import datetime, timezone
import json
import uuid
from sqlalchemy import insert
from .schema import log_alteracoes, audit_outbox


def record(connection, username, action):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    event_id = str(uuid.uuid4())
    payload = {'event_id': event_id, 'timestamp': now.isoformat() + 'Z', 'actor': username, 'action': action}
    connection.execute(insert(log_alteracoes).values(timestamp=now, login_usuario=username, acao=action))
    connection.execute(insert(audit_outbox).values(event_id=event_id, created_at=now,
                       payload=json.dumps(payload, ensure_ascii=False), attempts=0))
