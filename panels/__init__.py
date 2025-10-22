from .painel_gestao_gatos import PainelGestaoGatos
# REMOVIDA: from .painel_vegetais_auditoria import PainelVegetaisAuditoria
from .painel_cadastro_vegetais import PainelCadastroVegetais
from .painel_modelo  import PainelModelo
from .painel_guia_config import PainelGuiaConfig
from .painel_gestao_usuarios import PainelGestaoUsuariosController

ALL_PANELS = [
    PainelGestaoGatos,
    # REMOVIDA: PainelVegetaisAuditoria,
    PainelCadastroVegetais,
    PainelGestaoUsuariosController,
    PainelModelo,
    PainelGuiaConfig,
]