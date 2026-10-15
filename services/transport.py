from urllib.parse import urlsplit
import ssl
import config


def validate_service_url(url):
    parsed = urlsplit(url)
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Informe URL de serviço sem credenciais, query ou fragmento.')
    if parsed.scheme != 'https' and not (config.ENVIRONMENT == 'development' and parsed.scheme == 'http'
                                         and parsed.hostname in {'127.0.0.1', 'localhost', '::1'}):
        raise ValueError('Serviços exigem HTTPS; HTTP é permitido somente em loopback de desenvolvimento.')
    return url.rstrip('/')


def tls_context(cafile=None):
    return ssl.create_default_context(cafile=cafile or None)
