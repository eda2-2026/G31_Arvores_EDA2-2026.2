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
        z = self._no(chave)
        if z is self.NIL:
            return None
        valor = z.valor

        # y = nó que sai fisicamente do lugar dele:
        #   z mesmo, se tem no máximo 1 filho; senão o sucessor de z
        y = z
        if z.esq is not self.NIL and z.dir is not self.NIL:
            y = z.dir
            while y.esq is not self.NIL:
                y = y.esq
        y_era_vermelho = y.vermelho

        # toda subárvore acima de onde y estava perde 1 nó
        acima = y.pai
        while acima is not self.NIL:
            acima.tamanho -= 1
            acima = acima.pai

        # x = quem ocupa o lugar antigo de y (pode ser o NIL)
        if z.esq is self.NIL:
            x = z.dir
            self._trocar_no_pai(z, z.dir)
        elif z.dir is self.NIL:
            x = z.esq
            self._trocar_no_pai(z, z.esq)
        else:
            x = y.dir
            if y.pai is z:
                x.pai = y  # importante quando x é o NIL
            else:
                self._trocar_no_pai(y, y.dir)
                y.dir = z.dir
                y.dir.pai = y
            # y assume o lugar de z: filhos, cor e tamanho
            self._trocar_no_pai(z, y)
            y.esq = z.esq
            y.esq.pai = y
            y.vermelho = z.vermelho
            y.tamanho = z.tamanho

        # tirar um vermelho não quebra nada; tirar um preto deixa um caminho
        # com um preto a menos -> x fica "duplo preto" e precisa ser corrigido
        if not y_era_vermelho:
            self._corrigir_remocao(x)
        return valor

    def _corrigir_remocao(self, x):
        while x is not self.raiz and not x.vermelho:
            pai = x.pai
            if x is pai.esq:
                irmao = pai.dir
                if irmao.vermelho:
                    # caso 1: irmão vermelho -> gira pra ficar com irmão preto
                    self._pintar(irmao, False)
                    self._pintar(pai, True)
                    self._rotacionar_esquerda(pai)
                    irmao = pai.dir
                if not irmao.esq.vermelho and not irmao.dir.vermelho:
                    # caso 2: irmão preto com filhos pretos -> irmão vira
                    # vermelho e o "preto extra" sobe pro pai
                    self._pintar(irmao, True)
                    x = pai
                else:
                    if not irmao.dir.vermelho:
                        # caso 3: só o sobrinho de dentro é vermelho -> gira
                        # o irmão pra virar o caso 4
                        self._pintar(irmao.esq, False)
                        self._pintar(irmao, True)
                        self._rotacionar_direita(irmao)
                        irmao = pai.dir
                    # caso 4: sobrinho de fora vermelho -> uma rotação no pai
                    # devolve o preto que faltava e acaba
                    self._pintar(irmao, pai.vermelho)
                    self._pintar(pai, False)
                    self._pintar(irmao.dir, False)
                    self._rotacionar_esquerda(pai)
                    x = self.raiz
            else:  # espelho: x é filho direito
                irmao = pai.esq
                if irmao.vermelho:
                    self._pintar(irmao, False)
                    self._pintar(pai, True)
                    self._rotacionar_direita(pai)
                    irmao = pai.esq
                if not irmao.dir.vermelho and not irmao.esq.vermelho:
                    self._pintar(irmao, True)
                    x = pai
                else:
                    if not irmao.esq.vermelho:
                        self._pintar(irmao.dir, False)
                        self._pintar(irmao, True)
                        self._rotacionar_esquerda(irmao)
                        irmao = pai.esq
                    self._pintar(irmao, pai.vermelho)
                    self._pintar(pai, False)
                    self._pintar(irmao.esq, False)
                    self._rotacionar_direita(pai)
                    x = self.raiz
        self._pintar(x, False)
