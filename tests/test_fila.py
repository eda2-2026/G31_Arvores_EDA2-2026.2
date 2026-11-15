import random
import unittest

from fila import ErroFila, FilaTurma, chave_prioridade

TURMA = {"codigo": "TST0001", "disciplina": "Teste", "professor": "-", "horario": "-", "vagas": 5}


def aluno(n, formando=0, ira=3.0, semestre=4, chegada=None):
    return {
        "pedido_id": n, "matricula": f"{n:09d}", "nome": f"Aluno {n}", "curso": "-",
        "pokemon_id": 1, "shiny": 0, "ira": ira, "ira_int": int(round(ira * 10000)),
        "semestre": semestre, "formando": formando, "timestamp": "2026-07-20T08:00:00",
        "chegada": chegada if chegada is not None else 1000 + n,
    }


class TestFila(unittest.TestCase):
    def setUp(self):
        # IRA decrescente: os 5 primeiros ficam com a vaga, 6..10 na espera
        self.fila = FilaTurma(TURMA, [aluno(i, ira=5 - i * 0.1) for i in range(1, 11)])

    def ordem_espera(self):
        return [c["pedido_id"] for c in self.fila.primeiros_da_espera(100)]

    def test_fase_1_corta_nas_vagas(self):

        """Processamento: os melhores ficam com as vagas, o resto vai pra fila."""
        self.assertEqual(sorted(self.fila.matriculados), [f"{i:09d}" for i in range(1, 6)])
        self.assertEqual(self.ordem_espera(), [6, 7, 8, 9, 10])
        self.assertEqual(self.fila.situacao(f"{8:09d}"), {"status": "espera", "posicao": 3, "total": 5})

    def test_trancar_promove_o_primeiro(self):

        """Trancamento promove o 1º da fila na hora."""
        ev = self.fila.trancar(f"{2:09d}")
        self.assertEqual(ev["promovido"]["pedido_id"], 6)
        self.assertEqual(self.fila.vagas_livres(), 0)
        self.assertEqual(self.ordem_espera(), [7, 8, 9, 10])
        self.assertEqual(self.fila.situacao(f"{2:09d}"), {"status": "trancado"})

    def test_pedido_novo_entra_no_lugar_da_prioridade(self):

        """Pedido novo entra no lugar da prioridade (formando fura a fila)."""
        ev = self.fila.pedir(aluno(50, formando=1, ira=2.0))  # formando passa na frente
        self.assertEqual(ev["posicao"], 1)
        ev = self.fila.pedir(aluno(51, ira=1.0))  # IRA baixo vai pro fim
        self.assertEqual(ev["posicao"], 7)
        ev = self.fila.pedir(aluno(52, ira=5 - 7.5 * 0.1))  # entre o 7 e o 8
        self.assertEqual(ev["posicao"], 4)
        self.assertEqual(self.ordem_espera(), [50, 6, 7, 52, 8, 9, 10, 51])

    def test_vaga_livre_matricula_direto(self):

        """Sobrou vaga e a fila está vazia: matricula direto."""
        for i in range(6, 11):
            self.fila.desistir(f"{i:09d}")
        self.fila.trancar(f"{1:09d}")  # ninguém na fila pra promover
        self.assertEqual(self.fila.vagas_livres(), 1)
        self.assertEqual(self.fila.pedir(aluno(60))["status"], "matriculado")
        self.assertEqual(self.fila.vagas_livres(), 0)

    def test_desistir(self):

        """Desistência tira da fila e quem estava atrás sobe."""
        ev = self.fila.desistir(f"{7:09d}")
        self.assertEqual(ev["saiu_da_posicao"], 2)
        self.assertEqual(self.ordem_espera(), [6, 8, 9, 10])
        self.assertEqual(self.fila.situacao(f"{8:09d}")["posicao"], 2)

    def test_erros(self):

        """Recusa operações inválidas (já matriculado, não está na fila...)."""
        with self.assertRaises(ErroFila):
            self.fila.pedir(aluno(1))       # já matriculado
        with self.assertRaises(ErroFila):
            self.fila.pedir(aluno(6))       # já na espera
        with self.assertRaises(ErroFila):
            self.fila.trancar(f"{6:09d}")   # não está matriculado
        with self.assertRaises(ErroFila):
            self.fila.desistir(f"{1:09d}")  # não está na espera

    def test_trancou_e_pediu_de_novo(self):

        """Quem trancou pode pedir de novo e volta pra fila."""
        self.fila.trancar(f"{1:09d}")
        ev = self.fila.pedir(aluno(1, ira=4.9, chegada=99999))
        self.assertEqual(ev["status"], "espera")

    def test_operacoes_aleatorias_contra_lista_ordenada(self):

        """800 operações aleatórias: fila na árvore igual a uma lista reordenada a cada passo."""
        # o "jeito lento": uma lista que é reordenada inteira a cada mudança
        rng = random.Random(7)
        fila = FilaTurma(TURMA, [])
        matriculados, espera = set(), []
        proximo = 1
        for _ in range(800):
            op = rng.random()
            if op < 0.5:
                a = aluno(proximo, formando=rng.randint(0, 1), ira=rng.randint(0, 50) / 10,
                          semestre=rng.randint(1, 12))
                proximo += 1
                ev = fila.pedir(a)
                if len(matriculados) < TURMA["vagas"]:
                    matriculados.add(a["matricula"])
                else:
                    espera.append(a)
                    espera.sort(key=chave_prioridade)
                    self.assertEqual(ev["posicao"], espera.index(a) + 1)
            elif op < 0.8 and matriculados:
                m = rng.choice(sorted(matriculados))
                ev = fila.trancar(m)
                matriculados.remove(m)
                if espera:
                    primeiro = espera.pop(0)
                    matriculados.add(primeiro["matricula"])
                    self.assertEqual(ev["promovido"]["matricula"], primeiro["matricula"])
            elif espera:
                a = rng.choice(espera)
                ev = fila.desistir(a["matricula"])
                self.assertEqual(ev["saiu_da_posicao"], espera.index(a) + 1)
                espera.remove(a)
            self.assertEqual(set(fila.matriculados), matriculados)
            self.assertEqual([c["pedido_id"] for _, c in fila.espera.em_ordem()],
                             [a["pedido_id"] for a in espera])


if __name__ == "__main__":
    unittest.main()
