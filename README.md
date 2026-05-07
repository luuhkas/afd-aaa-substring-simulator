# AFD - Linguagem com `aaa`

Simulador visual de um Autômato Finito Determinístico (AFD) que reconhece palavras sobre o alfabeto `{a, b}` que contêm a substring `aaa`.

## Como executar

Instale o Pygame, se ainda não estiver instalado:

```bash
python3 -m pip install pygame
```

Execute o projeto:

```bash
python3 main.py
```

## Como usar

- Digite uma palavra usando apenas `a` e `b`.
- Use `ENTER` para executar a simulação.
- Use `BACKSPACE` para apagar.
- Use `ESC` para sair.

## Organização

```text
main.py       Entrada do programa e loop principal do Pygame.
automato.py   Lógica do AFD, leitura da palavra e estado da simulação.
config.py     Constantes visuais, dimensões, estados e transições.
geometry.py   Cálculo dos caminhos, curvas e setas do autômato.
ui.py         Interface gráfica e animações.
```

## Lógica do AFD

Estados:

- `q0`: estado inicial.
- `q1`: leu um `a` consecutivo.
- `q2`: leu dois `a` consecutivos.
- `q3`: estado final, já encontrou `aaa`.

A palavra é aceita se a execução terminar em `q3`.
