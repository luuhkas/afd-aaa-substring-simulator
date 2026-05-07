from config import DURACAO_TRANSICAO, TRANSICOES


class AutomatoSimulator:
    def __init__(self):
        self.palavra = ""
        self.cursor = 0
        self.estado_atual = "q0"
        self.indice = 0
        self.executando = False
        self.resultado = ""
        self.visitados = {"q0"}
        self.animacao = None

    def adicionar_simbolo(self, simbolo):
        if self.executando or simbolo not in ("a", "b"):
            return
        self.palavra = self.palavra[:self.cursor] + simbolo + self.palavra[self.cursor:]
        self.cursor += 1
        self.resultado = ""

    def apagar_simbolo(self):
        if self.executando or self.cursor == 0:
            return
        self.palavra = self.palavra[:self.cursor - 1] + self.palavra[self.cursor:]
        self.cursor -= 1
        self.resultado = ""

    def deletar_simbolo(self):
        if self.executando or self.cursor >= len(self.palavra):
            return
        self.palavra = self.palavra[:self.cursor] + self.palavra[self.cursor + 1:]
        self.resultado = ""

    def mover_cursor(self, delta):
        self.cursor = max(0, min(len(self.palavra), self.cursor + delta))

    def iniciar_execucao(self, agora):
        if self.executando:
            return

        self.estado_atual = "q0"
        self.indice = 0
        self.resultado = ""
        self.visitados = {"q0"}
        self.animacao = None
        self.cursor = len(self.palavra)
        self.executando = True

        if not self.palavra:
            self.executando = False
            self.resultado = "REJEITA"

    def atualizar(self, agora):
        if not self.executando:
            return

        if self.indice >= len(self.palavra):
            self.executando = False
            self.resultado = "ACEITA" if self.estado_atual == "q3" else "REJEITA"
            return

        if self.animacao is None:
            self._iniciar_proxima_transicao(agora)
            return

        tempo = agora - self.animacao["inicio"]
        if tempo >= DURACAO_TRANSICAO:
            self.estado_atual = self.animacao["destino"]
            self.visitados.add(self.estado_atual)
            self.indice += 1
            self.animacao = None

    def _iniciar_proxima_transicao(self, agora):
        simbolo = self.palavra[self.indice]
        destino = TRANSICOES[(self.estado_atual, simbolo)]
        self.animacao = {
            "origem": self.estado_atual,
            "simbolo": simbolo,
            "destino": destino,
            "inicio": agora,
        }
