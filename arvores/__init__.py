from .base import ArvoreBase, Metricas
from .bst import BST
from .avl import AVL
from .rubro_negra import RubroNegra

ARVORES = {
    "bst": BST,
    "avl": AVL,
    "rubro_negra": RubroNegra,
}
