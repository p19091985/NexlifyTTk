# panels/__init__.py

# Importa as classes de cada módulo de painel
from .painel_01_controller import PainelVisualizacaoDados
from .painel_01Junto import PainelVisualizacaoDadosJunto
from .painel_01_separado_junto import PainelVisualizacaoDadosSeparadoJunto
from .painel_02 import PainelExemplosBootstrap
from .painel_03 import PainelDashboard
from .painel_04 import PainelWidgetsVisuais
from .painel_05 import PainelFormularios
from .painel_06 import PainelEsqueleto
from .painel_07 import PainelTransacoes

# --- MODIFICAÇÃO: Adicionada a importação do novo painel ---
from .painel_08 import PainelCrudCompleto


# A lista agora contém todos os painéis
ALL_PANELS = [
    PainelVisualizacaoDadosJunto,
    PainelVisualizacaoDados,
    PainelVisualizacaoDadosSeparadoJunto,
    PainelExemplosBootstrap,
    PainelDashboard,
    PainelWidgetsVisuais,
    PainelFormularios,
    PainelEsqueleto,
    PainelTransacoes,
    PainelCrudCompleto, # <-- Adicionado à lista
]