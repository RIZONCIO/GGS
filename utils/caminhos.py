import os
import sys


def get_pasta_cofre():
    raiz = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(raiz, "cofre")
