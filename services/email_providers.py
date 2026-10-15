"""SMTP presets checked against provider documentation on 2026-10-15."""
PROVIDERS = {
    'gmail': dict(name='Gmail / Google Workspace', host='smtp.gmail.com', port=587, security='starttls', auth='password',
        note='Use senha de aplicativo com verificação em duas etapas, quando permitida pela conta.',
        source='https://support.google.com/mail/answer/7104828'),
    'outlook': dict(name='Outlook / Hotmail / Live', host='smtp-mail.outlook.com', port=587, security='starttls', auth='oauth2',
        token_url='https://login.microsoftonline.com/consumers/oauth2/v2.0/token',
        scope='https://outlook.office.com/SMTP.Send offline_access',
        note='Exige OAuth2. Informe o ID de um aplicativo Microsoft registrado e conecte a conta.',
        source='https://support.microsoft.com/en-au/outlook/pop-imap-and-smtp-settings-for-outlook-com'),
    'yahoo': dict(name='Yahoo Mail', host='smtp.mail.yahoo.com', port=465, security='ssl', auth='password',
        note='Use uma senha de aplicativo gerada na conta Yahoo.', source='https://help.yahoo.com/kb/SLN3217.html'),
    'icloud': dict(name='iCloud Mail', host='smtp.mail.me.com', port=587, security='starttls', auth='password',
        note='Use o endereço completo e uma senha específica de aplicativo Apple.', source='https://support.apple.com/102525'),
    'zoho': dict(name='Zoho Mail', host='smtp.zoho.com', port=465, security='ssl', auth='password',
        note='Preset pessoal do datacenter US. Para domínio corporativo/região diferente, confira o painel Zoho e ajuste o host. Use senha de aplicativo se exigida.',
        source='https://www.zoho.com/mail/help/zoho-smtp.html'),
    'aol': dict(name='AOL Mail', host='smtp.aol.com', port=465, security='ssl', auth='password',
        note='Use uma senha de aplicativo AOL.',
        source='https://help.aol.com/articles/how-do-i-use-other-email-applications-to-send-and-receive-my-aol-mail'),
    'gmx': dict(name='GMX', host='mail.gmx.com', port=587, security='starttls', auth='password',
        note='Confira a liberação de clientes externos e a senha de aplicativo se usar dois fatores. Preset GMX internacional.',
        source='https://support.gmx.com/pop-imap/imap/server.html'),
    'mailcom': dict(name='mail.com', host='smtp.mail.com', port=587, security='starttls', auth='password',
        note='Acesso por cliente externo depende do plano Premium e das permissões da conta.',
        source='https://support.mail.com/premium/imap/server.html'),
    'fastmail': dict(name='Fastmail', host='smtp.fastmail.com', port=465, security='ssl', auth='password',
        note='Use senha de aplicativo e plano com SMTP; o plano Basic não oferece esse acesso.',
        source='https://www.fastmail.help/hc/en-us/articles/1500000278342-Server-names-and-ports'),
    'yandex': dict(name='Yandex Mail', host='smtp.yandex.com', port=465, security='ssl', auth='password',
        note='Habilite clientes externos e gere uma senha de aplicativo Mail no Yandex ID.',
        source='https://yandex.com/support/yandex-360/customers/mail/en/mail-clients/others'),
    'custom': dict(name='SMTP personalizado', host='', port=587, security='starttls', auth='password',
        note='Configure host, porta, TLS e autenticação conforme seu servidor. Aceita CA privada e OAuth2 com refresh token.', source=''),
}


def defaults(provider='custom'):
    if provider not in PROVIDERS:
        raise ValueError('Provedor de e-mail desconhecido.')
    preset = PROVIDERS[provider]
    return dict(provider=provider, enabled=False, host=preset['host'], port=preset['port'],
                security=preset['security'], auth=preset['auth'], sender='', username='', password='',
                client_id='', client_secret='', refresh_token='', ca='',
                token_url=preset.get('token_url', ''), scope=preset.get('scope', ''))
