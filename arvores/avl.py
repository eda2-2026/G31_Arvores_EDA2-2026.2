"""Árvore AVL - implementação da Ana.

Regra da AVL: em todo nó, a altura da subárvore esquerda e a da direita
diferem no máximo em 1 (fator de balanceamento entre -1 e 1). Quando uma
inserção ou remoção quebra isso, uma ou duas rotações consertam.

O que precisa ser feito (os testes em tests/test_arvores.py conferem tudo
depois de cada operação - rode `py -m unittest` na raiz do projeto):

  inserir(chave, valor) -> True, ou False se a chave já existe (sem mudar nada)
  remover(chave)        -> o valor removido, ou None se não existe

Em todo nó que mudar (inclusive nos que giram numa rotação), manter certos:
  - altura   = 1 + max(altura(esq), altura(dir))   (nó vazio tem altura 0)
  - tamanho  = 1 + tamanho(esq) + tamanho(dir)     (use self._atualizar_tamanho)

Contar nas métricas: self.metricas.rotacoes += 1 a cada rotação simples
(uma rotação dupla conta 2). Para comparar chaves use self._comparar(a, b),
que devolve -1, 0 ou 1 e já conta a comparação.

Os 4 casos, olhando o fator = altura(esq) - altura(dir) do nó desbalanceado:
  fator > 1  e fator(esq) >= 0  -> rotação à direita            (LL)
  fator > 1  e fator(esq) < 0   -> esquerda no filho, depois direita (LR)
  fator < -1 e fator(dir) <= 0  -> rotação à esquerda           (RR)
  fator < -1 e fator(dir) > 0   -> direita no filho, depois esquerda (RL)

Pode ser recursivo: a altura da AVL fica em torno de 1,44·log2(n), então
nunca passa de uns 30 níveis.

buscar, posicao, k_esimo, intervalo, altura e em_ordem já vêm prontos da
ArvoreBase - não precisa mexer.
"""

from .base import ArvoreBase


class NoAVL:
    __slots__ = ("chave", "valor", "esq", "dir", "tamanho", "altura")

    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.esq = None
        self.dir = None
        self.tamanho = 1
        self.altura = 1


class AVL(ArvoreBase):
    nome = "AVL"

    def inserir(self, chave, valor=None):
        raise NotImplementedError("AVL: inserção ainda não implementada")

    def remover(self, chave):
        raise NotImplementedError("AVL: remoção ainda não implementada")
