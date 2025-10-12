# panels/__init__.py

# Importa os painéis existentes e o novo painel de cadastro
from .painel_gestao_gatos_controller import PainelGestaoGatos
from .painel_vegetais_auditoria_controller import PainelVegetaisAuditoria
from .painel_cadastro_vegetais_controller import PainelCadastroVegetais  # <-- ADICIONE ESTA LINHA
from .painel_modelo_controller import PainelModelo

# Lista final de painéis que serão carregados pela aplicação.
ALL_PANELS = [
    PainelGestaoGatos,
    PainelVegetaisAuditoria,
    PainelCadastroVegetais,  # <-- ADICIONE ESTA LINHA
    PainelModelo,
]