import os
from .Procesos.lectura import lectura
from .Procesos.limpieza import limpia
from .Procesos.transiciones import transiciones, estados_finales
from .Procesos.tokenizador import tokenizacion

class Lexico:
    def __init__(self, transiciones, estados_finales):
        self.estado_inicial = 0
        self.estados_finales = estados_finales
        self.estados = self._crear_estados(transiciones)

    def _crear_estados(self, transiciones):
        estados = {}
        for origen, destino, simbolo in transiciones:
            if origen not in estados:
                estados[origen] = {}
            estados[origen][simbolo] = destino
        return estados

def inicia_lexico(archivo="Codigos/Enzo.txt"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, archivo)
    
    lexi = Lexico(transiciones, estados_finales)
    t = lectura(full_path)
    t = limpia(t)
    tokens = tokenizacion(lexi, t)
    if not tokens:
        return None
    print("Lexico: ", tokens)
    
    return tokens