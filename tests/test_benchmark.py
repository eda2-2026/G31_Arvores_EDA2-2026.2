import unittest

import benchmark_arvores as b


class TestBenchmark(unittest.TestCase):
    def test_crescente_degenera_a_bst_e_nao_a_rubro_negra(self):
        """Matrículas crescentes: a BST vira lista, a rubro-negra não."""
        chaves = list(range(261000001, 261000001 + 4000))
        r = b.rodar(chaves, 4000, "crescente", semente=1)
        arv = {a["arvore"]: a for a in r["arvores"]}
        bst, rn = arv["bst"], arv["rubro_negra"]
        self.assertTrue(bst["limitada"])
        self.assertEqual(bst["n"], b.LIMITE_BST_DEGENERADA)
        self.assertEqual(bst["altura"], b.LIMITE_BST_DEGENERADA)  # virou lista
        self.assertEqual(rn["n"], 4000)
        self.assertLessEqual(rn["altura"], 2 * 12)  # 2·log2(4001) ≈ 23,9
        self.assertEqual(rn["curva"][-1], [4000, rn["altura"]])
        self.assertGreater(bst["busca"]["media_comparacoes"], 50 * rn["busca"]["media_comparacoes"])

    def test_aleatoria_nao_limita(self):

        """Ordem aleatória: todas as árvores recebem todas as matrículas."""
        r = b.rodar(list(range(5000)), 2000, "aleatoria", semente=2)
        for a in r["arvores"]:
            if not a.get("pendente"):
                self.assertEqual(a["n"], 2000)
                self.assertFalse(a["limitada"])


if __name__ == "__main__":
    unittest.main()
