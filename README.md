# AFD - Simulador Visual da Linguagem com `aaa`

Este projeto implementa um simulador visual de um Autômato Finito Determinístico
(AFD) para reconhecer palavras sobre o alfabeto `{a, b}` que contêm a substring
`aaa`.

A linguagem reconhecida é:

```text
L = { w em {a,b}* | w contem "aaa" }
```

Ou seja, uma palavra é aceita quando, em algum ponto da leitura, aparecem três
letras `a` consecutivas. Depois que o autômato encontra `aaa`, ele permanece no
estado final e qualquer continuação da palavra continua sendo aceita.

## Objetivo

O simulador foi desenvolvido para o Trabalho 1 da disciplina de Autômatos. A
ideia é mostrar, de forma interativa, como a definição formal de um AFD se
transforma em execução passo a passo:

- entrada da palavra;
- transições entre estados;
- destaque visual do estado atual;
- animação do símbolo sendo processado;
- resultado final de aceitação ou rejeição;
- leitura automática de várias sentenças a partir de arquivos `.txt`.

## Linguagem Reconhecida

Exemplos de palavras aceitas:

```text
aaa
aaab
baaab
baabaaab
aaaaaa
```

Exemplos de palavras rejeitadas:

```text
a
aa
abab
aabaa
bb
```

## Definição Formal do AFD

O autômato é definido pela 5-upla:

```text
M = (Q, Sigma, delta, q0, F)
```

Componentes:

```text
Q      = { q0, q1, q2, q3 }
Sigma  = { a, b }
q0     = q0
F      = { q3 }
```

Função de transição:

| Estado | `a` | `b` |
|:------:|:---:|:---:|
| `q0` | `q1` | `q0` |
| `q1` | `q2` | `q0` |
| `q2` | `q3` | `q0` |
| `q3` | `q3` | `q3` |

Semântica dos estados:

- `q0`: ainda não há sequência relevante de `a`s consecutivos.
- `q1`: foi lido exatamente um `a` consecutivo.
- `q2`: foram lidos exatamente dois `a`s consecutivos.
- `q3`: a substring `aaa` já foi encontrada; este é o estado final.

## Funcionalidades

- Simulação manual digitando uma palavra com `a` e `b`.
- Execução animada, símbolo por símbolo.
- Campo de entrada com cursor, `BACKSPACE`, `DELETE`, setas, `HOME` e `END`.
- Seleção de arquivos `.txt` do diretório do projeto.
- Modo automático para processar uma fila de sentenças.
- Histórico visual das palavras já processadas.
- Tela de conclusão com resumo de aceitas e rejeitadas.
- Documentação complementar em Markdown e HTML.

## Como Executar

Requisito principal:

- Python 3
- Pygame

Instale o Pygame, se necessário:

```bash
python3 -m pip install pygame
```

Execute:

```bash
python3 main.py
```

## Como Usar

Modo manual:

1. Digite uma palavra usando apenas `a` e `b`.
2. Pressione `ENTER` para iniciar a simulação.
3. Aguarde o resultado `ACEITA` ou `REJEITA`.
4. Edite a palavra e execute novamente, se quiser testar outro caso.

Modo arquivo:

1. Clique em `Abrir arquivo`.
2. Escolha um arquivo `.txt` listado pelo programa.
3. Cada linha não vazia do arquivo será tratada como uma palavra.
4. O simulador executa as sentenças em sequência e mostra o histórico.

Atalhos úteis:

| Tecla | Ação |
|------|------|
| `ENTER` | Executa a palavra digitada |
| `BACKSPACE` | Apaga o símbolo antes do cursor |
| `DELETE` | Apaga o símbolo depois do cursor |
| `LEFT` / `RIGHT` | Move o cursor |
| `HOME` / `END` | Move para início/fim da palavra |
| `ESC` | Fecha o simulador |

## Arquivos de Entrada

O repositório inclui exemplos:

- `entrada.txt`
- `entrada2.txt`

Cada arquivo deve conter uma palavra por linha:

```text
aaab
baaab
baabaaab
aabaa
bb
```

Linhas vazias são ignoradas. O simulador aceita somente símbolos do alfabeto
`{a, b}`.

## Organização do Projeto

```text
main.py             Entrada do programa, eventos do Pygame e loop principal.
automato.py         Lógica do AFD, modo manual, modo arquivo e histórico.
config.py           Constantes visuais, estados e função de transição.
geometry.py         Cálculo de curvas, setas e posições das animações.
ui.py               Renderização da interface, painel, estados e resultados.
entrada.txt         Conjunto simples de palavras para teste.
entrada2.txt        Conjunto maior de palavras para teste.
DOCUMENTACAO.md     Roteiro detalhado para apresentação do trabalho.
DOCUMENTACAO.html   Versão HTML da documentação de apresentação.
```

## Documentação de Apresentação

Para uma explicação mais detalhada, incluindo divisão por apresentadores,
prova de correção, geometria da animação e ciclo de execução, consulte:

- [DOCUMENTACAO.md](DOCUMENTACAO.md)
- [DOCUMENTACAO.html](DOCUMENTACAO.html)
