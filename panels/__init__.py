# panels/__init__.py

# Importa as classes de cada módulo de painel
from .painel_01 import PainelVisualizacaoDados
from .painel_02 import PainelTiposLinguagem
from .painel_03 import PainelDashboard
from .painel_04 import PainelWidgetsVisuais
from .painel_05 import PainelFormularios

# Cria uma lista explícita com todas as classes de painel.
# Esta lista é usada pelo app.py para carregar todos os painéis disponíveis.
ALL_PANELS = [
    PainelVisualizacaoDados,
    PainelTiposLinguagem,
    PainelDashboard,
    PainelWidgetsVisuais,
    PainelFormularios,
]