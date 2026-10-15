"""Start the API explicitly. Production requires a TLS certificate and key."""
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='NexlifyTTk API central')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8443)
    parser.add_argument('--cert')
    parser.add_argument('--key')
    args = parser.parse_args()
    os.environ['NEXLIFY_API_MODE'] = 'server'
    import config
    config.API_MODE = 'server'
    config.validate()
    if not (args.cert and args.key) and (config.ENVIRONMENT != 'development' or args.host not in {'127.0.0.1', '::1'}):
        parser.error('Servidor exige --cert e --key; HTTP somente em loopback de desenvolvimento.')
    from persistencia.logger import setup_loggers
    setup_loggers()
    import uvicorn
    uvicorn.run('services.api:app', host=args.host, port=args.port, ssl_certfile=args.cert, ssl_keyfile=args.key,
                proxy_headers=False, access_log=False, server_header=False, limit_concurrency=64, timeout_keep_alive=5)


if __name__ == '__main__':
    main()
