from config import DURACAO_TRANSICAO, PAUSA_INICIO, PAUSA_RESULTADO, TRANSICOES


class AutomatoSimulator:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.palavra = ""
        self.cursor = 0
        self.estado_atual = "q0"
        self.indice = 0
        self.executando = False
        self.resultado = ""
        self.visitados = {"q0"}
        self.animacao = None
        self.fila = []
        self.indice_fila = -1
        self.modo_arquivo = False
        self.tempo_carregado = None
        self.tempo_resultado = None
        self.historico = []
        self.concluido = False

    def reset_manual(self):
        self._reset()

    def carregar_arquivo(self, caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            palavras = [linha.strip() for linha in f if linha.strip()]
        if not palavras:
            return
        self.fila = palavras
        self.indice_fila = 0
        self.modo_arquivo = True
        self.historico = []
        self.concluido = False
        self._carregar_palavra_atual()

    def _carregar_palavra_atual(self):
        self.palavra = self.fila[self.indice_fila]
        self.cursor = len(self.palavra)
        self.estado_atual = "q0"
        self.indice = 0
        self.resultado = ""
        self.visitados = {"q0"}
        self.animacao = None
        self.executando = False
        self.tempo_carregado = None
        self.tempo_resultado = None

    def avancar_fila(self):
        if not self.modo_arquivo or self.executando:
            return False
        if self.indice_fila + 1 >= len(self.fila):
            return False
        self.indice_fila += 1
        self._carregar_palavra_atual()
        return True

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
        if self.concluido:
            return

        if self.modo_arquivo and self.resultado and not self.executando:
            if self.tempo_resultado is None:
                self.tempo_resultado = agora
                self.historico.append((self.palavra, self.resultado))
            elif agora - self.tempo_resultado >= PAUSA_RESULTADO:
                self.tempo_resultado = None
                if not self.avancar_fila():
                    self.concluido = True
            return

        if self.modo_arquivo and not self.executando and not self.resultado:
            if self.tempo_carregado is None:
                self.tempo_carregado = agora
            elif agora - self.tempo_carregado >= PAUSA_INICIO:
                self.iniciar_execucao(agora)
            return

        if not self.executando:
            return

        if self.indice >= len(self.palavra):
            self.executando = False
            self.resultado = "ACEITA" if self.estado_atual == "q3" else "REJEITA"
            return

        if self.animacao is None:
            self._iniciar_proxima_transicao(agora)
            return

        if agora - self.animacao["inicio"] >= DURACAO_TRANSICAO:
            self.estado_atual = self.animacao["destino"]
            self.visitados.add(self.estado_atual)
            self.indice += 1
            self.animacao = None

    def _iniciar_proxima_transicao(self, agora):
        simbolo = self.palavra[self.indice]
        destino = TRANSICOES[(self.estado_atual, simbolo)]
        self.animacao = {
            "origem":  self.estado_atual,
            "simbolo": simbolo,
            "destino": destino,
            "inicio":  agora,
        }
