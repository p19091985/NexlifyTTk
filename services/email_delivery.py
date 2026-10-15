"""Reusable server-side SMTP delivery through certificate-verified TLS."""
import re
import smtplib
import ssl
from email.message import EmailMessage


def validate_address(value):
    if (not isinstance(value, str) or len(value) > 254 or not value.isascii()
            or not re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}", value)):
        raise ValueError('Informe um endereço de e-mail válido, sem nome de exibição.')
    local, domain = value.rsplit('@', 1)
    if len(local) > 64 or local.startswith('.') or local.endswith('.') or '..' in value:
        raise ValueError('Endereço de e-mail inválido.')
    if any(not label or len(label) > 63 or label.startswith('-') or label.endswith('-') for label in domain.split('.')):
        raise ValueError('Domínio de e-mail inválido.')
    return local + '@' + domain.lower()


def send_email(address, subject, body, *, settings=None):
    from . import email_settings
    email_settings.require_server()
    address = validate_address(address)
    settings = email_settings.validate(settings) if settings is not None else email_settings.effective()
    if not settings['enabled']:
        raise ValueError('Envio de e-mail desabilitado. Configure e habilite o SMTP no servidor.')
    if (not isinstance(subject, str) or not 1 <= len(subject) <= 200
            or any(ord(c) < 32 or ord(c) == 127 for c in subject)):
        raise ValueError('Assunto de e-mail inválido.')
    if not isinstance(body, str) or len(body.encode('utf-8')) > 1048576:
        raise ValueError('Mensagem excede o limite de 1 MiB.')
    message = EmailMessage()
    message['From'], message['To'] = settings['sender'], address
    message['Subject'] = subject
    message.set_content(body)
    try:
        context = ssl.create_default_context(cafile=settings['ca'] or None)
        if settings['security'] == 'ssl':
            smtp = smtplib.SMTP_SSL(settings['host'], settings['port'], timeout=10, context=context)
        else:
            smtp = smtplib.SMTP(settings['host'], settings['port'], timeout=10)
        with smtp:
            if settings['security'] == 'starttls':
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
            if settings['auth'] == 'oauth2':
                from .email_oauth import access_token
                token = access_token(settings)
                # An error challenge must never cause credentials to be sent twice.
                initial = 'user=' + settings['username'] + '\x01auth=Bearer ' + token + '\x01\x01'
                smtp.auth('XOAUTH2', lambda challenge=None: initial if challenge is None else '')
            else:
                smtp.login(settings['username'], settings['password'])
            if smtp.send_message(message):
                raise smtplib.SMTPException('Delivery refused')
    except (OSError, smtplib.SMTPException, UnicodeError):
        raise ConnectionError('Não foi possível enviar o e-mail. Verifique o SMTP, a autenticação e o certificado.') from None
    # No automatic retry after DATA: the server may have accepted a message before a disconnect.


def send_code(address, code):
    send_email(address, 'NexlifyTTk — código de verificação',
        f'Seu código de verificação é: {code}\n\n'
        'Válido por cinco minutos e para um único uso. Não compartilhe este código.\n'
        'Se você não solicitou este acesso, ignore a mensagem.\n')


def send_test(address, *, settings=None):
    send_email(address, 'NexlifyTTk — teste de envio',
               'Teste de configuração SMTP do NexlifyTTk. Este e-mail não contém códigos de acesso.\n', settings=settings)
