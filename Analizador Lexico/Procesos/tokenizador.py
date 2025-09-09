from Procesos.tokens import llaves
from Procesos.transiciones import num

def tokenizacion(lexi, texto):
    resultado = []
    cont_string = 0
    palabras = texto.split()
    for palabra in palabras:
        estado = lexi.estado_inicial
        palanca_string = 0
        for letra in palabra:
            trans = lexi.estados.get(estado, {})
            if letra in trans:
                estado = trans[letra]
            elif letra >= 'a' and letra <= 'z':
                estado = trans['minuschar']
            elif letra in num:
                estado = trans['num']
            elif letra in ('+','-'):
                estado = trans['sim']
            else:
                raise ValueError(f"no es posible tokenizar '{palabra}'")
        cont_string += 1
        if estado in lexi.estados_finales:
            token = llaves.get(estado)
            if token:
                resultado.append(token)
            else:
                raise ValueError(f"no es posible tokenizar '{palabra}' (estado final desconocido)")
        else:
            raise ValueError(f"no es posible tokenizar '{palabra}' (no es estado final)")
    return resultado