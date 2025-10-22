from .painel_gestao_gatos_controller import PainelGestaoGatos
from .painel_vegetais_auditoria_controller import PainelVegetaisAuditoria
from .painel_cadastro_vegetais_controller import PainelCadastroVegetais
from .painel_modelo_controller import PainelModelo
from .painel_guia_config_controller import PainelGuiaConfig

from .painel_gestao_usuarios_controller import PainelGestaoUsuariosController

ALL_PANELS = [
    PainelGestaoGatos,
    PainelVegetaisAuditoria,
    PainelCadastroVegetais,
                                 
    PainelGestaoUsuariosController,
    PainelModelo,
    PainelGuiaConfig,
]