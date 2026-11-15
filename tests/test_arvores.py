"""Testes das árvores. Rode na raiz do projeto com:  py -m unittest -v

Os mesmos testes valem para as três árvores. Depois de cada inserção e
remoção, conferem:
  - todas: ordem das chaves, `tamanho` de cada nó, resposta igual a um
    dicionário comum fazendo as mesmas operações;
  - AVL: `altura` de cada nó e fator de balanceamento entre -1 e 1;
  - rubro-negra: as 5 propriedades (raiz preta, NIL preto, vermelho sem filho
    vermelho, mesma quantidade de pretos em todo caminho) e os ponteiros `pai`.

Árvore ainda não implementada (NotImplementedError) é pulada, não reprovada.
"""

import math
import random
import unittest

from arvores import AVL, BST, RubroNegra


def todos_os_nos(arv):
    nos = []
    pilha = [arv.raiz] if arv.raiz is not arv.NIL else []
    while pilha:
        no = pilha.pop()
        nos.append(no)
        for filho in (no.esq, no.dir):
            if filho is not arv.NIL:
                pilha.append(filho)
    return nos


class TestesComuns:
    ARVORE = None
    LIMITE_ALTURA = None  # função n -> altura máxima permitida (None = sem limite)

    def setUp(self):
        try:
            teste = self.ARVORE()
            teste.inserir(0)
            teste.remover(0)
        except NotImplementedError as erro:
            self.skipTest(str(erro))
        self.arv = self.ARVORE()
        self.rng = random.Random(31)

    # ---- verificações ----

    def verificar(self, modelo=None):
        arv = self.arv
        nos = todos_os_nos(arv)
        self.assertEqual(len(arv), len(nos), "tamanho da raiz não bate com a quantidade de nós")
        for no in nos:
            esperado = 1 + arv._tam(no.esq) + arv._tam(no.dir)
            self.assertEqual(no.tamanho, esperado, f"tamanho errado no nó {no.chave!r}")
        chaves = [c for c, _ in arv.em_ordem()]
        self.assertEqual(chaves, sorted(chaves), "chaves fora de ordem")
        self.assertEqual(len(chaves), len(set(chaves)), "chave repetida na árvore")
        if modelo is not None:
            self.assertEqual(list(arv.em_ordem()), sorted(modelo.items()))
        self.verificar_extra()

    def verificar_extra(self):
        pass

    # ---- testes ----

    def test_vazia(self):
        self.assertEqual(len(self.arv), 0)
        self.assertEqual(self.arv.altura(), 0)
        self.assertIsNone(self.arv.buscar(5))
        self.assertIsNone(self.arv.remover(5))
        self.assertIsNone(self.arv.k_esimo(1))
        self.assertIsNone(self.arv.posicao(5))
        self.assertEqual(self.arv.intervalo(0, 10), [])
        self.verificar()

    def test_insere_busca_e_repetida(self):
        self.assertTrue(self.arv.inserir(10, "dez"))
        self.assertTrue(self.arv.inserir(5, "cinco"))
        self.assertFalse(self.arv.inserir(10, "outro"))
        self.assertEqual(self.arv.buscar(10), "dez")
        self.assertEqual(len(self.arv), 2)
        self.assertIn(5, self.arv)
        self.assertNotIn(7, self.arv)
        self.verificar()

    def test_operacoes_aleatorias(self):
        modelo = {}
        for i in range(1500):
            chave = self.rng.randint(0, 300)
            if self.rng.random() < 0.6:
                inseriu = self.arv.inserir(chave, i)
                self.assertEqual(inseriu, chave not in modelo)
                if inseriu:
                    modelo[chave] = i
            else:
                self.assertEqual(self.arv.remover(chave), modelo.pop(chave, None))
            self.verificar(modelo)

    def test_remove_tudo(self):
        chaves = self.rng.sample(range(5000), 600)
        for c in chaves:
            self.arv.inserir(c, c * 2)
        self.rng.shuffle(chaves)
        modelo = {c: c * 2 for c in chaves}
        for c in chaves:
            self.assertEqual(self.arv.remover(c), c * 2)
            del modelo[c]
            self.verificar(modelo)
        self.assertEqual(self.arv.raiz, self.arv.NIL)

    def test_sequencial_crescente(self):
        # é assim que as matrículas de um semestre novo chegam
        n = 2000
        for c in range(n):
            self.arv.inserir(c)
        self.verificar()
        if self.LIMITE_ALTURA:
            self.assertLessEqual(self.arv.altura(), self.LIMITE_ALTURA(n))

    def test_consultas_de_ordem(self):
        chaves = self.rng.sample(range(10000), 800)
        for c in chaves:
            self.arv.inserir(c, str(c))
        ordenadas = sorted(chaves)
        for i, c in enumerate(ordenadas, start=1):
            self.assertEqual(self.arv.posicao(c), i)
            self.assertEqual(self.arv.k_esimo(i), (c, str(c)))
        self.assertIsNone(self.arv.k_esimo(0))
        self.assertIsNone(self.arv.k_esimo(len(chaves) + 1))
        self.assertIsNone(self.arv.posicao(-1))
        for _ in range(50):
            a, b = sorted(self.rng.sample(range(10000), 2))
            esperado = [(c, str(c)) for c in ordenadas if a <= c <= b]
            self.assertEqual(self.arv.intervalo(a, b), esperado)

    def test_chave_composta(self):
        # a prioridade da matrícula: (não formando, -IRA, -semestre, hora)
        pedidos = [(0, -45000, -9, 100), (1, -38000, -5, 50), (0, -45000, -9, 90), (0, -47000, -12, 300)]
        for p in pedidos:
            self.arv.inserir(p, p)
        self.assertEqual(self.arv.menor()[0], (0, -47000, -12, 300))
        self.assertEqual(self.arv.posicao((0, -45000, -9, 90)), 2)
        self.verificar()

    def test_metricas_contam_comparacoes(self):
        for c in range(50):
            self.arv.inserir(c)
        self.assertGreater(self.arv.metricas.comparacoes, 0)


