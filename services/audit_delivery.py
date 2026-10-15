"""Transactional outbox delivery; retries never roll back business transactions."""
import hashlib
import hmac
import os
from datetime import timedelta
import httpx
from sqlalchemy import select, update, or_, func
from persistencia.database import DatabaseManager
from persistencia.schema import audit_outbox
from persistencia.auth import utcnow
from .transport import validate_service_url, tls_context


def delivery_settings():
    url = validate_service_url(os.environ.get('NEXLIFY_AUDIT_URL', ''))
    key = os.environ.get('NEXLIFY_AUDIT_KEY', '').encode()
    if len(key) < 32:
        raise ValueError('Defina NEXLIFY_AUDIT_KEY com pelo menos 32 bytes aleatórios.')
    return url, key


def pending_count():
    with DatabaseManager.get_engine().connect() as connection:
        return connection.execute(select(func.count()).select_from(audit_outbox).where(audit_outbox.c.delivered_at.is_(None))).scalar_one()


def deliver_once(limit=100):
    url, key = delivery_settings()
    now = utcnow()
    engine = DatabaseManager.get_engine()
    with engine.connect() as connection:
        events = connection.execute(select(audit_outbox).where(audit_outbox.c.delivered_at.is_(None),
            or_(audit_outbox.c.next_attempt.is_(None), audit_outbox.c.next_attempt <= now))
            .order_by(audit_outbox.c.created_at).limit(limit)).mappings().all()
    delivered = 0
    with httpx.Client(verify=tls_context(os.environ.get('NEXLIFY_AUDIT_CA', '')), timeout=10,
                      follow_redirects=False, trust_env=False) as client:
        for event in events:
            body = event['payload'].encode('utf-8')
            signature = hmac.new(key, body, hashlib.sha256).hexdigest()
            try:
                response = client.post(url, content=body, headers={'Content-Type': 'application/json',
                    'X-Nexlify-Signature': signature, 'Idempotency-Key': event['event_id']})
                response.raise_for_status()
                receipt = response.json()
                if receipt.get('event_id') != event['event_id'] or receipt.get('sha256') != hashlib.sha256(body).hexdigest():
                    raise ValueError('Recibo de auditoria inválido.')
            except (httpx.HTTPError, ValueError, TypeError):
                values = {'attempts': event['attempts'] + 1,
                          'next_attempt': now + timedelta(seconds=min(3600, 5 * 2 ** min(event['attempts'], 10)))}
            else:
                delivered += 1
                values = {'delivered_at': utcnow(), 'attempts': event['attempts'] + 1, 'next_attempt': None}
            with engine.begin() as connection:
                connection.execute(update(audit_outbox).where(audit_outbox.c.event_id == event['event_id'],
                    audit_outbox.c.delivered_at.is_(None)).values(**values))
    return {'delivered': delivered, 'pending': pending_count()}


def main():
    import argparse
    import json
    import threading
    parser = argparse.ArgumentParser(description='Entrega auditoria para um coletor externo protegido.')
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    delivery_settings()
    while True:
        print(json.dumps(deliver_once()), flush=True)
        if not args.watch:
            break
        threading.Event().wait(30)


if __name__ == '__main__':
    main()
