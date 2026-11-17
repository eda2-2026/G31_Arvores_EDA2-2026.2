"""Árvore AVL - implementação da Ana.

Regra da AVL: em todo nó, a altura da subárvore esquerda e a da direita
diferem no máximo em 1. Esse é o fator de balanceamento:

    fator = altura(esq) - altura(dir)        (tem que ficar entre -1 e 1)

Com isso a altura fica no máximo ~1,44·log2(n+2), um pouco mais justa que a
da rubro-negra (2·log2(n+1)). Em troca, costuma girar um pouco mais.

Cada nó guarda:
  - altura  = 1 + max(altura(esq), altura(dir))   (nó vazio tem altura 0)
  - tamanho = 1 + tamanho(esq) + tamanho(dir)     (usado por posicao/k_esimo)

Inserção e remoção são recursivas: descem até o lugar certo e, na volta da
recursão, cada nó do caminho passa por `_balancear`, que recalcula altura e
tamanho e, se o fator saiu de [-1, 1], aplica um dos 4 casos:

  fator > 1  e fator(esq) >= 0  -> rotação à direita                   (LL)
  fator > 1  e fator(esq) < 0   -> esquerda no filho, depois direita   (LR)
  fator < -1 e fator(dir) <= 0  -> rotação à esquerda                  (RR)
  fator < -1 e fator(dir) > 0   -> direita no filho, depois esquerda   (RL)

Na inserção, uma correção basta: a rotação devolve a subárvore à altura que
ela tinha antes. E assim que uma subárvore termina com a mesma altura (com
ou sem rotação), nada acima dela pode ter desbalanceado: daí pra cima só o
tamanho aumenta, sem recalcular nem girar nada.

Na remoção, a rotação pode baixar a altura da subárvore e desbalancear um
ancestral, então pode haver uma correção em cada nível até a raiz.

A recursão não é problema aqui: com 100 mil nós a altura fica abaixo de 24.
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


def _alt(no):
    return 0 if no is None else no.altura


# o que a inserção mudou numa subárvore, avisado de filho pra pai
_NADA = 0        # chave repetida: nada mudou
_SO_TAMANHO = 1  # a altura ficou igual: daqui pra cima só o tamanho aumenta
_ALTURA = 2      # a altura aumentou: o pai precisa recalcular e talvez girar


class AVL(ArvoreBase):
    nome = "AVL"

    # ---------- utilidades ----------

    def _atualizar(self, no):
        """Recalcula altura e tamanho do nó (os filhos já têm que estar certos)
        e devolve o fator dele.

        Roda em muitos nós de cada inserção e remoção, por isso faz as contas
        direto, sem chamar _alt e _tam: em Python cada chamada de função custa
        caro, e aqui seriam 4 chamadas a mais por nó."""
        e, d = no.esq, no.dir
        if e is None:
            alt_e = tam_e = 0
        else:
            alt_e, tam_e = e.altura, e.tamanho
        if d is None:
            alt_d = tam_d = 0
        else:
            alt_d, tam_d = d.altura, d.tamanho
        no.altura = 1 + (alt_e if alt_e > alt_d else alt_d)
        no.tamanho = 1 + tam_e + tam_d
        return alt_e - alt_d

    def _fator(self, no):
        return _alt(no.esq) - _alt(no.dir)

    def _rotacionar_direita(self, y):
        """Devolve a nova raiz da subárvore.
                y               x
               / \\            / \\
              x   c    ->     a   y
             / \\                 / \\
            a   b               b   c
        """
        x = y.esq
        y.esq = x.dir
        x.dir = y
        self._atualizar(y)  # y desceu: recalcula ele primeiro, depois x
        self._atualizar(x)
        self.metricas.rotacoes += 1
        return x

    def _rotacionar_esquerda(self, x):
        """Espelho da rotação à direita."""
        y = x.dir
        x.dir = y.esq
        y.esq = x
        self._atualizar(x)
        self._atualizar(y)
        self.metricas.rotacoes += 1
        return y

    def _balancear(self, no):
        """Atualiza o nó e, se ficou desbalanceado, aplica o caso certo.
        Devolve a nova raiz da subárvore (o próprio nó, se não girou)."""
        fator = self._atualizar(no)
        if fator > 1:
            if self._fator(no.esq) < 0:                       # LR
                no.esq = self._rotacionar_esquerda(no.esq)
            return self._rotacionar_direita(no)               # LL
        if fator < -1:
            if self._fator(no.dir) > 0:                       # RL
                no.dir = self._rotacionar_direita(no.dir)
            return self._rotacionar_esquerda(no)              # RR
        return no

    # ---------- inserção ----------

    def inserir(self, chave, valor=None):
        self.raiz, mudou = self._inserir(self.raiz, chave, valor)
        return mudou != _NADA

    def _inserir(self, no, chave, valor):
        """Devolve (nova raiz da subárvore, o que mudou nela)."""
        if no is None:
            return NoAVL(chave, valor), _ALTURA
        c = self._comparar(chave, no.chave)
        if c == 0:
            return no, _NADA  # chave repetida: nada muda, nem altura nem tamanho
        if c < 0:
            no.esq, mudou = self._inserir(no.esq, chave, valor)
        else:
            no.dir, mudou = self._inserir(no.dir, chave, valor)
        if mudou == _SO_TAMANHO:
            # o filho ficou com a mesma altura, então este nó também: não tem
            # como ter desbalanceado, só ganhou um nó embaixo
            no.tamanho += 1
        elif mudou == _ALTURA:
            altura_antes = no.altura
            no = self._balancear(no)
            if no.altura == altura_antes:
                # ou o filho que cresceu era o mais baixo, ou houve rotação
                # (que devolve a subárvore à altura de antes): daqui pra cima
                # nada mais desbalanceia
                mudou = _SO_TAMANHO
        return no, mudou

    # ---------- remoção ----------

    def remover(self, chave):
        self.raiz, saiu = self._remover(self.raiz, chave)
        return None if saiu is None else saiu.valor

    def _remover(self, no, chave):
        """Devolve (nova raiz da subárvore, nó que saiu ou None se não achou)."""
        if no is None:
            return None, None
        c = self._comparar(chave, no.chave)
        if c < 0:
            no.esq, saiu = self._remover(no.esq, chave)
        elif c > 0:
            no.dir, saiu = self._remover(no.dir, chave)
        else:
            saiu = no
            # zero ou um filho: o filho (já balanceado) sobe no lugar dele
            if no.esq is None:
                return no.dir, saiu
            if no.dir is None:
                return no.esq, saiu
            # dois filhos: o sucessor (menor da direita) sai de lá e toma o
            # lugar do nó removido, herdando os dois filhos
            direita, sucessor = self._remover_menor(no.dir)
            sucessor.esq, sucessor.dir = no.esq, direita
            no = sucessor
        if saiu is None:
            return no, None  # não achou: nada mudou no caminho
        return self._balancear(no), saiu

    def _remover_menor(self, no):
        """Tira o menor nó da subárvore. Devolve (nova raiz, o nó que saiu)."""
        if no.esq is None:
            return no.dir, no
        no.esq, menor = self._remover_menor(no.esq)
        return self._balancear(no), menor
