import math

from config import ESTADOS, TRANSICOES


def misturar(cor_a, cor_b, t):
    t = max(0, min(1, t))
    return tuple(round(cor_a[i] + (cor_b[i] - cor_a[i]) * t) for i in range(3))


def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def pontos_bezier(p0, p1, p2, p3, passos=42):
    pontos = []
    for i in range(passos + 1):
        t = i / passos
        inv = 1 - t
        x = inv ** 3 * p0[0] + 3 * inv ** 2 * t * p1[0] + 3 * inv * t ** 2 * p2[0] + t ** 3 * p3[0]
        y = inv ** 3 * p0[1] + 3 * inv ** 2 * t * p1[1] + 3 * inv * t ** 2 * p2[1] + t ** 3 * p3[1]
        pontos.append((round(x), round(y)))
    return pontos


def ponto_no_caminho(pontos, t):
    if len(pontos) == 1:
        return pontos[0]

    segmentos = [(inicio, fim, math.dist(inicio, fim)) for inicio, fim in zip(pontos, pontos[1:])]
    total = sum(tamanho for _, _, tamanho in segmentos)
    alvo = ease(t) * total
    percorrido = 0
    for inicio, fim, tamanho in segmentos:
        if percorrido + tamanho >= alvo:
            local = (alvo - percorrido) / max(1, tamanho)
            return (
                inicio[0] + (fim[0] - inicio[0]) * local,
                inicio[1] + (fim[1] - inicio[1]) * local,
            )
        percorrido += tamanho

    return pontos[-1]


def caminho_transicao(origem, simbolo):
    destino = TRANSICOES[(origem, simbolo)]
    ox, oy = ESTADOS[origem]
    dx, dy = ESTADOS[destino]

    if origem == destino:
        return pontos_bezier(
            (ox - 24, oy - 46),
            (ox - 38, oy - 118),
            (ox + 50, oy - 118),
            (ox + 34, oy - 46),
            34,
        )
    if simbolo == "b":
        if origem == "q1":
            return pontos_bezier(
                (ox - 28, oy + 38),
                (ox - 24, oy + 110),
                (dx + 42, dy + 110),
                (dx + 30, dy + 48),
                42,
            )

        return pontos_bezier(
            (ox - 28, oy + 40),
            (ox - 24, oy + 195),
            (dx + 28, dy + 195),
            (dx + 22, dy + 50),
            56,
        )

    return pontos_bezier(
        (ox + 48, oy),
        (ox + 84, oy + 10),
        (dx - 84, dy + 10),
        (dx - 48, dy),
        20,
    )


def posicao_rotulo(origem, simbolo):
    if origem == "q0" and simbolo == "b":
        return (ESTADOS[origem][0] - 30, ESTADOS[origem][1] - 140)
    if origem == "q3":
        return (ESTADOS[origem][0] - 8, ESTADOS[origem][1] - 140)
    if simbolo == "b":
        return ((ESTADOS[origem][0] + ESTADOS["q0"][0]) // 2, 490 if origem == "q1" else 575)

    ox, oy = ESTADOS[origem]
    dx, dy = ESTADOS[TRANSICOES[(origem, simbolo)]]
    return ((ox + dx) // 2, oy - 34)


def pontos_cabeca_seta(fim, anterior, tamanho=13):
    angulo = math.atan2(fim[1] - anterior[1], fim[0] - anterior[0])
    abertura = 0.48
    ponta_1 = (
        fim[0] - tamanho * math.cos(angulo - abertura),
        fim[1] - tamanho * math.sin(angulo - abertura),
    )
    ponta_2 = (
        fim[0] - tamanho * math.cos(angulo + abertura),
        fim[1] - tamanho * math.sin(angulo + abertura),
    )
    return [fim, ponta_1, ponta_2]
