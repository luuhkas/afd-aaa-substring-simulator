# AFD — Simulador Visual · Documentação de Apresentação

> Trabalho 1 — Autômatos · 4 apresentadores

---

## Pessoa 1 — Teoria e Definição Formal

### 1.1 Linguagem Reconhecida

> L = { w ∈ {a,b}* | w contém a substring "aaa" }

| Palavra | Resultado | Motivo |
|---------|-----------|--------|
| `aaab` | **ACEITA** | contém "aaa" |
| `baaab` | **ACEITA** | contém "aaa" |
| `baabaaab` | **ACEITA** | contém "aaa" |
| `aabaa` | **REJEITA** | máximo 2 'a' consecutivos |
| `bb` | **REJEITA** | nenhum 'a' |

### 1.2 Definição Formal — 5-upla

> M = (Q, Σ, δ, q₀, F)

| Componente | Valor |
|-----------|-------|
| Q (estados) | { q0, q1, q2, q3 } |
| Σ (alfabeto) | { a, b } |
| δ (função de transição) | tabela abaixo |
| q₀ (estado inicial) | q0 |
| F (estados finais) | { q3 } |

### 1.3 Função de Transição δ

| Estado | a | b |
|:------:|:-:|:-:|
| q0 | q1 | q0 |
| q1 | q2 | q0 |
| q2 | **q3** | q0 |
| q3 | q3 | q3 |

### 1.4 Semântica dos Estados

| Estado | Invariante |
|--------|-----------|
| q0 | nenhum 'a' consecutivo acumulado |
| q1 | leu exatamente 1 'a' consecutivo |
| q2 | leu exatamente 2 'a' consecutivos |
| q3 ★ | encontrou "aaa" — estado armadilha, toda extensão é aceita |

### 1.5 Diagrama de Transições

```
         b              b              b
    ┌──────┐       ┌──────┐       ┌──────┐
    ↓      │       ↓      │       ↓      │
→  [q0] ──a──→ [q1] ──a──→ [q2] ──a──→ ((q3))
    ↑      │    │           │               │ a,b
    └──────┘    └───b───────┘               └──┘
```

### 1.6 Prova de Correção

**Teorema:** M aceita w ↔ w contém "aaa".

- **(→)** Se w contém "aaa", δ percorre q0→q1→q2→q3 no ponto da ocorrência. q3 é armadilha: qualquer sufixo mantém o estado. Logo w é aceita.
- **(←)** Se M aceita w, o estado final é q3. O único caminho a q3 é via (q2,a)→q3, que exige q1→q2 antes, portanto q0→q1→q2→q3 — três 'a' consecutivos ocorreram.

### 1.7 Complexidade e Minimalidade

| Métrica | Valor |
|---------|-------|
| Estados | 4 |
| Transições | 8 |
| Alfabeto | 2 símbolos |
| Tempo de reconhecimento | O(n), n = \|w\| |
| Espaço | O(1) — estados fixos |

O AFD é **minimal**: q0, q1, q2 e q3 são todos par-a-par distinguíveis. Nenhum estado pode ser fundido.

---

## Pessoa 2 — Núcleo do AFD (`config.py` + `automato.py`)

### 2.1 `config.py` — Estruturas de Dados

Toda a definição matemática do AFD vive aqui como estruturas Python:

```python
TRANSICOES = {
    ("q0", "a"): "q1",  ("q0", "b"): "q0",
    ("q1", "a"): "q2",  ("q1", "b"): "q0",
    ("q2", "a"): "q3",  ("q2", "b"): "q0",
    ("q3", "a"): "q3",  ("q3", "b"): "q3",
}
```

A função δ é um dicionário `(estado, símbolo) → estado`. Consulta em **O(1)**.

Constantes de temporização que controlam o ritmo da simulação:

```python
DURACAO_TRANSICAO = 1050  # ms por passo animado
PAUSA_INICIO      = 400   # ms antes de iniciar sentença em modo arquivo
PAUSA_RESULTADO   = 1100  # ms exibindo resultado antes de avançar
BADGE_REGISTRO_W  = 120   # largura dos badges do histórico (compartilhada com ui.py)
```

### 2.2 `automato.py` — Classe `AutomatoSimulator`

**Atributos de estado manual:**

| Atributo | Descrição |
|----------|-----------|
| `palavra` | String digitada |
| `cursor` | Posição do cursor de edição |
| `estado_atual` | Estado corrente do AFD |
| `indice` | Posição do símbolo sendo processado |
| `executando` | Flag: simulação em andamento |
| `resultado` | `"ACEITA"` \| `"REJEITA"` \| `""` |
| `visitados` | Estados já visitados (highlight visual) |
| `animacao` | Metadados da transição em curso |

