import sys

import pygame

from automato import AutomatoSimulator
from config import ALTURA, FPS, LARGURA, LARGURA_CANVAS, LARGURA_PAINEL, criar_fontes
from ui import Interface

_CAMPO = pygame.Rect(LARGURA_CANVAS + 24, 126, LARGURA_PAINEL - 48, 44)


def processar_eventos(automato, focado):
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if _CAMPO.collidepoint(evento.pos):
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
            automato.iniciar_execucao(pygame.time.get_ticks())
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

    automato = AutomatoSimulator()
    interface = Interface(tela, criar_fontes(pygame))
    clock = pygame.time.Clock()
    focado = True

    while True:
        focado = processar_eventos(automato, focado)
        automato.atualizar(pygame.time.get_ticks())
        interface.desenhar(automato, focado)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
