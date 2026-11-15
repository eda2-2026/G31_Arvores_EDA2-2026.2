"""Árvore rubro-negra - implementação do João (em construção)."""

from .base import ArvoreBase


class RubroNegra(ArvoreBase):
    nome = "Rubro-negra"

    def inserir(self, chave, valor=None):
        raise NotImplementedError("Rubro-negra: inserção ainda não implementada")

    def remover(self, chave):
        raise NotImplementedError("Rubro-negra: remoção ainda não implementada")
