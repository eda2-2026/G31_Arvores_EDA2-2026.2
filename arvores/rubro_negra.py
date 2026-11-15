"""Árvore rubro-negra - implementação do João.

As 5 regras (se todas valem, a altura fica no máximo 2·log2(n+1)):
  1. todo nó é vermelho ou preto;
  2. a raiz é preta;
  3. as folhas (NIL) são pretas;
  4. nó vermelho não tem filho vermelho;
  5. todo caminho de um nó até as folhas abaixo dele passa pela mesma
     quantidade de nós pretos (a "altura negra").

Em vez de None, as pontas da árvore apontam para um único nó sentinela
`self.NIL`, preto e com tamanho 0. Assim dá pra perguntar `no.vermelho` ou
`no.pai` sem testar None toda hora - é como o Cormen (CLRS) faz.

Cada nó guarda também `pai` (as correções sobem a árvore) e `tamanho`
(quantos nós tem na subárvore, usado por posicao/k_esimo da ArvoreBase).
"""

from .base import ArvoreBase


class NoRN:
    __slots__ = ("chave", "valor", "esq", "dir", "pai", "tamanho", "vermelho")

    def __init__(self, chave, valor, nil, vermelho=True):
        self.chave = chave
        self.valor = valor
        self.esq = nil
        self.dir = nil
        self.pai = nil
        self.tamanho = 1
        self.vermelho = vermelho


class RubroNegra(ArvoreBase):
    nome = "Rubro-negra"

    def __init__(self):
        nil = NoRN(None, None, None, vermelho=False)
        nil.esq = nil.dir = nil.pai = nil
        nil.tamanho = 0
        self.NIL = nil  # um sentinela por árvore
        super().__init__()

    # ---------- utilidades ----------

    def _pintar(self, no, vermelho):
        """Muda a cor e conta nas métricas (só se mudou de verdade)."""
        if no.vermelho != vermelho:
            no.vermelho = vermelho
            self.metricas.recoloracoes += 1

    def _rotacionar_esquerda(self, x):
        """
              x                 y
             / \\              / \\
            a   y     ->      x   c
               / \\           / \\
              b   c         a   b
        """
        y = x.dir
        x.dir = y.esq
        if y.esq is not self.NIL:
            y.esq.pai = x
        self._trocar_no_pai(x, y)
        y.esq = x
        x.pai = y
        # y fica com a subárvore inteira que era de x; x é recalculado
        y.tamanho = x.tamanho
        self._atualizar_tamanho(x)
        self.metricas.rotacoes += 1

    def _rotacionar_direita(self, x):
        """Espelho da rotação à esquerda."""
        y = x.esq
        x.esq = y.dir
        if y.dir is not self.NIL:
            y.dir.pai = x
        self._trocar_no_pai(x, y)
        y.dir = x
        x.pai = y
        y.tamanho = x.tamanho
        self._atualizar_tamanho(x)
        self.metricas.rotacoes += 1

    def _trocar_no_pai(self, velho, novo):
        """Faz o pai de `velho` apontar para `novo` (o "transplant" do Cormen)."""
        pai = velho.pai
        if pai is self.NIL:
            self.raiz = novo
        elif velho is pai.esq:
            pai.esq = novo
        else:
            pai.dir = novo
        novo.pai = pai

    # ---------- inserção ----------

    def inserir(self, chave, valor=None):
        # 1) desce como numa BST comum procurando o lugar
        pai = self.NIL
        no = self.raiz
        c = 0
        while no is not self.NIL:
            c = self._comparar(chave, no.chave)
            if c == 0:
                return False  # chave repetida: nada muda
            pai = no
            no = no.esq if c < 0 else no.dir

        # 2) pendura o nó novo, sempre VERMELHO (não muda a altura negra)
        novo = NoRN(chave, valor, self.NIL)
        novo.pai = pai
        if pai is self.NIL:
            self.raiz = novo
        elif c < 0:
            pai.esq = novo
        else:
            pai.dir = novo

        # 3) todo mundo no caminho ganhou 1 nó na subárvore
        acima = pai
        while acima is not self.NIL:
            acima.tamanho += 1
            acima = acima.pai

        # 4) o único problema possível: novo vermelho com pai vermelho
        self._corrigir_insercao(novo)
        return True

    def _corrigir_insercao(self, z):
        while z.pai.vermelho:
            pai = z.pai
            avo = pai.pai  # existe: pai vermelho nunca é a raiz
            if pai is avo.esq:
                tio = avo.dir
                if tio.vermelho:
                    # caso 1: tio vermelho -> só recolore e o problema sobe
                    self._pintar(pai, False)
                    self._pintar(tio, False)
                    self._pintar(avo, True)
                    z = avo
                else:
                    if z is pai.dir:
                        # caso 2: z em "zigue-zague" -> gira pra virar o caso 3
                        z = pai
                        self._rotacionar_esquerda(z)
                        pai = z.pai
                    # caso 3: z em linha reta -> gira o avô e troca as cores
                    self._pintar(pai, False)
                    self._pintar(avo, True)
                    self._rotacionar_direita(avo)
            else:  # espelho: pai é filho direito do avô
                tio = avo.esq
                if tio.vermelho:
                    self._pintar(pai, False)
                    self._pintar(tio, False)
                    self._pintar(avo, True)
                    z = avo
                else:
                    if z is pai.esq:
                        z = pai
                        self._rotacionar_direita(z)
                        pai = z.pai
                    self._pintar(pai, False)
                    self._pintar(avo, True)
                    self._rotacionar_esquerda(avo)
        self._pintar(self.raiz, False)  # regra 2

    # ---------- remoção ----------

    def remover(self, chave):
        raise NotImplementedError("Rubro-negra: remoção ainda não implementada")
