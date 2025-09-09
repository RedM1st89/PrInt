class Automata:
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

    def tokenizacion(self, texto):
        tokens = []
        estado = self.estado_inicial
        buffer = ""
        token_anterior = None
        i = 0
        n = len(texto)

        #Estos serviran despues para comprobar si el string ingresado no tiene algun caracter no valido
        signos = {'+', '-'}
        operadores = {'+', '-', '*', '/', '='}
        parentesis = {'(', ')'}
				
        while i < n:
            x = texto[i]

            if not (x.isalnum() or x in operadores or x in parentesis):
                    raise ValueError(f"Carácter inválido encontrado: '{x}' en la posición {i}")

            # Procesar operadores y paréntesis
            if x in operadores or x in parentesis:
                if buffer and estado in self.estados_finales:
                    token = 'id' if self._es_id(estado) else 'num'
                    tokens.append(token)
                    token_anterior = token
                    buffer = ""
                    estado = self.estado_inicial

                if x in signos:
                    if token_anterior in (None, 'op', 'par_abierto'):
                        j = i + 1
                        signo = x
                        #Checa si sigue digito
                        if j < n and texto[j].isdigit():
                            num_buffer = signo
                            j += 1
                            while j < n and texto[j].isdigit():
                                num_buffer += texto[j]
                                j += 1
                            x = f"{signo}num"  #Aqui nomas agrega el signo
                            tokens.append((x))
                            token_anterior = x
                            i = j
                            continue
                        else:
                            #Namas es un operador
                            tokens.append((x))
                            token_anterior = 'op'
                            i += 1
                            continue
                    else:
                        tokens.append((x))
                        token_anterior = 'op'
                        i += 1
                        continue
                else:
                    tokens.append((x))
                    token_anterior = 'op' if x in operadores else 'par_abierto' if x == '(' else 'par_cerrado'
                    i += 1
                    continue

            # Procesar letras o dígitos
            tipo = 'char' if x.isalpha() else 'num' if x.isdigit() else None

            if tipo and tipo in self.estados.get(estado, {}):
                estado = self.estados[estado][tipo]
                buffer += x
                i += 1
            else:
                if buffer and estado in self.estados_finales:
                    tokens.append('id' if self._es_id(estado) else 'num')
                    token_anterior = tokens[-1]
                buffer = ""
                estado = self.estado_inicial
                
                i += 1

        if buffer and estado in self.estados_finales:
            tokens.append('id' if self._es_id(estado) else 'num')

        return tokens

    def _es_id(self, estado):
        return estado == 2

    
class Sintac:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pointer = 0

    #Checa que no se ha acabado el recorrido de la secuencia de tokens y sino, recorre
    def token_actual(self):
        return self.tokens[self.pointer] if self.pointer < len(self.tokens) else None

    #Corrobora que el token actual sigue la regla inicial para S
    def es_igual(self, comparado):
        if self.token_actual() == comparado:
            self.pointer += 1
            return True
        return False

    #Comienza a buscar en S 
    def proceso(self):
        if self.S() and self.pointer == len(self.tokens):
            return True
        return False

    #Inicio
    def S(self):
        if self.es_igual('id') and self.es_igual('='):
            return self.E()
        return False

    def E(self):
        if not self.T():
            return False
        return self.E_simbolo()

    #E si sigue un simbolo (no ha terminado)
    def E_simbolo(self):
        while self.token_actual() in ('+', '-'):
            self.pointer += 1
            if not self.T():
                return False
        return True

    def T(self):
        if not self.F():
            return False
        return self.T_simbolo()

    #T si sigue un simbolo (no ha terminado)
    def T_simbolo(self):
        while self.token_actual() in ('*', '/'):
            self.pointer += 1
            if not self.F():
                return False
        return True

    #Punto final de la recursion
    def F(self):
        tok = self.token_actual()
        if tok in ('id', 'num', '-num', '+num'):
            self.pointer += 1
            return True
        elif tok == '(':
            self.pointer += 1
            if not self.E():
                return False
            return self.es_igual(')')
        return False

            
            

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

automata = Automata(transiciones, estados_finales)

#Inicio del programa
while(True):
    t = input("Ingresa texto: ")
    t = t.replace(" ","")

    tokens = automata.tokenizacion(t)

    if not tokens:
        exit(1)

    print("Lexico: ", tokens)

    prueba = Sintac(tokens)

    if prueba.S():
        print("Sintactico: Valido")
    else:
        print("Sintactico: Invalido")