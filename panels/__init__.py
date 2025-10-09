# panels/__init__.py

# -
# REGISTRO CENTRAL DE PAINÉIS
#
# Este arquivo importa a classe controladora principal de cada painel
# e a adiciona à lista `ALL_PANELS`. A aplicação principal (app.py) usa
# esta lista para carregar dinamicamente todos os painéis disponíveis.
# -

#  Painéis Principais de Funcionalidade 

# 1. Painel para gerir a tabela de Linguagens de Programação.
from .painelGestaoLinguagens import PainelGestaoLinguagens

# 2. Painel para visualizar a trilha de auditoria e testar transações.
from .painel_auditoria_controller import PainelAuditoria

# 3. Painel de Catálogo de Espécies (versão com lógica no mesmo arquivo).
from .painel_catalogo_controller import PainelCatalogoEspecies

#  Painéis que demonstram Padrões de Arquitetura e UI 

# 4. Painel de Gestão de Espécies (versão MVC original).
from .painel_especies_controller import PainelGestaoEspecies

# 5. Painel de Catálogo de Espécies (nova versão MVC, mais comentada).
from .painel_catalogo_mvc_controller import PainelCatalogoEspeciesMVC

# 6. Painel que demonstra todos os componentes visuais (Widgets).
from .painel_componentes_ui_controller import PainelComponentesUI

# 7. Painel modelo (template) para a criação de novas telas.
from .painel_modelo_controller import PainelModelo


#  LISTA FINAL DE PAINÉIS 
# A ordem nesta lista determina a ordem em que os botões aparecerão na barra lateral.

ALL_PANELS = [
    PainelGestaoLinguagens,       #
    PainelCatalogoEspecies,       #
    PainelCatalogoEspeciesMVC,    # Adicionado o novo painel MVC
    PainelGestaoEspecies,         #
    PainelAuditoria,              #
    PainelComponentesUI,          #
    PainelModelo,                 #
]