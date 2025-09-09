from Procesos.lectura import lectura
from Procesos.limpieza import limpia
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
    
transiciones = [
    #Par izq
    (0,3,'('),
    #Par der
    (0,8,')'),
    #Par der rompecadena
    (8,9,'+'),
    (8,9,'-'),
    #Op
    (0,1,'/'),
    (0,1,'='),
    (0,1,'*'),
    #num simbolo
    (0,6,'+'),
    (0,6,'-'),
    (6,5,'num'),
    #num
    (0,5,'num'),
    (6,5,'num'),
    #loopnum
    (5,5,'num'),
    #num rompecadenas
    (5,7,'+'),
    (5,7,'-'),
    #id
    (0,2,'char'),
    #loopid
    (2,2,'char'),
    #id rompecadenas
    (2,4,'+'),
    (2,4,'-')
]
#Aceptacion
estados_finales = {1,2,3,4,5,6,7,8,9}

lexi = Lexico(transiciones, estados_finales)

#Inicio del programa
#Lee archivo
t = lectura("Codigos/Robin.txt")
#Limpia texto
t = limpia(t)
#Tokeniza el texto bonito
tokens = Lexico.tokenizacion(lexi,t)
#Si no hay tokens, bye
if not tokens:
    exit(1)
#Imprime tokens
print("Lexico: ", tokens)
