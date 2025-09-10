from Procesos.tokens import llaves
from Procesos.transiciones import num

def tokenizacion(lexi, texto):
    resultado = []
    i = 0
    
    while i < len(texto):
        # Saltar espacios en blanco y saltos de línea fuera de strings
        if texto[i] in (' ', '\t', '\n', '\r'):
            i += 1
            continue
            
        # Inicializar para nuevo token
        estado = lexi.estado_inicial
        j = i
        
        # Caso especial para strings
        if texto[i] == '"':
            # Primera comilla
            trans = lexi.estados.get(estado, {})
            if '"' in trans:
                estado = trans['"']
            else:
                raise ValueError(f"Error al iniciar string en posición {i}")
            
            j += 1
            # Procesar caracteres dentro del string
            while j < len(texto) and texto[j] != '"':
                trans = lexi.estados.get(estado, {})
                if 'string' in trans:
                    estado = trans['string']
                else:
                    raise ValueError(f"Error procesando string en posición {j}")
                j += 1
            
            # Comilla de cierre
            if j < len(texto) and texto[j] == '"':
                trans = lexi.estados.get(estado, {})
                if '"' in trans:
                    estado = trans['"']
                    j += 1
                else:
                    raise ValueError(f"Error cerrando string en posición {j}")
            else:
                raise ValueError(f"String sin cerrar iniciado en posición {i}")
        
        else:
            # Procesar token normal (palabra, número, símbolo)
            while j < len(texto) and texto[j] not in (' ', '\t', '\n', '\r'):
                letra = texto[j]
                trans = lexi.estados.get(estado, {})
                
                # Buscar transición específica por letra exacta
                if letra in trans:
                    estado = trans[letra]
                # Buscar por categorías
                elif letra >= 'a' and letra <= 'z' and 'minuschar' in trans:
                    estado = trans['minuschar']
                elif letra in num and 'num' in trans:
                    estado = trans['num']
                elif letra in ('+', '-') and 'sim' in trans:
                    estado = trans['sim']
                elif letra == '.' and '.' in trans:
                    estado = trans['.']
                else:
                    # Si no hay transición válida, verificar si el estado actual es final
                    if estado in lexi.estados_finales:
                        # Es un token válido, esta letra pertenece al siguiente token
                        break
                    else:
                        raise ValueError(f"No es posible tokenizar en posición {i}, carácter '{letra}', estado {estado}")
                
                j += 1
                
                # Para símbolos individuales, terminar inmediatamente
                if letra in (';', ':', '(', ')', ',', '{', '}'):
                    break
        
        # Verificar si llegamos a un estado final
        if estado in lexi.estados_finales:
            token = llaves.get(estado)
            if token:
                resultado.append(token)
            else:
                raise ValueError(f"Estado final desconocido {estado}")
        else:
            raise ValueError(f"No termina en estado final (estado {estado})")
        
        i = j
    
    return resultado