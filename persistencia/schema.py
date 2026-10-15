"""Schema portável. A inicialização não apaga tabelas nem cria senhas padrão."""
from sqlalchemy import MetaData, Table, Column, String, Integer, DateTime, ForeignKey, Text, CheckConstraint, Identity, UniqueConstraint
metadata = MetaData()
ROLES = ('Administrador Global', 'Diretor de Operações', 'Gerente de TI', 'Supervisor de Produção',
         'Operador de Linha', 'Analista de Dados', 'Auditor Externo')
usuarios = Table('usuarios', metadata,
    Column('login_usuario', String(100), primary_key=True),
    Column('senha_criptografada', String(255), nullable=False),
    Column('nome_completo', String(200), nullable=False),
    Column('tipo_acesso', String(60), nullable=False),
    CheckConstraint('tipo_acesso IN (' + ', '.join(repr(role) for role in ROLES) + ')', name='ck_usuario_perfil'))
tipos_vegetais = Table('tipos_vegetais', metadata,
    Column('id', Integer, Identity(), primary_key=True), Column('nome', String(150), nullable=False, unique=True))
vegetais = Table('vegetais', metadata,
    Column('id', Integer, Identity(), primary_key=True), Column('nome', String(150), nullable=False),
    Column('id_tipo', Integer, ForeignKey('tipos_vegetais.id')))
especie_gatos = Table('especie_gatos', metadata,
    Column('id', Integer, Identity(), primary_key=True), Column('nome_especie', String(150), nullable=False, unique=True),
    Column('pais_origem', String(100)), Column('temperamento', String(200)))
log_alteracoes = Table('log_alteracoes', metadata,
    Column('id', Integer, Identity(), primary_key=True), Column('timestamp', DateTime, nullable=False),
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='SET NULL')),
    Column('acao', Text))
auth_state = Table('auth_state', metadata,
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='CASCADE'), primary_key=True),
    Column('failed_attempts', Integer, nullable=False, default=0),
    Column('locked_until', DateTime), Column('must_change', Integer, nullable=False, default=0))
schema_versions = Table('schema_versions', metadata,
    Column('version', Integer, primary_key=True), Column('applied_at', DateTime, nullable=False))

user_security = Table('user_security', metadata,
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='CASCADE'), primary_key=True),
    Column('mfa_secret', Text), Column('mfa_enabled', Integer, nullable=False, default=0),
    Column('pending_secret', Text), Column('pending_until', DateTime),
    Column('last_counter', Integer, nullable=False, default=-1),
    Column('recovery_hashes', Text), Column('security_version', Integer, nullable=False, default=0))
api_sessions = Table('api_sessions', metadata,
    Column('token_hash', String(64), primary_key=True),
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='CASCADE'), nullable=False),
    Column('credential_digest', String(64), nullable=False), Column('access_level', String(60), nullable=False),
    Column('security_version', Integer, nullable=False),
    Column('created_at', DateTime, nullable=False), Column('last_activity', DateTime, nullable=False),
    Column('reauthenticated_at', DateTime, nullable=False))
audit_outbox = Table('audit_outbox', metadata,
    Column('event_id', String(36), primary_key=True), Column('created_at', DateTime, nullable=False),
    Column('payload', Text, nullable=False), Column('attempts', Integer, nullable=False, default=0),
    Column('next_attempt', DateTime), Column('delivered_at', DateTime))
external_identities = Table('external_identities', metadata,
    Column('id', Integer, Identity(), primary_key=True), Column('issuer', String(255), nullable=False),
    Column('subject', String(255), nullable=False),
    UniqueConstraint('issuer', 'subject', name='uq_external_identity'),
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='CASCADE'), nullable=False))

email_mfa = Table('email_mfa', metadata,
    Column('login_usuario', String(100), ForeignKey('usuarios.login_usuario', ondelete='CASCADE'), primary_key=True),
    Column('email', String(254)), Column('pending_email', String(254)),
    Column('code_digest', String(64)), Column('nonce', String(32)),
    Column('code_until', DateTime), Column('purpose', String(20)), Column('sent_at', DateTime))
