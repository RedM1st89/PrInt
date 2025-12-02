from .tokens import llaves
from .transiciones import num

class Token:
    def __init__(self, tipo, lexema, linea):
        self.tipo = tipo
        self.lexema = lexema
        self.linea = linea
    
    def __repr__(self):
        return f"Token({self.tipo}, '{self.lexema}', L{self.linea})"
    
    def __str__(self):
        return self.tipo  # Para compatibilidad con análisis sintáctico

def tokenizacion(lexi, texto):
    resultado = []
    i = 0
    linea_actual = 1  # Contador de líneas
    
    while i < len(texto):
        # Contar saltos de línea para tracking
        if texto[i] == '\n':
            linea_actual += 1
            i += 1
            continue
            
        # Saltar espacios en blanco y tabs
        if texto[i] in (' ', '\t', '\r'):
            i += 1
            continue
            
        # Guardar posición inicial del token
        inicio = i
        estado = lexi.estado_inicial
        j = i
        
        # Caso especial para strings
        if texto[i] == '"':
            # Primera comilla
            trans = lexi.estados.get(estado, {})
            if '"' in trans:
                estado = trans['"']
            else:
                raise ValueError(f"Error al iniciar string en línea {linea_actual}")
            
            j += 1
            # Procesar caracteres dentro del string
            while j < len(texto) and texto[j] != '"':
                trans = lexi.estados.get(estado, {})
                if 'string' in trans:
                    estado = trans['string']
                else:
                    raise ValueError(f"Error procesando string en línea {linea_actual}")
                j += 1
            
            # Comilla de cierre
            if j < len(texto) and texto[j] == '"':
                trans = lexi.estados.get(estado, {})
                if '"' in trans:
                    estado = trans['"']
                    j += 1
                else:
                    raise ValueError(f"Error cerrando string en línea {linea_actual}")
            else:
                raise ValueError(f"String sin cerrar en línea {linea_actual}")
        
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
                elif letra in ('+') and 'pos' in trans:
                    estado = trans['pos']
                elif letra in ('-') and 'neg' in trans:
                    estado = trans['neg']
                elif letra == '.' and '.' in trans:
                    estado = trans['.']
                else:
                    # Si no hay transición válida, verificar si el estado actual es final
                    if estado in lexi.estados_finales:
                        # Es un token válido, esta letra pertenece al siguiente token
                        break
                    else:
                        raise ValueError(f"No es posible tokenizar en línea {linea_actual}, carácter '{letra}', estado {estado}")
                
                j += 1
                
                # Para símbolos individuales, terminar inmediatamente
                if letra in (';', ':', '(', ')', ',', '{', '}'):
                    break
        
        # Verificar si llegamos a un estado final
        if estado in lexi.estados_finales:
            token_tipo = llaves.get(estado)
            if token_tipo:
                # Extraer el lexema (texto original)
                lexema = texto[inicio:j]
                # Crear token rico con tipo, lexema y línea
                token_obj = Token(token_tipo, lexema, linea_actual)
                resultado.append(token_obj)
            else:
                raise ValueError(f"Estado final desconocido {estado} en línea {linea_actual}")
        else:
            raise ValueError(f"No termina en estado final (estado {estado}) en línea {linea_actual}")
        
        i = j
    
    return resultado