class TestBST(TestesComuns, unittest.TestCase):
    ARVORE = BST


class TestAVL(TestesComuns, unittest.TestCase):
    ARVORE = AVL
    LIMITE_ALTURA = staticmethod(lambda n: 1.4405 * math.log2(n + 2) - 0.3277)

    def verificar_extra(self):
        def altura(no):
            return 0 if no is None else no.altura
        for no in todos_os_nos(self.arv):
            self.assertEqual(no.altura, 1 + max(altura(no.esq), altura(no.dir)),
                             f"altura errada no nó {no.chave!r}")
            self.assertLessEqual(abs(altura(no.esq) - altura(no.dir)), 1,
                                 f"nó {no.chave!r} desbalanceado")

    def test_rotacoes_contadas(self):
        for c in range(100):
            self.arv.inserir(c)
        self.assertGreater(self.arv.metricas.rotacoes, 0)


class TestRubroNegra(TestesComuns, unittest.TestCase):
    ARVORE = RubroNegra
    LIMITE_ALTURA = staticmethod(lambda n: 2 * math.log2(n + 1))

    def verificar_extra(self):
        arv = self.arv
        nil = arv.NIL
        self.assertFalse(nil.vermelho, "NIL tem que ser preto")
        if arv.raiz is nil:
            return
        self.assertFalse(arv.raiz.vermelho, "raiz tem que ser preta")
        self.assertIs(arv.raiz.pai, nil, "raiz não pode ter pai")

        def pretos(no):
            if no is nil:
                return 1
            for filho in (no.esq, no.dir):
                if filho is not nil:
                    self.assertIs(filho.pai, no, f"ponteiro pai errado em {filho.chave!r}")
                    if no.vermelho:
                        self.assertFalse(filho.vermelho, f"vermelho {no.chave!r} com filho vermelho")
            esq, dir_ = pretos(no.esq), pretos(no.dir)
            self.assertEqual(esq, dir_, f"altura negra diferente abaixo de {no.chave!r}")
            return esq + (0 if no.vermelho else 1)

        pretos(arv.raiz)

    def test_rotacoes_e_recoloracoes_contadas(self):
        for c in range(100):
            self.arv.inserir(c)
        self.assertGreater(self.arv.metricas.rotacoes, 0)
        self.assertGreater(self.arv.metricas.recoloracoes, 0)


if __name__ == "__main__":
    unittest.main()
