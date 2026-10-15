"""SMTP configuration on the server host; GUI or interactive terminal without secrets in argv."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import getpass
import json
import time
from services import email_settings, email_oauth
from services.email_delivery import send_test
from services.email_providers import PROVIDERS, defaults


def configure():
    if email_settings.environment_active():
        raise ValueError('SMTP está configurado pelo ambiente. Remova essas variáveis para salvar pelo assistente.')
    print('Provedores: '+', '.join(PROVIDERS))
    provider = input('Provedor [custom]: ').strip() or 'custom'
    data = defaults(provider)
    print(PROVIDERS[provider]['note'])
    for key, title in (('host', 'Servidor'), ('port', 'Porta'), ('security', 'Segurança: starttls/ssl'),
                       ('sender', 'E-mail remetente'), ('username', 'Usuário SMTP'), ('auth', 'Autenticação: password/oauth2')):
        data[key] = input(f'{title} [{data[key]}]: ').strip() or data[key]
    if data['auth'] == 'password':
        data['password'] = getpass.getpass('Senha / senha de aplicativo: ')
    elif provider == 'outlook':
        data['client_id'] = input('Application (client) ID Microsoft: ').strip()
        flow = email_oauth.start_microsoft(data['client_id'])
        print('Abra '+flow['verification_uri']+' e informe o código '+flow['user_code'])
        while True:
            token = email_oauth.poll_microsoft(flow)
            if token:
                data['refresh_token'] = token
                break
            time.sleep(min(flow['interval'], 60))
    else:
        for key, title in (('client_id', 'Client ID'), ('token_url', 'Endpoint de token HTTPS'), ('scope', 'Escopos')):
            data[key] = input(title+': ').strip()
        data['client_secret'] = getpass.getpass('Segredo do aplicativo (opcional): ')
        data['refresh_token'] = getpass.getpass('Refresh token: ')
    data['ca'] = input('Arquivo de CA privada (opcional): ').strip()
    data['enabled'] = input('Habilitar envios por esta conta? [s/N]: ').lower() == 's'
    email_settings.save(data)
    print('Configuração salva e protegida. O estado do MFA não foi alterado.')


def main():
    parser = argparse.ArgumentParser(description='Configurar SMTP na máquina do servidor ou aplicação local.')
    parser.add_argument('--headless', action='store_true', help='Assistente interativo de terminal')
    parser.add_argument('--list', action='store_true', help='Listar provedores e parâmetros públicos')
    parser.add_argument('--test-to', help='Enviar um e-mail de teste com a configuração efetiva')
    args = parser.parse_args()
    try:
        email_settings.require_server()
        if args.list:
            print(json.dumps(PROVIDERS, ensure_ascii=False, indent=2))
        elif args.test_to:
            send_test(args.test_to)
            print('Mensagem aceita pelo servidor SMTP. Confira a caixa de entrada e o spam.')
        elif args.headless:
            configure()
        else:
            import tkinter as tk
            from dialogs.email_settings_dialog import EmailSettingsDialog
            root = tk.Tk()
            root.withdraw()
            # This standalone operation is authorized by access to the server OS account,
            # like the database provisioning utility; it is never exposed through RPC.
            def local_operator(parent):
                email_settings.require_server()
                return True
            dialog = EmailSettingsDialog(root, authorize=local_operator)
            root.wait_window(dialog)
            root.destroy()
    except (ValueError, PermissionError, ConnectionError, OSError) as error:
        parser.exit(1, str(error)+'\n')


if __name__ == '__main__':
    main()
