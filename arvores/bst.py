"""Árvore binária de busca comum, sem balanceamento.

Existe pra perder no benchmark: com chaves em ordem crescente (como as
matrículas de um semestre novo), cada nó novo entra sempre à direita do
anterior e a árvore vira uma lista - altura n em vez de log n.
"""

from .base import ArvoreBase


class NoBST:
    __slots__ = ("chave", "valor", "esq", "dir", "tamanho")

    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.esq = None
        self.dir = None
        self.tamanho = 1


class BST(ArvoreBase):
    nome = "BST comum"

    def inserir(self, chave, valor=None):
        if self.raiz is None:
            self.raiz = NoBST(chave, valor)
            return True
        caminho = []
        no = self.raiz
        while True:
            c = self._comparar(chave, no.chave)
            if c == 0:
                return False  # chave repetida: nada muda, nem os tamanhos
            caminho.append(no)
            proximo = no.esq if c < 0 else no.dir
            if proximo is None:
                if c < 0:
                    no.esq = NoBST(chave, valor)
                else:
                    no.dir = NoBST(chave, valor)
                break
            no = proximo
        for ancestral in caminho:
            ancestral.tamanho += 1
        return True

    def remover(self, chave):
        caminho = []
        no = self.raiz
        while no is not None:
            c = self._comparar(chave, no.chave)
            if c == 0:
                break
            caminho.append(no)
            no = no.esq if c < 0 else no.dir
        if no is None:
            return None
        valor = no.valor

        alvo = no
        if no.esq is not None and no.dir is not None:
            # dois filhos: o sucessor (menor da direita) toma o lugar dele,
            # e quem sai fisicamente da árvore é o nó do sucessor
            caminho.append(no)
            alvo = no.dir
            while alvo.esq is not None:
                caminho.append(alvo)
                alvo = alvo.esq
            no.chave, no.valor = alvo.chave, alvo.valor

        filho = alvo.esq if alvo.esq is not None else alvo.dir
        pai = caminho[-1] if caminho else None
        if pai is None:
            self.raiz = filho
        elif pai.esq is alvo:
            pai.esq = filho
        else:
            pai.dir = filho
        for ancestral in caminho:
            ancestral.tamanho -= 1
        return valor
