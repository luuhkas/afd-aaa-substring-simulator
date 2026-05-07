import os
import sys

import pygame

from automato import AutomatoSimulator
from config import ALTURA, BADGE_REGISTRO_W, FPS, LARGURA, LARGURA_CANVAS, LARGURA_PAINEL, criar_fontes
from ui import CONC_BTN_FECHAR, CONC_BTN_REINICIAR, Interface, seletor_row_at

_CAMPO         = pygame.Rect(LARGURA_CANVAS + 24, 126, LARGURA_PAINEL - 48, 44)
_BOTAO_ARQUIVO = pygame.Rect(LARGURA_CANVAS + 24, 500, LARGURA_PAINEL - 48, 40)
_STRIP_RECT    = pygame.Rect(0, 622, LARGURA_CANVAS, ALTURA - 622)

_DIRETORIO = os.path.dirname(os.path.abspath(__file__))


def _listar_txts():
    return sorted(f for f in os.listdir(_DIRETORIO) if f.endswith(".txt"))


def _clamp_scroll(automato, registro):
    visivel    = LARGURA_CANVAS - 32
    total      = len(automato.fila) * BADGE_REGISTRO_W
    max_scroll = max(0, total - visivel)
    registro["scroll_x"] = max(0, min(max_scroll, registro["scroll_x"]))


def processar_eventos(automato, focado, seletor, registro):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── tela de conclusão ────────────────────────────────
        if automato.concluido:
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if CONC_BTN_REINICIAR.collidepoint(evento.pos):
                    automato.reset_manual()
                    registro["scroll_x"] = 0
                    focado = True
                elif CONC_BTN_FECHAR.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()
            continue

        # ── seletor aberto ───────────────────────────────────
        if seletor["aberto"]:
            if evento.type == pygame.MOUSEMOTION:
                seletor["hover"] = seletor_row_at(seletor, *evento.pos)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                idx = seletor_row_at(seletor, *evento.pos)
                if idx >= 0:
                    caminho = os.path.join(_DIRETORIO, seletor["arquivos"][idx])
                    automato.carregar_arquivo(caminho)
                    registro["scroll_x"] = 0
                    focado = False
                seletor["aberto"] = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                seletor["aberto"] = False
            continue

        # ── drag no registro ─────────────────────────────────
        if evento.type == pygame.MOUSEBUTTONUP:
            registro["drag"] = False

        if evento.type == pygame.MOUSEMOTION and registro["drag"]:
            dx = evento.pos[0] - registro["drag_start_x"]
            registro["scroll_x"] = registro["drag_scroll_start"] - dx
            _clamp_scroll(automato, registro)
            continue

        # ── modo normal ──────────────────────────────────────
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if _STRIP_RECT.collidepoint(evento.pos) and automato.modo_arquivo:
                registro["drag"]             = True
                registro["drag_start_x"]     = evento.pos[0]
                registro["drag_scroll_start"] = registro["scroll_x"]
            elif _BOTAO_ARQUIVO.collidepoint(evento.pos) and not automato.modo_arquivo:
                seletor["arquivos"] = _listar_txts()
                seletor["hover"]    = -1
                seletor["aberto"]   = True
            elif _CAMPO.collidepoint(evento.pos) and not automato.modo_arquivo:
                focado = True
                automato.cursor = len(automato.palavra)
            else:
                focado = False
            continue

        if evento.type != pygame.KEYDOWN:
            continue

        if evento.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if evento.key == pygame.K_RETURN:
            if not automato.modo_arquivo:
                automato.iniciar_execucao(pygame.time.get_ticks())
            continue

        if automato.modo_arquivo:
            continue

        if not focado:
            continue

        if evento.key == pygame.K_BACKSPACE:
            automato.apagar_simbolo()
        elif evento.key == pygame.K_DELETE:
            automato.deletar_simbolo()
        elif evento.key == pygame.K_LEFT:
            automato.mover_cursor(-1)
        elif evento.key == pygame.K_RIGHT:
            automato.mover_cursor(1)
        elif evento.key == pygame.K_HOME:
            automato.mover_cursor(-len(automato.palavra))
        elif evento.key == pygame.K_END:
            automato.mover_cursor(len(automato.palavra))
        elif not automato.executando:
            automato.adicionar_simbolo(evento.unicode.lower())

    return focado


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("AFD - Linguagem com aaa")

    automato  = AutomatoSimulator()
    interface = Interface(tela, criar_fontes(pygame))
    clock     = pygame.time.Clock()
    focado    = True
    seletor   = {"aberto": False, "arquivos": [], "hover": -1}
    registro  = {"scroll_x": 0, "drag": False, "drag_start_x": 0, "drag_scroll_start": 0}

    while True:
        focado = processar_eventos(automato, focado, seletor, registro)
        automato.atualizar(pygame.time.get_ticks())
        interface.desenhar(automato, focado, seletor, registro["scroll_x"])
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
