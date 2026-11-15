"""Interface comum das árvores (BST, AVL e rubro-negra).

As três árvores têm os mesmos métodos, então o resto do sistema troca de
árvore sem mudar mais nada - igual ao seletor de algoritmo do trabalho 2.

Cada nó guarda `tamanho` (quantos nós tem a subárvore dele). É isso que deixa
responder "qual a minha posição na fila?" e "quem é o k-ésimo?" em O(altura)
sem percorrer a árvore inteira. Toda árvore precisa manter esse campo certo
em inserção, remoção e rotação.

Campos de um nó: chave, valor, esq, dir, tamanho
  - AVL também tem: altura
  - rubro-negra também tem: vermelho (bool) e pai

As buscas aqui são todas iterativas (sem recursão): a BST comum vira uma
lista quando recebe chaves em ordem crescente, e recursão com 10 mil níveis
estoura a pilha do Python.
"""

from collections import deque


class Metricas:
    def __init__(self):
        self.zerar()

    def zerar(self):
        self.comparacoes = 0
        self.rotacoes = 0
        self.recoloracoes = 0

    def como_dict(self):
        return {"comparacoes": self.comparacoes, "rotacoes": self.rotacoes,
                "recoloracoes": self.recoloracoes}


class ArvoreBase:
    nome = "Árvore"
    NIL = None  # a rubro-negra troca por um nó sentinela

    def __init__(self):
        self.raiz = self.NIL
        self.metricas = Metricas()

    # ---- o que cada árvore implementa ----

    def inserir(self, chave, valor=None):
        """Insere e devolve True; se a chave já existe, não mexe e devolve False."""
        raise NotImplementedError

    def remover(self, chave):
        """Remove e devolve o valor; se a chave não existe, devolve None."""
        raise NotImplementedError

    # ---- utilidades ----

    def _tam(self, no):
        return 0 if no is self.NIL else no.tamanho

    def _atualizar_tamanho(self, no):
        no.tamanho = 1 + self._tam(no.esq) + self._tam(no.dir)

    def _comparar(self, a, b):
        self.metricas.comparacoes += 1
        if a < b:
            return -1
        return 1 if a > b else 0

    def __len__(self):
        return self._tam(self.raiz)

    def __contains__(self, chave):
        return self._no(chave) is not self.NIL

    # ---- consultas (iguais para todas as árvores) ----

    def _no(self, chave):
        no = self.raiz
        while no is not self.NIL:
            c = self._comparar(chave, no.chave)
            if c == 0:
                return no
            no = no.esq if c < 0 else no.dir
        return self.NIL

    def buscar(self, chave):
        no = self._no(chave)
        return None if no is self.NIL else no.valor

    def posicao(self, chave):
        """Posição (1, 2, 3...) da chave em ordem crescente, ou None.
        Descendo pra direita, todo mundo da esquerda + o próprio nó vem antes."""
        no = self.raiz
        antes = 0
        while no is not self.NIL:
            c = self._comparar(chave, no.chave)
            if c < 0:
                no = no.esq
            elif c > 0:
                antes += self._tam(no.esq) + 1
                no = no.dir
            else:
                return antes + self._tam(no.esq) + 1
        return None

    def k_esimo(self, k):
        """(chave, valor) do k-ésimo menor (k começa em 1), ou None."""
        if not 1 <= k <= len(self):
            return None
        no = self.raiz
        while True:
            esquerda = self._tam(no.esq)
            if k <= esquerda:
                no = no.esq
            elif k == esquerda + 1:
                return no.chave, no.valor
            else:
                k -= esquerda + 1
                no = no.dir

    def menor(self):
        return self.k_esimo(1)

    def em_ordem(self):
        """Gera (chave, valor) em ordem crescente."""
        pilha = []
        no = self.raiz
        while pilha or no is not self.NIL:
            while no is not self.NIL:
                pilha.append(no)
                no = no.esq
            no = pilha.pop()
            yield no.chave, no.valor
            no = no.dir

    def intervalo(self, inicio, fim):
        """Todos os (chave, valor) com inicio <= chave <= fim, em ordem. Só desce
        nos galhos que podem ter chave dentro do intervalo."""
        saida = []
        pilha = []
        no = self.raiz
        while pilha or no is not self.NIL:
            while no is not self.NIL:
                pilha.append(no)
                no = no.esq if self._comparar(inicio, no.chave) < 0 else self.NIL
            no = pilha.pop()
            if self._comparar(no.chave, fim) > 0:
                break
            if self._comparar(no.chave, inicio) >= 0:
                saida.append((no.chave, no.valor))
            no = no.dir
        return saida

    def altura(self):
        """Quantidade de níveis (árvore vazia = 0, só a raiz = 1)."""
        if self.raiz is self.NIL:
            return 0
        niveis = 0
        fila = deque([self.raiz])
        while fila:
            niveis += 1
            for _ in range(len(fila)):
                no = fila.popleft()
                if no.esq is not self.NIL:
                    fila.append(no.esq)
                if no.dir is not self.NIL:
                    fila.append(no.dir)
        return niveis
