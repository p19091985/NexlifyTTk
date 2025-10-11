# panels/__init__.py
from .painelGestaoLinguagens import PainelGestaoLinguagens
from .painel_auditoria_controller import PainelAuditoria
from .painel_catalogo_controller import PainelCatalogoEspecies
from .painel_especies_controller import PainelGestaoEspecies
from .painel_catalogo_mvc_controller import PainelCatalogoEspeciesMVC
from .painel_componentes_ui_controller import PainelComponentesUI
from .painel_modelo_controller import PainelModelo

ALL_PANELS = [
    PainelGestaoLinguagens,
    PainelCatalogoEspecies,
    PainelCatalogoEspeciesMVC,
    PainelGestaoEspecies,
    PainelAuditoria,
    PainelComponentesUI,
    PainelModelo,
]