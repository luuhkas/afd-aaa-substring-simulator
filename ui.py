import math

import pygame

from config import (
    ALTURA,
    AMBAR,
    AMBAR_CLARO,
    AZUL_CLARO,
    BADGE_REGISTRO_W,
    LARANJA,
    BORDA,
    BORDA_CLARA,
    CANVAS_LINHA,
    CIANO,
    CIANO_CLARO,
    DURACAO_TRANSICAO,
    ESTADOS,
    FUNDO,
    LARGURA,
    LARGURA_CANVAS,
    LARGURA_PAINEL,
    PAINEL,
    PAINEL_2,
    TEXTO,
    TEXTO_CANVAS,
    TEXTO_SUAVE,
    TRANSICOES_DESENHADAS,
    VERDE,
    VERDE_CLARO,
    VERMELHO,
    VERMELHO_CLARO,
)
from geometry import caminho_transicao, misturar, ponto_no_caminho, pontos_cabeca_seta, posicao_rotulo

_PX = LARGURA_CANVAS + 24
_PW = LARGURA_PAINEL - 48

# ── seletor de arquivo ────────────────────────────────────────────────────────
_SEL_W       = 380
_SEL_X       = (LARGURA - _SEL_W) // 2
_SEL_TITLE_H = 48
_SEL_ROW_H   = 40
_SEL_PAD_BOT = 14


def _seletor_rect(n):
    h = _SEL_TITLE_H + n * _SEL_ROW_H + _SEL_PAD_BOT
    y = (ALTURA - h) // 2
    return pygame.Rect(_SEL_X, y, _SEL_W, h)


# ── tela de conclusão ────────────────────────────────────────────────────────
_CONC_W  = 380
_CONC_H  = 268
_CONC_X  = (LARGURA - _CONC_W) // 2
_CONC_Y  = (ALTURA  - _CONC_H) // 2
_CONC_PX = _CONC_X + 20
_CONC_PW = _CONC_W - 40

CONC_BTN_REINICIAR = pygame.Rect(_CONC_PX, _CONC_Y + 136, _CONC_PW, 52)
CONC_BTN_FECHAR    = pygame.Rect(_CONC_PX, _CONC_Y + 202, _CONC_PW, 46)


def seletor_row_at(seletor, mx, my):
    """Retorna o índice da linha do seletor sob (mx, my), ou -1."""
    arqs = seletor.get("arquivos", [])
    if not arqs:
        return -1
    r = _seletor_rect(len(arqs))
    if not r.collidepoint(mx, my):
        return -1
    for i in range(len(arqs)):
        row = pygame.Rect(r.x + 1, r.y + _SEL_TITLE_H + i * _SEL_ROW_H, r.w - 2, _SEL_ROW_H)
        if row.collidepoint(mx, my):
            return i
    return -1