**Atributos de modo arquivo:**

| Atributo | Descrição |
|----------|-----------|
| `fila` | Lista de palavras lidas do arquivo |
| `indice_fila` | Índice da sentença atual |
| `modo_arquivo` | Flag: lendo do arquivo |
| `historico` | Lista de `(palavra, resultado)` processados |
| `concluido` | True quando todas as sentenças foram processadas |
| `tempo_carregado` | Timestamp para a pausa de início |
| `tempo_resultado` | Timestamp para a pausa após resultado |

**Padrão de reset:** `__init__` e `reset_manual` chamam o mesmo `_reset()` privado — sem duplicação de código.

### 2.3 Ciclo de Execução — Modo Manual

```
ENTER pressionado
    ↓
iniciar_execucao(agora)
  estado_atual = "q0", indice = 0, executando = True
    ↓
Loop 60 FPS → atualizar(agora):
  ┌─ sem animação → _iniciar_proxima_transicao()
  │     simbolo = palavra[indice]
  │     destino = TRANSICOES[(estado_atual, simbolo)]
  │     animacao = { origem, simbolo, destino, inicio }
  └─ animação em curso → aguarda 1050ms
        ↓ tempo esgotado
        estado_atual = destino
        visitados.add(estado_atual)
        indice += 1, animacao = None
    ↓
indice == len(palavra)
  → resultado = "ACEITA" se estado_atual == "q3" senão "REJEITA"
```

### 2.4 Ciclo de Execução — Modo Arquivo (Auto-play)

```
carregar_arquivo(caminho)
  lê linhas → fila = ["aaab", "baaab", ...]
  indice_fila = 0 → _carregar_palavra_atual()
    ↓
atualizar(agora) a cada frame:

  [AGUARDANDO INÍCIO]
  tempo_carregado == None → registra timestamp
  elapsed >= 400ms → iniciar_execucao(agora)
    ↓
  [EXECUTANDO] — mesmo ciclo do modo manual
    ↓
  [RESULTADO EXIBIDO]
  tempo_resultado == None → registra timestamp
                          → historico.append((palavra, resultado))
  elapsed >= 1100ms → avancar_fila()
    ├─ tem próxima → _carregar_palavra_atual() → repete
    └─ última sentença → concluido = True → para
```

---

## Pessoa 3 — Geometria e Animação (`geometry.py`)

### 3.1 Responsabilidade do Módulo

`geometry.py` calcula **onde** e **como** os elementos visuais se movem. Não renderiza nada — apenas devolve pontos e cores para `ui.py` usar.

### 3.2 Curva de Bézier Cúbica

Cada aresta do diagrama é uma curva definida por 4 pontos de controle:

```
B(t) = (1-t)³P₀ + 3(1-t)²tP₁ + 3(1-t)t²P₂ + t³P₃,  t ∈ [0,1]
```

`caminho_transicao(origem, simbolo)` seleciona automaticamente os pontos de controle P1 e P2 por tipo de transição:

| Tipo | Curvatura |
|------|-----------|
| Transições `a` (avançam) | Arco suave para frente |
| Transição `b` de q1 | Arco médio abaixo retornando a q0 |
| Transição `b` de q2 | Arco largo abaixo retornando a q0 |
| q0→q0 e q3→q3 | Loop sobre o próprio estado |

### 3.3 Função de Easing (smoothstep)

```
ease(t) = t² · (3 − 2t)
```

Aplicada sobre o parâmetro t antes de localizar o ponto na curva. Resultado: o token **parte devagar, acelera no meio e desacelera no fim** — movimento natural ao olho humano.

### 3.4 Localização do Token na Curva

`ponto_no_caminho(pontos, t)` divide a curva em segmentos, calcula o comprimento total e percorre até a fração `ease(t)`:

```python
alvo = ease(t) * comprimento_total
# percorre segmentos até encontrar o segmento alvo
# interpola linearmente dentro do segmento
```

### 3.5 Cabeça de Seta

`pontos_cabeca_seta(fim, anterior, tamanho=13)` usa trigonometria para calcular os dois vértices laterais da ponta da seta:

```
angulo = atan2(fim.y - anterior.y, fim.x - anterior.x)
ponta_1 = fim - tamanho · (cos(angulo - 0.48), sin(angulo - 0.48))
ponta_2 = fim - tamanho · (cos(angulo + 0.48), sin(angulo + 0.48))
```

