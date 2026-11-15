"""Fila de espera de uma turma, guardada numa árvore rubro-negra.

Como funciona, em duas fases:
  1. Período de matrícula: os pedidos do período são processados de uma vez
     com a ordenação do trabalho 2 (merge sort, estável). Os primeiros, até
     o número de vagas, ficam MATRICULADOS; o resto vai pra FILA DE ESPERA.
  2. Depois disso a turma muda o tempo todo:
       - pedido novo   -> entra direto se sobrou vaga; senão entra na fila,
                          no lugar que a prioridade dele manda (um formando
                          com IRA alto passa na frente de quem já estava lá);
       - trancamento   -> a vaga abre e o 1º da fila é promovido na hora;
       - desistência   -> o aluno sai da fila.

Por que árvore e não lista ordenada? Numa lista, cada pedido novo ou
desistência custa O(n) (achar o lugar e deslocar todo mundo), e reordenar
tudo a cada mudança custa O(n log n). Na rubro-negra cada operação é
O(log n): inserir, remover, achar o 1º (k_esimo(1)) e responder "qual a
minha posição na fila?" (posicao) - essa última graças ao `tamanho` que
cada nó guarda.

A chave na árvore é a própria prioridade da matrícula:
    (não formando, -IRA, -semestre, hora do pedido, id do pedido)
Menor chave = mais prioridade. O id no fim garante que nunca há duas iguais.
"""

from itertools import islice

from arvores import RubroNegra
from matricula import processar_turma

CAMPOS_ALUNO = ("pedido_id", "matricula", "nome", "curso", "pokemon_id", "shiny",
                "ira", "semestre", "formando", "timestamp")


def chave_prioridade(c):
    return (1 - c["formando"], -c["ira_int"], -c["semestre"], c["chegada"], c["pedido_id"])


def resumo(c):
    return {campo: c[campo] for campo in CAMPOS_ALUNO}


class ErroFila(Exception):
    pass


class FilaTurma:
    def __init__(self, turma, candidatos):
        self.turma = turma
        self.vagas = turma["vagas"]
        self.matriculados = {}   # matrícula -> aluno
        self.espera = RubroNegra()
        self.chave_de = {}       # matrícula -> chave dela na árvore
        self.trancados = set()
        self.historico = []      # últimas operações, pra mostrar na tela

        # fase 1: o resultado do período de matrícula (trabalho 2)
        r = processar_turma(turma, candidatos, "merge")
        for c in r["resultado"]:
            if c["deferido"]:
                self.matriculados[c["matricula"]] = c
            else:
                self._entrar_na_espera(c)

    # ---------- consultas ----------

    def situacao(self, matricula):
        if matricula in self.matriculados:
            return {"status": "matriculado"}
        if matricula in self.chave_de:
            return {"status": "espera", "posicao": self.espera.posicao(self.chave_de[matricula]),
                    "total": len(self.espera)}
        if matricula in self.trancados:
            return {"status": "trancado"}
        return None

    def primeiros_da_espera(self, n=50):
        return [{"posicao": i, **resumo(c)}
                for i, (_, c) in enumerate(islice(self.espera.em_ordem(), n), start=1)]

    def lista_matriculados(self):
        return sorted((resumo(c) for c in self.matriculados.values()), key=lambda c: c["nome"])

    def vagas_livres(self):
        return self.vagas - len(self.matriculados)

    # ---------- operações (fase 2) ----------

    def pedir(self, candidato):
        matricula = candidato["matricula"]
        if matricula in self.matriculados:
            raise ErroFila("Esse aluno já está matriculado na turma.")
        if matricula in self.chave_de:
            raise ErroFila("Esse aluno já está na fila de espera.")
        self.trancados.discard(matricula)

        def operacao():
            # se sobrou vaga, a fila está vazia (toda vaga aberta promove alguém)
            if self.vagas_livres() > 0:
                self.matriculados[matricula] = candidato
                return {"status": "matriculado"}
            self._entrar_na_espera(candidato)
            return self.situacao(matricula)

        return self._registrar("pedido", candidato, operacao)

    def trancar(self, matricula):
        aluno = self.matriculados.get(matricula)
        if aluno is None:
            raise ErroFila("Esse aluno não está matriculado na turma.")

        def operacao():
            del self.matriculados[matricula]
            self.trancados.add(matricula)
            promovido = self._promover_primeiro()
            return {"promovido": resumo(promovido) if promovido else None}

        return self._registrar("trancar", aluno, operacao)

    def desistir(self, matricula):
        if matricula not in self.chave_de:
            raise ErroFila("Esse aluno não está na fila de espera.")
        chave = self.chave_de[matricula]

        def operacao():
            posicao = self.espera.posicao(chave)
            self.espera.remover(chave)
            del self.chave_de[matricula]
            return {"saiu_da_posicao": posicao}

        return self._registrar("desistir", self.espera.buscar(chave), operacao)

    # ---------- por dentro ----------

    def _entrar_na_espera(self, c):
        chave = chave_prioridade(c)
        self.espera.inserir(chave, c)
        self.chave_de[c["matricula"]] = chave

    def _promover_primeiro(self):
        primeiro = self.espera.k_esimo(1)  # a menor chave = maior prioridade
        if primeiro is None:
            return None
        chave, aluno = primeiro
        self.espera.remover(chave)
        del self.chave_de[aluno["matricula"]]
        self.matriculados[aluno["matricula"]] = aluno
        return aluno

    def _registrar(self, tipo, aluno, operacao):
        """Roda a operação medindo quanto a árvore trabalhou nela."""
        antes = self.espera.metricas.como_dict()
        resultado = operacao()
        depois = self.espera.metricas.como_dict()
        evento = {
            "tipo": tipo,
            "aluno": resumo(aluno),
            **resultado,
            "custo": {k: depois[k] - antes[k] for k in antes},
            "na_espera": len(self.espera),
            "altura": self.espera.altura(),
        }
        self.historico.append(evento)
        del self.historico[:-20]
        return evento
