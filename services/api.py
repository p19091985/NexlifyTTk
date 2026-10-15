"""Central authorization boundary. Never accepts SQL or client-provided hashes."""
from collections import defaultdict, deque
from contextlib import asynccontextmanager
import threading
import time
import json
import logging
import os

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
import config
from persistencia import auth, mfa
from persistencia.database import DatabaseManager
from persistencia.repository import GenericRepository as Repository
from persistencia.data_service import DataService
from . import sessions


class Rpc(BaseModel):
    model_config = ConfigDict(extra='forbid')
    method: str = Field(max_length=60)
    params: dict = Field(default_factory=dict)


@asynccontextmanager
async def lifespan(app):
    if config.API_MODE != 'server' or not config.USE_LOGIN:
        raise RuntimeError('API exige api_mode=server e login habilitado.')
    config.validate()
    if config.ENVIRONMENT == 'production':
        from persistencia.logger import setup_loggers
        setup_loggers()
        # OAuth callback URLs contain one-use codes; access logs must not record them.
        logging.getLogger('uvicorn.access').disabled = True
    if config.INITIALIZE_DATABASE_ON_STARTUP:
        DatabaseManager.initialize_database()
    stop = threading.Event()
    worker = None
    if os.environ.get('NEXLIFY_AUDIT_URL'):
        from .audit_delivery import delivery_settings, deliver_once
        delivery_settings()
        def deliver():
            while not stop.is_set():
                try:
                    deliver_once(limit=20)
                except (ValueError, OSError, SQLAlchemyError):
                    logging.getLogger('audit').error('Entrega externa pendente; eventos permanecem na fila.')
                stop.wait(30)
        worker = threading.Thread(target=deliver, name='audit-delivery', daemon=True)
        worker.start()
    elif config.ENVIRONMENT == 'production':
        raise RuntimeError('Servidor em produção exige NEXLIFY_AUDIT_URL e NEXLIFY_AUDIT_KEY.')
    try:
        yield
    finally:
        stop.set()
        if worker:
            worker.join(timeout=15)
        DatabaseManager.dispose()


app = FastAPI(title='NexlifyTTk API', docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
_limits = defaultdict(deque)
_limit_lock = threading.Lock()
_hash_slots = threading.BoundedSemaphore(4)


def throttle(client, authentication=False):
    now = time.monotonic()
    key = (client, authentication)
    with _limit_lock:
        for stale in list(_limits):
            if not _limits[stale] or _limits[stale][-1] < now - 60:
                del _limits[stale]
        if key not in _limits and len(_limits) >= 4096:
            raise PermissionError('Limite de requisições atingido.')
        queue = _limits[key]
        while queue and queue[0] < now - 60:
            queue.popleft()
        if len(queue) >= (10 if authentication else 120):
            raise PermissionError('Limite de requisições atingido. Aguarde.')
        queue.append(now)


@app.middleware('http')
async def request_limits(request, call_next):
    # Count actual bytes, including chunked requests; never log a request body.
    if config.ENVIRONMENT == 'production' and request.url.scheme != 'https':
        return JSONResponse({'detail': 'HTTPS obrigatório.'}, status_code=400)
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 65536:
            return JSONResponse({'detail': 'Requisição excede o limite.'}, status_code=413)
    request._body = bytes(body)
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, error):
    return JSONResponse({'detail': 'Requisição inválida.'}, status_code=400)


@app.get('/health')
def health():
    return {'status': 'ok'}


def public_session():
    session = auth.current_session(require_password_change=True, allow_mfa_setup=True)
    return {key: value for key, value in session.items() if not key.startswith('_')}


def user_values(values):
    if not isinstance(values, dict) or any(not isinstance(key, str) for key in values):
        raise ValueError('Campos inválidos.')
    values = {key.lower(): value for key, value in values.items()}
    if 'senha_criptografada' in values:
        raise ValueError('Hashes enviados por clientes não são aceitos.')
    if 'password' in values:
        values['senha_criptografada'] = auth.hash_password(values.pop('password'))
    return values


def records(frame):
    return json.loads(frame.to_json(orient='table', index=False, date_format='iso'))


