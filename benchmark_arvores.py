"""Benchmark BST × AVL × rubro-negra com as matrículas da base.

Para cada árvore:
  1. insere n matrículas (em ordem crescente, como chegam num semestre novo,
     ou embaralhadas), anotando a altura ao longo do caminho;
  2. busca 1.000 matrículas sorteadas (média de comparações por busca);
  3. remove 10% delas.

A BST comum com chaves crescentes vira uma lista: cada inserção percorre a
árvore inteira (O(n²) no total). Por isso, nesse caso, ela para em
LIMITE_BST_DEGENERADA e o resultado mostra até onde chegou.
"""

import random
import time

from arvores import ARVORES

LIMITE_BST_DEGENERADA = 3000
PONTOS_CURVA = 20
BUSCAS = 1000


def _implementada(classe):
    try:
        teste = classe()
        teste.inserir(0)
        teste.remover(0)
        return True
    except NotImplementedError:
        return False


def _medir(arv, tarefa):
    arv.metricas.zerar()
    inicio = time.perf_counter()
    tarefa()
    return {"tempo_ms": round((time.perf_counter() - inicio) * 1000, 2), **arv.metricas.como_dict()}


def rodar_uma(classe, chaves, ordenadas, rng):
    arv = classe()
    limitada = classe.__name__ == "BST" and ordenadas and len(chaves) > LIMITE_BST_DEGENERADA
    if limitada:
        chaves = chaves[:LIMITE_BST_DEGENERADA]
    n = len(chaves)

    curva = []
    passo = max(1, n // PONTOS_CURVA)

    def inserir_tudo():
        for i, c in enumerate(chaves, start=1):
            arv.inserir(c)
            if i % passo == 0 or i == n:
                # altura() percorre a árvore inteira: o tempo dela é descontado
                t = time.perf_counter()
                curva.append([i, arv.altura()])
                pausa[0] += time.perf_counter() - t

    pausa = [0.0]
    insercao = _medir(arv, inserir_tudo)
    insercao["tempo_ms"] = round(insercao["tempo_ms"] - pausa[0] * 1000, 2)
    altura = arv.altura()

    alvos = rng.sample(chaves, min(BUSCAS, n))
    busca = _medir(arv, lambda: [arv.buscar(c) for c in alvos])
    busca["media_comparacoes"] = round(busca["comparacoes"] / len(alvos), 1)

    saem = rng.sample(chaves, n // 10)
    remocao = _medir(arv, lambda: [arv.remover(c) for c in saem])

    return {
        "n": n,
        "limitada": limitada,
        "altura": altura,
        "altura_final": arv.altura(),
        "curva": curva,
        "insercao": insercao,
        "busca": busca,
        "remocao": remocao,
    }


def rodar(matriculas, n, ordem, semente=None):
    rng = random.Random(semente)
    chaves = rng.sample(matriculas, min(n, len(matriculas)))
    ordenadas = ordem == "crescente"
    if ordenadas:
        chaves.sort()

    resultados = []
    for id_arv, classe in ARVORES.items():
        linha = {"arvore": id_arv, "nome": classe.nome}
        if not _implementada(classe):
            linha["pendente"] = True
        else:
            linha.update(rodar_uma(classe, chaves, ordenadas, random.Random(semente)))
        resultados.append(linha)
    return {"n": len(chaves), "ordem": ordem, "limite_bst": LIMITE_BST_DEGENERADA,
            "arvores": resultados}
