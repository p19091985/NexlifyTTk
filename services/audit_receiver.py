"""Optional off-host collector. API only permits creation and exact retries.

Run under a different OS account/host. WORM retention belongs to the storage.
No database credentials or application encryption keys belong on this host.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path
import tempfile
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from utils.secure_files import private_directory, restrict_permissions

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def store_event(body, signature, event_id, directory, key):
    if len(key) < 32 or not hmac.compare_digest(hmac.new(key, body, hashlib.sha256).hexdigest(), signature):
        raise PermissionError('Assinatura inválida.')
    if str(uuid.UUID(event_id)) != event_id:
        raise ValueError('Identificador inválido.')
    data = json.loads(body)
    if data.get('event_id') != event_id:
        raise ValueError('Identificador divergente.')
    directory = private_directory(directory)
    destination = directory / (event_id + '.json')
    fd, temporary = tempfile.mkstemp(dir=directory, prefix='.event-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            restrict_permissions(temporary)
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Hard-link publishes a complete file atomically, without replacing.
            os.link(temporary, destination)
        except FileExistsError:
            from utils.secure_files import reject_link_path
            reject_link_path(destination)
            if destination.read_bytes() != body:
                raise ValueError('Evento já existe com outro conteúdo.') from None
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {'event_id': event_id, 'sha256': hashlib.sha256(body).hexdigest()}


@app.post('/events')
async def receive(request: Request):
    if request.url.scheme != 'https':
        return JSONResponse({'detail': 'HTTPS obrigatório.'}, status_code=400)
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 65536:
            return JSONResponse({'detail': 'Evento excede o limite.'}, status_code=413)
    directory = os.environ.get('NEXLIFY_AUDIT_STORAGE')
    if not directory:
        return JSONResponse({'detail': 'Coletor não configurado.'}, status_code=503)
    try:
        return store_event(bytes(body), request.headers.get('X-Nexlify-Signature', ''),
            request.headers.get('Idempotency-Key', ''), directory,
            os.environ.get('NEXLIFY_AUDIT_KEY', '').encode())
    except PermissionError:
        return JSONResponse({'detail': 'Autenticação inválida.'}, status_code=403)
    except (ValueError, TypeError):
        return JSONResponse({'detail': 'Evento inválido ou divergente.'}, status_code=400)