### 3.6 Interpolação Linear de Cores

```
misturar(cor_a, cor_b, t) = cor_a + (cor_b − cor_a) · t
```

Usada para animar o fundo dos estados durante a transição: o estado de origem e o de destino pulsam suavemente enquanto a animação ocorre.

---

## Pessoa 4 — Arquitetura e Loop Principal (`main.py`)

### 4.1 Visão Geral da Arquitetura

```
main.py ──── gerencia estado da aplicação e loop de eventos
   │
   ├── automato.py ── lógica pura do AFD (independente de UI)
   ├── config.py   ── constantes e estruturas de dados
   ├── geometry.py ── algoritmos geométricos (sem renderização)
   └── ui.py       ── renderização (recebe dados, não decide lógica)
```

**Princípio:** `automato.py` não conhece Pygame; `geometry.py` não conhece o autômato; `main.py` coordena tudo.

### 4.2 Estado da Aplicação em `main.py`

```python
automato = AutomatoSimulator()   # estado do AFD
focado   = True                  # campo de texto com foco
seletor  = {                     # overlay de seleção de arquivo
    "aberto": False,
    "arquivos": [],
    "hover": -1,
}
registro = {                     # scroll do histórico visual
    "scroll_x": 0,
    "drag": False,
    "drag_start_x": 0,
    "drag_scroll_start": 0,
}
```

### 4.3 Loop Principal

```python
while True:
    focado = processar_eventos(automato, focado, seletor, registro)
    automato.atualizar(pygame.time.get_ticks())
    interface.desenhar(automato, focado, seletor, registro["scroll_x"])
    pygame.display.flip()
    clock.tick(60)  # 60 FPS
```

Cada frame: captura eventos → avança estado → renderiza → exibe.

### 4.4 Hierarquia de Prioridade de Eventos

```
processar_eventos():
  1. QUIT → encerra
  2. automato.concluido → apenas botões da tela de conclusão
  3. seletor.aberto    → hover, clique em linha, ESC
  4. drag no registro  → MOUSEBUTTONUP, MOUSEMOTION
  5. modo normal       → clique no botão arquivo / campo de texto
  6. KEYDOWN           → ESC, ENTER, edição de texto
```

Cada camada ignora os eventos que não lhe pertencem usando `continue`.

### 4.5 Modo Manual vs Modo Arquivo

```
MODO MANUAL                    MODO ARQUIVO
───────────────────────────    ────────────────────────────────
Usuário digita a/b             Lê arquivo .txt (1 palavra/linha)
ENTER → iniciar_execucao()     Auto-play: pausa 400ms → executa
Resultado exibido              Resultado + 1100ms → próxima
Loop livre                     Após última: concluido = True
                               Tela de conclusão com resumo
```

### 4.6 Seletor de Arquivo

Ao clicar "Abrir arquivo":

```python
seletor["arquivos"] = sorted(*.txt no diretório do script)
seletor["aberto"]   = True
```

A `ui.py` renderiza o overlay; `main.py` detecta o clique via `seletor_row_at(seletor, mx, my)` que compara a posição do mouse com os rects de cada linha calculados geometricamente.

### 4.7 Scroll do Registro

```python
_clamp_scroll(automato, registro):
    visivel    = LARGURA_CANVAS - 32          # 716 px
    total      = len(fila) * BADGE_REGISTRO_W # n × 120 px
    max_scroll = max(0, total - visivel)
    scroll_x   = clamp(scroll_x, 0, max_scroll)
```

- Se `total <= visivel`: badges centralizados, sem scroll.
- Se `total > visivel`: drag horizontal ativo, scrollbar exibida.

### 4.8 Fluxo Completo End-to-End

```
Inicialização
    ↓
[MODO MANUAL]
  Digita → ENTER → animação passo a passo → resultado
    ↓
  Clica "Abrir arquivo"
    ↓
[SELETOR]
  Lista .txt do diretório → clica arquivo
    ↓
[MODO ARQUIVO — AUTO-PLAY]
  Para cada sentença:
    pausa 400ms → executa → anima → resultado → pausa 1100ms
    badge no registro: âmbar (atual) → verde/vermelho (processado)
    ↓
  Última sentença concluída
    ↓
[TELA DE CONCLUSÃO]
  Resumo: N aceitas / M rejeitadas
  [ Reiniciar simulador ]  →  volta ao modo manual
  [ Fechar simulador    ]  →  sys.exit()
```
