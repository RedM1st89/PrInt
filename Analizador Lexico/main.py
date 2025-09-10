from Procesos.lectura import lectura
from Procesos.limpieza import limpia
from Procesos.transiciones import transiciones
from Procesos.transiciones import estados_finales
from Procesos.tokenizador import tokenizacion
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
    


lexi = Lexico(transiciones, estados_finales)

#Inicio del programa
#Lee archivo
t = lectura("Codigos/Enzo.txt")
#Limpia texto
t = limpia(t)
#Tokeniza el texto bonito
tokens = tokenizacion(lexi,t)
#Si no hay tokens, bye
if not tokens:
    exit(1)
#Imprime tokens
print("Lexico: ", tokens)