class Interface:
    def __init__(self, tela, fontes):
        self.tela = tela
        self.fontes = fontes
        self._pertence_cache = {}

    def desenhar(self, automato, focado=True, seletor=None, scroll_x=0):
        self.tela.fill(FUNDO)
        self._painel(automato, focado)
        self._canvas(automato, scroll_x)
        if automato.concluido:
            self._conclusao(automato)
        elif seletor and seletor.get("aberto"):
            self._seletor(seletor)

    # ── primitivas ────────────────────────────────────────────────────────────

    def _txt(self, texto, x, y, cor=TEXTO, fonte="normal", centro=False):
        img = self.fontes[fonte].render(texto, True, cor)
        rect = img.get_rect(center=(x, y)) if centro else img.get_rect(topleft=(x, y))
        self.tela.blit(img, rect)
        return rect

    def _card(self, rect, cor=PAINEL, borda=BORDA, raio=12):
        pygame.draw.rect(self.tela, cor, rect, border_radius=raio)
        pygame.draw.rect(self.tela, borda, rect, 1, border_radius=raio)

    def _chip(self, texto, rect, fundo, cor=TEXTO, fonte="pequena"):
        pygame.draw.rect(self.tela, fundo, rect, border_radius=rect.height // 2)
        self._txt(texto, rect.centerx, rect.centery, cor, fonte, centro=True)

    def _linha(self, pontos, cor, largura):
        pygame.draw.lines(self.tela, cor, False, pontos, largura)
        pygame.draw.aalines(self.tela, cor, False, pontos)

    def _rotulo(self, texto, pos, cor=CIANO):
        img = self.fontes["pequena"].render(texto, True, cor)
        rect = img.get_rect(center=pos)
        caixa = rect.inflate(18, 10)
        pygame.draw.rect(self.tela, FUNDO, caixa, border_radius=10)
        pygame.draw.rect(self.tela, misturar(cor, BORDA, 0.5), caixa, 1, border_radius=10)
        self.tela.blit(img, rect)

    def _div(self, y):
        pygame.draw.line(self.tela, BORDA, (_PX, y), (_PX + _PW, y), 1)

    def _pertence(self, sx, sy, cor):
        if cor not in self._pertence_cache:
            h, w = 12, 11
            H, W, t = h * 4, w * 4, 8
            r = H // 2 - t // 2
            CX, CY = t // 2 + r, H // 2
            surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pts = [(CX + r * math.cos(math.pi / 2 + i * math.pi / 56),
                    CY + r * math.sin(math.pi / 2 + i * math.pi / 56))
                   for i in range(57)]
            pygame.draw.lines(surf, cor, False, pts, t)
            pygame.draw.line(surf, cor, (CX - t // 2, CY - r), (W - 4, CY - r), t)
            pygame.draw.line(surf, cor, (t // 2,       CY    ), (W - 8, CY    ), t)
            pygame.draw.line(surf, cor, (CX - t // 2, CY + r), (W - 4, CY + r), t)
            self._pertence_cache[cor] = pygame.transform.smoothscale(surf, (w, h))
        self.tela.blit(self._pertence_cache[cor], (sx, sy))

    # ── painel direito ────────────────────────────────────────────────────────

    def _painel(self, automato, focado):
        pygame.draw.rect(self.tela, PAINEL,
                         pygame.Rect(LARGURA_CANVAS, 0, LARGURA_PAINEL, ALTURA))
        pygame.draw.line(self.tela, BORDA,
                         (LARGURA_CANVAS, 0), (LARGURA_CANVAS, ALTURA), 1)

        self._txt("Simulator", _PX, 40, TEXTO, "titulo")
        if automato.modo_arquivo:
            chip_txt = f"{automato.indice_fila + 1} / {len(automato.fila)}"
            chip_r = pygame.Rect(_PX + _PW - 72, 32, 72, 22)
            self._chip(chip_txt, chip_r, (20, 36, 80), CIANO, "pequena")

        self._div(96)

        self._txt("ENTRADA", _PX, 108, TEXTO_SUAVE, "pequena")
        campo = pygame.Rect(_PX, 126, _PW, 44)
        borda_campo = CIANO if focado else BORDA
        fundo_campo = (20, 36, 80) if focado else PAINEL_2
        self._card(campo, fundo_campo, borda_campo, 10)
        palavra = automato.palavra if automato.palavra else "digite a ou b"
        self._txt(palavra, _PX + 14, 139, TEXTO if automato.palavra else TEXTO_SUAVE, "mono_media")
        if focado and not automato.executando:
            texto_ate_cursor = automato.palavra[:automato.cursor]
            cx = min(_PX + _PW - 10,
                     _PX + 14 + self.fontes["mono_media"].size(texto_ate_cursor)[0])
            if (pygame.time.get_ticks() // 530) % 2 == 0:
                pygame.draw.line(self.tela, CIANO, (cx, 133), (cx, 161), 2)

        self._div(184)

        self._txt("LEITURA", _PX, 196, TEXTO_SUAVE, "pequena")
        self._fita(automato)
        self._progresso(automato)

        self._div(292)

        self._txt("ESTADO ATUAL", _PX, 304, TEXTO_SUAVE, "pequena")
        estado_r = pygame.Rect(_PX, 324, _PW, 48)
        self._card(estado_r, AZUL_CLARO, CIANO, 12)
        self._txt(automato.estado_atual, estado_r.centerx, estado_r.centery,
                  CIANO, "mono_media", centro=True)

        self._div(390)

        self._resultado(automato)
        if not automato.modo_arquivo:
            self._botao_arquivo()
            self._atalhos(automato, y=552)
        else:
            self._atalhos(automato, y=500)

    def _fita(self, automato):
        x, y = _PX, 216
        if not automato.palavra:
            self._txt("Sem entrada", x, y + 8, TEXTO_SUAVE, "pequena")
            return
        for i, letra in enumerate(automato.palavra[:12]):
            ativo = i == automato.indice and automato.executando
            lido  = i < automato.indice
            fundo = (24, 44, 90) if ativo else PAINEL_2
            borda = AMBAR if ativo else BORDA_CLARA if lido else BORDA
            rect  = pygame.Rect(x + i * 28, y, 24, 30)
            self._card(rect, fundo, borda, 6)
            cor = AMBAR if ativo else TEXTO_SUAVE if lido else TEXTO
            self._txt(letra, rect.centerx, rect.centery, cor, "pequena", centro=True)
        if len(automato.palavra) > 12:
            self._txt("...", x + 340, y + 6, TEXTO_SUAVE, "pequena")

    def _progresso(self, automato):
        trilha = pygame.Rect(_PX, 256, _PW, 4)
        pygame.draw.rect(self.tela, PAINEL_2, trilha, border_radius=2)
        total = max(1, len(automato.palavra))
        p = automato.indice / total if automato.palavra else 0
        if automato.executando and automato.indice < len(automato.palavra):
            p = max(p, (automato.indice + 0.35) / total)
        preen = pygame.Rect(trilha.x, trilha.y, round(trilha.width * min(1, p)), trilha.height)
        if preen.width:
            pygame.draw.rect(self.tela, CIANO, preen, border_radius=2)
        self._txt(f"{automato.indice} / {len(automato.palavra)} simbolos lidos",
                  _PX, 270, TEXTO_SUAVE, "pequena")

    def _resultado(self, automato):
        rect = pygame.Rect(_PX, 406, _PW, 78)
        if not automato.resultado:
            self._card(rect, PAINEL_2, BORDA, 12)
            self._txt("RESULTADO", _PX + 16, 421, TEXTO_SUAVE, "pequena")
            self._txt("Aguardando execucao", _PX + 16, 444, TEXTO_SUAVE)
            return
        aceitou = automato.resultado == "ACEITA"
        fundo = (16, 44, 24) if aceitou else (48, 18, 24)
        borda = VERDE if aceitou else VERMELHO
        cor   = VERDE_CLARO if aceitou else VERMELHO_CLARO
        self._card(rect, fundo, borda, 12)
        pygame.draw.rect(self.tela, borda, pygame.Rect(_PX, 406, 4, 78), border_radius=2)
        self._txt("RESULTADO", _PX + 20, 421, cor, "pequena")
        self._txt(automato.resultado, _PX + 20, 444, cor, "media")

    def _botao_arquivo(self):
        mx, my = pygame.mouse.get_pos()
        rect = pygame.Rect(_PX, 500, _PW, 40)
        hover = rect.collidepoint(mx, my)
        fundo = (22, 40, 96) if hover else (14, 24, 66)
        borda = CIANO if hover else BORDA_CLARA
        self._card(rect, fundo, borda, 10)
        cx, cy = rect.centerx, rect.centery
        # ícone pasta
        pw, ph = 14, 10
        fx = cx - 58
        fy = cy - ph // 2
        pygame.draw.rect(self.tela, borda, (fx, fy + 3, pw, ph - 3), border_radius=2)
        pygame.draw.rect(self.tela, borda, (fx, fy + 3, 6, 3))
        pygame.draw.rect(self.tela, borda, (fx, fy, 6, 4), border_radius=1)
        self._txt("Abrir arquivo", cx - 40, cy, CIANO if hover else TEXTO_SUAVE, "pequena")

    def _atalhos(self, automato, y=500):
        if automato.modo_arquivo:
            atalhos     = [("ESC", "sair")]
            altura_card = 52
        else:
            atalhos = [
                ("ENTER",     "executar"),
                ("BACKSPACE", "apagar"),
                ("ESC",       "sair"),
            ]
            altura_card = 96
        rect = pygame.Rect(_PX, y, _PW, altura_card)
        self._card(rect, PAINEL_2, BORDA, 12)
        for i, (tecla, acao) in enumerate(atalhos):
            ry = y + 14 + i * 26
            pygame.draw.circle(self.tela, BORDA_CLARA, (_PX + 12, ry + 7), 3)
            self._txt(tecla, _PX + 24, ry, CIANO, "pequena")
            kw = self.fontes["pequena"].size(tecla)[0]
            self._txt(acao, _PX + 24 + kw + 10, ry, TEXTO_SUAVE, "pequena")

    # ── tela de conclusão ────────────────────────────────────────────────────

    def _conclusao(self, automato):
        mx, my = pygame.mouse.get_pos()

        backdrop = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 165))
        self.tela.blit(backdrop, (0, 0))

        card = pygame.Rect(_CONC_X, _CONC_Y, _CONC_W, _CONC_H)
        self._card(card, (11, 19, 52), BORDA_CLARA, 16)

        n_aceitas  = sum(1 for _, r in automato.historico if r == "ACEITA")
        n_rejeitas = len(automato.historico) - n_aceitas

        self._txt("Leitura concluída",
                  card.centerx, _CONC_Y + 24, TEXTO, "normal", centro=True)

        pygame.draw.line(self.tela, BORDA,
                         (_CONC_X + 16, _CONC_Y + 50),
                         (_CONC_X + _CONC_W - 16, _CONC_Y + 50), 1)

        # resumo colorido
        cy = _CONC_Y + 68
        self._txt(f"{len(automato.historico)} sentencas processadas",
                  card.centerx, cy, TEXTO_SUAVE, "pequena", centro=True)
        self._txt(f"{n_aceitas} aceitas",
                  card.centerx - 52, cy + 22, VERDE, "pequena", centro=True)
        self._txt("|", card.centerx, cy + 22, BORDA_CLARA, "pequena", centro=True)
        self._txt(f"{n_rejeitas} rejeitadas",
                  card.centerx + 52, cy + 22, VERMELHO, "pequena", centro=True)

        # descrição da ação
        self._txt("Limpa o simulador e volta ao estado inicial.",
                  card.centerx, _CONC_Y + 120, TEXTO_SUAVE, "pequena", centro=True)

        # botão reiniciar
        h1 = CONC_BTN_REINICIAR.collidepoint(mx, my)
        self._card(CONC_BTN_REINICIAR,
                   (22, 40, 96) if h1 else (14, 24, 66),
                   CIANO if h1 else BORDA_CLARA, 10)
        self._txt("Reiniciar simulador",
                  CONC_BTN_REINICIAR.centerx, CONC_BTN_REINICIAR.centery,
                  CIANO if h1 else TEXTO, "normal", centro=True)

        # botão fechar
        h2 = CONC_BTN_FECHAR.collidepoint(mx, my)
        self._card(CONC_BTN_FECHAR,
                   (52, 18, 22) if h2 else (22, 10, 12),
                   VERMELHO if h2 else (80, 40, 44), 10)
        self._txt("Fechar simulador",
                  CONC_BTN_FECHAR.centerx, CONC_BTN_FECHAR.centery,
                  VERMELHO_CLARO if h2 else (160, 80, 88), "normal", centro=True)

    # ── seletor de arquivo ───────────────────────────────────────────────────

    def _seletor(self, seletor):
        arqs = seletor.get("arquivos", [])
        hover = seletor.get("hover", -1)
        r = _seletor_rect(len(arqs))

        backdrop = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 155))
        self.tela.blit(backdrop, (0, 0))

        self._card(r, (11, 19, 52), BORDA_CLARA, 14)

        title_r = pygame.Rect(r.x, r.y, r.w, _SEL_TITLE_H)
        pygame.draw.rect(self.tela, (17, 28, 70), title_r, border_radius=14)
        pygame.draw.rect(self.tela, (17, 28, 70),
                         pygame.Rect(r.x, r.y + 6, r.w, _SEL_TITLE_H - 6))
        self._txt("Selecionar arquivo", r.x + 18, r.y + 14, TEXTO, "normal")
        self._txt("ESC para fechar", r.right - 100, r.y + 17, TEXTO_SUAVE, "pequena")

        pygame.draw.line(self.tela, BORDA,
                         (r.x + 1, r.y + _SEL_TITLE_H),
                         (r.right - 1, r.y + _SEL_TITLE_H), 1)

        if not arqs:
            self._txt("Nenhum arquivo .txt encontrado",
                      r.centerx, r.y + _SEL_TITLE_H + 20, TEXTO_SUAVE, "pequena")
            return

        for i, nome in enumerate(arqs):
            row = pygame.Rect(r.x + 1, r.y + _SEL_TITLE_H + i * _SEL_ROW_H,
                              r.w - 2, _SEL_ROW_H)
            if i == hover:
                pygame.draw.rect(self.tela, (22, 38, 90), row)
            pygame.draw.line(self.tela, BORDA,
                             (row.x + 16, row.bottom - 1),
                             (row.right - 16, row.bottom - 1), 1)
            cor = CIANO if i == hover else TEXTO
            self._txt(nome, row.x + 44, row.y + 12, cor, "normal")
            # ícone arquivo
            ix, iy = row.x + 18, row.y + 11
            pygame.draw.rect(self.tela, BORDA_CLARA, (ix, iy, 12, 15), border_radius=1)
            pygame.draw.polygon(self.tela, (11, 19, 52),
                                [(ix + 7, iy), (ix + 12, iy + 5), (ix + 7, iy + 5)])
            pygame.draw.line(self.tela, BORDA_CLARA, (ix + 7, iy), (ix + 12, iy + 5), 1)

    # ── canvas esquerdo ───────────────────────────────────────────────────────

    def _canvas(self, automato, scroll_x=0):
        self._dots()
        self._header_canvas()

        q0x, q0y = ESTADOS["q0"]
        self._linha([(q0x - 80, q0y), (q0x - 46, q0y)], BORDA_CLARA, 3)
        pygame.draw.polygon(self.tela, BORDA_CLARA,
                            pontos_cabeca_seta((q0x - 46, q0y), (q0x - 80, q0y), 12))
        self._rotulo("inicio", (q0x - 62, q0y - 28), TEXTO_CANVAS)

        for origem, simbolo in TRANSICOES_DESENHADAS:
            self._transicao(automato, origem, simbolo)
        self._particula(automato)
        for nome in ESTADOS:
            self._estado(automato, nome)
        self._registro(automato, scroll_x)

    def _registro(self, automato, scroll_x=0):
        if not automato.modo_arquivo or not automato.fila:
            return

        n        = len(automato.fila)
        badge_w  = BADGE_REGISTRO_W
        badge_h  = 46
        stripe_y = 624
        visivel  = LARGURA_CANVAS - 32
        total_w  = badge_w * n

        pygame.draw.line(self.tela, BORDA, (16, stripe_y), (LARGURA_CANVAS - 16, stripe_y), 1)
        self._txt("REGISTRO", 24, stripe_y + 8, TEXTO_SUAVE, "pequena")
        if total_w > visivel:
            self._txt("< arraste >", LARGURA_CANVAS - 70, stripe_y + 8, BORDA_CLARA, "pequena")

        y       = stripe_y + 28
        x_base  = 16 - scroll_x if total_w > visivel else (LARGURA_CANVAS - total_w) // 2

        clip = pygame.Rect(16, stripe_y + 24, visivel, badge_h + 4)
        self.tela.set_clip(clip)

        for i, palavra in enumerate(automato.fila):
            bx = x_base + i * badge_w + 4
            bw = badge_w - 8

            if i < len(automato.historico):
                aceita = automato.historico[i][1] == "ACEITA"
                fundo  = (16, 44, 24) if aceita else (48, 18, 24)
                borda  = VERDE        if aceita else VERMELHO
                cor_w  = VERDE_CLARO  if aceita else VERMELHO_CLARO
                cor_r  = VERDE        if aceita else VERMELHO
                label  = "ACEITA"     if aceita else "REJEITA"
            elif i == automato.indice_fila:
                pulso = (pygame.time.get_ticks() // 500) % 2
                fundo = (24, 38, 88) if pulso else (20, 32, 76)
                borda = AMBAR
                cor_w = AMBAR_CLARO
                cor_r = AMBAR
                label = "..."
            else:
                fundo = (10, 16, 40)
                borda = BORDA
                cor_w = TEXTO_SUAVE
                cor_r = TEXTO_SUAVE
                label = ""

            pygame.draw.rect(self.tela, fundo, (bx, y, bw, badge_h), border_radius=8)
            pygame.draw.rect(self.tela, borda, (bx, y, bw, badge_h), 1, border_radius=8)
            pygame.draw.rect(self.tela, borda, (bx + 1, y + 1, bw - 2, 3), border_radius=8)
            self._txt(palavra, bx + bw // 2, y + 14, cor_w, "pequena", centro=True)
            if label:
                self._txt(label, bx + bw // 2, y + 30, cor_r, "pequena", centro=True)

        self.tela.set_clip(None)

        # scrollbar
        if total_w > visivel:
            bar_y     = stripe_y + 78
            bar_total = visivel
            bar_w     = max(32, int(bar_total * visivel / total_w))
            max_s     = total_w - visivel
            bar_x     = 16 + int((bar_total - bar_w) * scroll_x / max(1, max_s))
            pygame.draw.rect(self.tela, (20, 30, 64), (16, bar_y, bar_total, 4), border_radius=2)
            pygame.draw.rect(self.tela, BORDA_CLARA,  (bar_x, bar_y, bar_w, 4), border_radius=2)

    def _dots(self):
        for x in range(24, 736, 32):
            for y in range(86, 700, 32):
                major = (x - 24) % 96 == 0 and (y - 86) % 96 == 0
                r   = 2 if major else 1
                cor = CANVAS_LINHA if major else (18, 28, 68)
                pygame.draw.circle(self.tela, cor, (x, y), r)

    def _header_canvas(self):
        cab = pygame.Rect(16, 8, LARGURA_CANVAS - 32, 66)
        self._card(cab, (10, 17, 46), BORDA, 14)

        cx, cy = 42, 41
        pygame.draw.circle(self.tela, (18, 48, 20), (cx, cy), 9)
        pygame.draw.circle(self.tela, VERDE, (cx, cy), 5)
        pygame.draw.circle(self.tela, (200, 240, 170), (cx - 2, cy - 2), 2)

        self._txt("Autômatos — Trabalho 1", cx + 18, 18, TEXTO, "normal")

        fonte = self.fontes["pequena"]
        bx, by = cx + 18, 48
        esq  = "L = {w "
        dir_ = " {a, b}* | aaa \xe9 subpalavra de w}"
        lw = fonte.size(esq)[0]
        sw = 11  # largura reservada para o simbolo desenhado
        self._txt(esq,  bx,          by, TEXTO_SUAVE, "pequena")
        self._pertence(bx + lw,      by + 2, TEXTO_SUAVE)
        self._txt(dir_, bx + lw + sw, by, TEXTO_SUAVE, "pequena")

    def _transicao_ativa(self, automato, origem, simbolo):
        a = automato.animacao
        return bool(a and a["origem"] == origem and (origem == "q3" or a["simbolo"] == simbolo))

    def _transicao(self, automato, origem, simbolo):
        pontos = caminho_transicao(origem, simbolo)
        ativa  = self._transicao_ativa(automato, origem, simbolo)
        cor    = AMBAR if ativa else BORDA_CLARA
        if ativa:
            self._linha(pontos, (40, 30, 0), 17)
            self._linha(pontos, (100, 70, 0), 10)
        else:
            self._linha(pontos, (8, 14, 38), 7)
        self._linha(pontos, cor, 5 if ativa else 3)
        pygame.draw.polygon(self.tela, cor,
                            pontos_cabeca_seta(pontos[-1], pontos[-2], 12))
        if origem == "q3":
            rotulo_cor = CIANO
        elif simbolo == "a":
            rotulo_cor = VERDE
        else:
            rotulo_cor = LARANJA
        self._rotulo(simbolo if origem != "q3" else "a,b",
                     posicao_rotulo(origem, simbolo), rotulo_cor)

    def _fase(self, automato, nome):
        a = automato.animacao
        if not a:
            return 0
        t     = (pygame.time.get_ticks() - a["inicio"]) / DURACAO_TRANSICAO
        pulso = (math.sin(pygame.time.get_ticks() / 95) + 1) / 2
        if nome == a["origem"] and t < 0.28:
            return pulso
        if nome == a["destino"] and t > 0.72:
            return pulso
        return 0

    def _estado(self, automato, nome):
        x, y      = ESTADOS[nome]
        final     = nome == "q3"
        atual     = nome == automato.estado_atual
        aceito    = automato.resultado == "ACEITA" and final
        rejeitado = automato.resultado == "REJEITA" and atual
        pulso     = self._fase(automato, nome)

        sombra = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(sombra, (0, 0, 0, 80), (75, 82), 50)
        self.tela.blit(sombra, (x - 75, y - 75))

        if pulso:
            raio_ext = 56 + round(8 * pulso)
            anel_cor = AMBAR_CLARO if atual and not aceito and not rejeitado else CIANO_CLARO
            anel_int = AMBAR       if atual and not aceito and not rejeitado else CIANO
            pygame.draw.circle(self.tela, anel_cor, (x, y), raio_ext, 2)
            pygame.draw.circle(self.tela, anel_int, (x, y), raio_ext - 6, 3)

        fundo, borda = FUNDO, BORDA
        if nome in automato.visitados:
            fundo, borda = (16, 26, 62), BORDA_CLARA
        if atual:
            fundo = misturar((22, 35, 80), (50, 35, 0), pulso)
            borda = AMBAR
        if aceito:
            fundo, borda = (16, 44, 24), VERDE
        elif rejeitado:
            fundo, borda = (48, 18, 24), VERMELHO

        pygame.draw.circle(self.tela, fundo, (x, y), 46)
        pygame.draw.circle(self.tela, borda, (x, y), 46, 4)
        if final:
            pygame.draw.circle(self.tela, VERDE if aceito else borda, (x, y), 36, 3)
        self._txt(nome, x, y - 2, TEXTO, "estado", centro=True)
        if atual:
            self._chip("atual",
                       pygame.Rect(x - 30, y + 56, 60, 22),
                       (20, 35, 80), AMBAR, "pequena")

    def _particula(self, automato):
        if not automato.animacao:
            return
        t = (pygame.time.get_ticks() - automato.animacao["inicio"]) / DURACAO_TRANSICAO
        if not 0.24 <= t <= 0.84:
            return
        pontos = caminho_transicao(automato.animacao["origem"], automato.animacao["simbolo"])
        px, py = ponto_no_caminho(pontos, (t - 0.24) / 0.60)
        c = (round(px), round(py))
        pygame.draw.circle(self.tela, AMBAR_CLARO, c, 13)
        pygame.draw.circle(self.tela, AMBAR, c, 8)
        pygame.draw.circle(self.tela, (255, 255, 255), (c[0] - 3, c[1] - 3), 3)
