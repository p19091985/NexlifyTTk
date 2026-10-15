"""Política única de páginas e dados. Recursos não cadastrados são negados."""
from dataclasses import dataclass
from types import MappingProxyType

from .schema import ROLES

ADMIN = 'Administrador Global'
AUDITOR = 'Auditor Externo'
ALL_ROLES = frozenset(ROLES)
ADMIN_ONLY = frozenset({ADMIN})
TECH_ROLES = frozenset({ADMIN, 'Gerente de TI'})
VEGETABLE_ROLES = frozenset({ADMIN, 'Diretor de Operações', 'Gerente de TI', 'Analista de Dados'})
AUDIT_ROLES = VEGETABLE_ROLES | {AUDITOR}
WRITERS = ALL_ROLES - {AUDITOR}


@dataclass(frozen=True)
class PageRule:
    roles: frozenset
    development_only: bool = False
    local_only: bool = False
    read_only_roles: frozenset = frozenset()


PAGE_RULES = MappingProxyType({
    'Cadastro de Vegetais': PageRule(VEGETABLE_ROLES),
    'Gestão de Espécies (Gatos)': PageRule(ALL_ROLES, read_only_roles=frozenset({AUDITOR})),
    'Gestão de Usuários': PageRule(ADMIN_ONLY),
    'Guia de Configuração': PageRule(ALL_ROLES),
    'Painel Modelo': PageRule(ADMIN_ONLY, development_only=True, local_only=True),
    'Vegetais e Auditoria': PageRule(AUDIT_ROLES, read_only_roles=frozenset({AUDITOR})),
    'settings.types': PageRule(VEGETABLE_ROLES),
    'settings.smtp': PageRule(ADMIN_ONLY, local_only=True),
    'settings.theme': PageRule(ALL_ROLES),
    'settings.computer': PageRule(TECH_ROLES),
    'settings.diagnostics': PageRule(TECH_ROLES),
    'help.about': PageRule(ALL_ROLES),
    'help.installation': PageRule(ALL_ROLES),
    'dev.tests': PageRule(ADMIN_ONLY, development_only=True, local_only=True),
    'dev.processes': PageRule(ADMIN_ONLY, development_only=True, local_only=True),
    'dev.tools': PageRule(ADMIN_ONLY, development_only=True, local_only=True),
    'dev.reset_preferences': PageRule(ADMIN_ONLY, development_only=True, local_only=True),
})


class PageAccessDenied(PermissionError):
    """Sessão válida, mas sem autorização para esta página."""


def can_access_page(role, page, *, profile_id='core', environment='production', api_mode='local'):
    rule = PAGE_RULES.get(page) if isinstance(page, str) else None
    if not rule or not isinstance(role, str) or role not in rule.roles:
        return False
    if rule.development_only and (profile_id != 'dev' or environment != 'development'):
        return False
    return not (rule.local_only and api_mode == 'client')


def can_access_table(role, table, *, write=False):
    if role not in ALL_ROLES:
        return False
    if table == 'usuarios':
        return role == ADMIN
    if table in {'vegetais', 'tipos_vegetais'}:
        return role in (VEGETABLE_ROLES if write else AUDIT_ROLES)
    if table == 'especie_gatos':
        return not write or role in WRITERS
    if table == 'log_alteracoes':
        return not write and role in AUDIT_ROLES
    return False
