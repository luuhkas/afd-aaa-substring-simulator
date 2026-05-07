LARGURA, ALTURA = 1180, 720
FPS = 60
DURACAO_TRANSICAO = 1050

LARGURA_CANVAS = 748
LARGURA_PAINEL = 432  # LARGURA - LARGURA_CANVAS

ESTADOS = {
    "q0": (165, 400),
    "q1": (330, 400),
    "q2": (495, 400),
    "q3": (660, 400),
}

TRANSICOES = {
    ("q0", "a"): "q1",
    ("q0", "b"): "q0",
    ("q1", "a"): "q2",
    ("q1", "b"): "q0",
    ("q2", "a"): "q3",
    ("q2", "b"): "q0",
    ("q3", "a"): "q3",
    ("q3", "b"): "q3",
}

TRANSICOES_DESENHADAS = [
    ("q0", "a"),
    ("q1", "a"),
    ("q2", "a"),
    ("q0", "b"),
    ("q1", "b"),
    ("q2", "b"),
    ("q3", "a"),
]

# Fundo navy
FUNDO        = (8, 14, 38)
PAINEL       = (11, 19, 50)
PAINEL_2     = (17, 28, 68)
CANVAS_LINHA = (30, 50, 100)

TEXTO        = (238, 242, 255)
TEXTO_SUAVE  = (148, 162, 195)
TEXTO_CANVAS = (172, 184, 218)

BORDA        = (44, 64, 120)
BORDA_CLARA  = (78, 108, 182)

# One Dark Pro — semântica de ferramentas técnicas
CIANO        = (86, 182, 194)    # foco / cursor / q3 trap
CIANO_CLARO  = (168, 220, 228)
AZUL_CLARO   = (14, 32, 85)      # fundo do card "estado atual"
VERDE        = (152, 195, 121)   # transição 'a' / ACEITA
VERDE_CLARO  = (198, 232, 170)
VERMELHO     = (224, 108, 117)   # REJEITA
VERMELHO_CLARO = (248, 188, 192)
AMBAR        = (251, 191, 36)    # estado ativo / animação
AMBAR_CLARO  = (255, 238, 155)
LARANJA      = (209, 130, 60)    # transição 'b' / reset


def criar_fontes(pygame):
    return {
        "titulo":     pygame.font.SysFont("Arial", 34, bold=True),
        "normal":     pygame.font.SysFont("Arial", 20),
        "pequena":    pygame.font.SysFont("Arial", 15),
        "media":      pygame.font.SysFont("Arial", 24, bold=True),
        "estado":     pygame.font.SysFont("Courier New", 34, bold=True),
        "mono_media": pygame.font.SysFont("Courier New", 22, bold=True),
    }