def dispatch(method, params):
    if method == 'pages/authorize':
        if set(params) != {'page'}:
            raise ValueError('Informe somente a página.')
        return auth.authorize_page(params['page'])
    if method == 'session':
        return public_session()
    if method == 'activity':
        auth.touch_session_activity()
        return {'ok': True}
    if method == 'reauth/status':
        auth.require_recent_auth()
    elif method == 'reauth':
        return auth.reauthenticate(params['password'], params.get('otp', '')) or {'ok': True}
    elif method == 'password':
        auth.change_own_password(params['old_password'], params['new_password'])
    elif method == 'mfa/enroll':
        return mfa.begin_enrollment(params['email'])
    elif method == 'mfa/confirm':
        return {'recovery_codes': mfa.confirm_enrollment(params['code'])}
    elif method == 'mfa/disable':
        mfa.disable()
    elif method == 'read':
        return records(Repository.read_table_to_dataframe(params['table'], params.get('columns'), params.get('where')))
    elif method == 'read_vegetais':
        return records(Repository.read_vegetais_com_tipo())
    elif method == 'insert':
        rows = params['rows']
        if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
            raise ValueError('Envie entre 1 e 100 registros.')
        if params['table'] == 'usuarios':
            auth.authorize('usuarios', write=True)
            rows = [user_values(row) for row in rows]
        Repository.write_dataframe_to_table(pd.DataFrame(rows), params['table'])
    elif method == 'update':
        values = params['values']
        if params['table'] == 'usuarios':
            auth.authorize('usuarios', write=True)
            values = user_values(values)
        Repository.update_table(params['table'], values, params['where'])
    elif method == 'delete':
        Repository.delete_from_table(params['table'], params['where'])
    elif method == 'reclassificar':
        return DataService.reclassificar_vegetal_e_logar(params['nome'], params['tipo'], '')
    elif method == 'renomear':
        return DataService.rename_especie_gato_e_logar(params['antigo'], params['novo'], '')
    else:
        raise ValueError('Operação não permitida.')
    return {'ok': True}


@app.post('/rpc')
def rpc(message: Rpc, request: Request):
    authorization = request.headers.get('Authorization', '')
    token = authorization[7:] if authorization.startswith('Bearer ') else ''
    auth._session.set(None)
    try:
        throttle(request.client.host if request.client else 'unknown', message.method in {'login', 'sso/start'})
        if message.method == 'login':
            if not _hash_slots.acquire(blocking=False):
                return JSONResponse({'detail': 'Autenticação ocupada. Tente novamente.'}, status_code=429)
            try:
                user = auth.verify_user_credentials(message.params['username'], message.params['password'], message.params.get('otp', ''))
            finally:
                _hash_slots.release()
            if not isinstance(user, dict):
                return JSONResponse({'detail': 'Credenciais inválidas ou conta bloqueada.'}, status_code=401)
            if user.get('mfa_required'):
                return user
            return {'token': sessions.issue(), 'user': user}
        if message.method in {'sso/start', 'sso/poll'}:
            from . import sso
            if message.method == 'sso/start':
                return sso.start()
            return sso.poll(message.params['handle'], message.params.get('otp', ''))
        sessions.load(token)
        if message.method == 'logout':
            sessions.revoke(token)
            return {'ok': True}
        result = dispatch(message.method, message.params)
        sessions.refresh(token, active=message.method not in {'session', 'reauth/status'})
        return result
    except PermissionError as error:
        return JSONResponse({'detail': str(error)}, status_code=403)
    except (ValueError, KeyError, TypeError):
        return JSONResponse({'detail': 'Operação ou dados inválidos.'}, status_code=400)
    except ConnectionError:
        return JSONResponse({'detail': 'Serviço externo indisponível.'}, status_code=503)
    except SQLAlchemyError:
        logging.getLogger('api').error('Operação de banco não concluída.')
        return JSONResponse({'detail': 'Serviço de dados indisponível.'}, status_code=503)
    finally:
        auth._session.set(None)


@app.get('/sso/callback')
def sso_callback(code: str = '', state: str = ''):
    from . import sso
    try:
        sso.callback(code, state)
        return JSONResponse({'detail': 'Identidade confirmada. Volte ao NexlifyTTk.'},
                            headers={'Referrer-Policy': 'no-referrer', 'Content-Security-Policy': "default-src 'none'"})
    except (ValueError, PermissionError):
        return JSONResponse({'detail': 'Login SSO inválido ou expirado. Inicie novamente.'}, status_code=400)
