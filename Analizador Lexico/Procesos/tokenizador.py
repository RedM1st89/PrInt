from Procesos.tokens import llaves
from Procesos.transiciones import num

def tokenizacion(lexi, texto):
    resultado = []
    palabras = texto.split()
    for palabra in palabras:
        estado = lexi.estado_inicial
        palanca_string = 0
        letra_pos = 0
        for letra in palabra:
            trans = lexi.estados.get(estado, {})
            if letra in ('"'):
                if letra_pos == 0:
                    estado = trans['"']
                    palanca_string = 1
                if letra_pos == len(palabra)-1:
                    estado = trans['"']
            elif palanca_string == 1:
                if letra in (" "):
                    continue
                else:
                    estado = trans['string']
            elif letra in trans:
                estado = trans[letra]
            elif letra >= 'a' and letra <= 'z':
                estado = trans['minuschar']
            elif letra in num:
                estado = trans['num']
            elif letra in ('+','-'):
                estado = trans['sim']
            else:
                raise ValueError(f"no es posible tokenizar '{palabra}'")
            letra_pos += 1
            print(letra_pos)
        if estado in lexi.estados_finales:
            token = llaves.get(estado)
            if token:
                resultado.append(token)
            else:
                raise ValueError(f"no es posible tokenizar '{palabra}' (estado final desconocido)")
        else:
            raise ValueError(f"no es posible tokenizar '{palabra}' (no es estado final)")
    return resultado