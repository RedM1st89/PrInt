from .SymbolTable import SymbolTable
from .TypeChecker import TypeChecker

class SemanticAnalyzer:
    """Analiza semánticamente el código verificando tipos, scopes y valores"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla = SymbolTable()
        self.type_checker = TypeChecker()
        self.en_declaracion_funcion = False
        self.funcion_actual = None
    
    def current(self):
        """Retorna el token actual"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def peek(self, offset=1):
        """Mira tokens adelante sin avanzar"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self):
        """Avanza al siguiente token"""
        self.pos += 1
        return self.current()
    
    def analizar(self):
        """Análisis semántico completo en dos pasadas"""
        # PASADA 1: Construir tabla de símbolos
        print("  → Pasada 1: Construcción de tabla de símbolos...")
        self.construir_tabla_simbolos()
        
        # PASADA 2: Verificación de tipos
        print("  → Pasada 2: Verificación de tipos y semántica...")
        self.pos = 0  # Reiniciar
        self.verificar_semantica()
        
        return self.tabla
    
    def construir_tabla_simbolos(self):
        """Primera pasada: construye la tabla de símbolos"""
        while self.pos < len(self.tokens):
            token = self.current()
            
            if not token:
                break
            
            # Declaración de variable
            if token.tipo == "DEFINIR":
                self.procesar_declaracion()
            
            # Declaración de función
            elif token.tipo == "FUNCTION":
                self.procesar_funcion()
            
            # Manejo de scopes
            elif token.tipo == "DELIM_LKEY":
                self.tabla.entrar_scope()
                self.advance()
            
            elif token.tipo == "DELIM_RKEY":
                self.tabla.salir_scope()
                self.advance()
            
            else:
                self.advance()
    
    def procesar_declaracion(self):
        """Procesa declaración de variable: DEFINIR ID TIPO"""
        self.advance()  # Saltar DEFINIR
        
        token_id = self.current()
        if not token_id or token_id.tipo != "ID":
            self.advance()
            return
        
        nombre = token_id.lexema
        linea = token_id.linea
        self.advance()
        
        token_tipo = self.current()
        if not token_tipo or token_tipo.tipo not in ["INT", "REAL", "BOOL", "STRING", "CHAR"]:
            self.advance()
            return
        
        tipo = token_tipo.tipo
        self.tabla.agregar_variable(nombre, tipo, linea)
        self.advance()
    
    def procesar_funcion(self):
        """Procesa declaración de función"""
        self.advance()  # Saltar FUNCTION
        
        # Variable de retorno
        token_retorno = self.current()
        if not token_retorno or token_retorno.tipo != "ID":
            return
        var_retorno = token_retorno.lexema
        self.advance()
        
        # EQUAL
        if not self.current() or self.current().tipo != "EQUAL":
            return
        self.advance()
        
        # Nombre de función
        token_nombre = self.current()
        if not token_nombre or token_nombre.tipo != "ID":
            return
        nombre_funcion = token_nombre.lexema
        linea = token_nombre.linea
        self.advance()
        
        # Paréntesis
        if not self.current() or self.current().tipo != "DELIM_LPAREN":
            return
        self.advance()
        
        # Recolectar parámetros
        parametros = []
        while self.current() and self.current().tipo != "DELIM_RPAREN":
            if self.current().tipo == "ID":
                parametros.append(self.current().lexema)
            self.advance()
        
        # Agregar función
        self.tabla.agregar_funcion(nombre_funcion, var_retorno, parametros, linea)
        
        # Avanzar al cuerpo de la función
        if self.current() and self.current().tipo == "DELIM_RPAREN":
            self.advance()
        
        # Entrar al scope de la función
        if self.current() and self.current().tipo == "DELIM_LKEY":
            self.tabla.entrar_scope()
            self.advance()
            
            # Agregar parámetros como variables en el scope de la función
            for param in parametros:
                # Asumimos tipo genérico para parámetros (podrías mejorarlo)
                self.tabla.agregar_variable(param, "INT", linea, es_parametro=True)
    
    def verificar_semantica(self):
        """Segunda pasada: verifica tipos y semántica"""
        while self.pos < len(self.tokens):
            token = self.current()
            
            if not token:
                break
            
            # Asignación
            if token.tipo == "ID" and self.peek() and self.peek().tipo == "EQUAL":
                self.verificar_asignacion()
            
            # IF
            elif token.tipo == "IF":
                self.verificar_if()
            
            # WHILE
            elif token.tipo == "WHILE":
                self.verificar_while()
            
            # FOR
            elif token.tipo == "FOR":
                self.verificar_for()
            
            # SWITCH
            elif token.tipo == "SWITCH":
                self.verificar_switch()
            
            # READ
            elif token.tipo == "READ":
                self.verificar_read()
            
            # WRITE
            elif token.tipo == "WRITE":
                self.verificar_write()
            
            # Manejo de scopes
            elif token.tipo == "DELIM_LKEY":
                self.tabla.entrar_scope()
                self.advance()
            
            elif token.tipo == "DELIM_RKEY":
                self.tabla.salir_scope()
                self.advance()
            
            else:
                self.advance()
    
    def verificar_asignacion(self):
        """Verifica una asignación: ID = Expression"""
        token_id = self.current()
        nombre_var = token_id.lexema
        linea = token_id.linea
        
        # Buscar variable en tabla
        entry = self.tabla.buscar(nombre_var)
        if not entry:
            self.tabla.errores.append(f"Error línea {linea}: Variable '{nombre_var}' no declarada")
            self.advance()
            return
        
        if entry.es_funcion:
            self.tabla.errores.append(f"Error línea {linea}: No se puede asignar valor a función '{nombre_var}'")
            self.advance()
            return
        
        tipo_var = entry.tipo
        
        self.advance()  # Saltar ID
        self.advance()  # Saltar EQUAL
        
        # Evaluar expresión del lado derecho
        tipo_expresion = self.evaluar_expresion()
        
        if tipo_expresion:
            # Verificar compatibilidad de tipos
            self.type_checker.verificar_asignacion(tipo_var, tipo_expresion, linea, self.tabla.errores)
            
            # Marcar variable como asignada
            self.tabla.marcar_asignacion(nombre_var, linea)
    
    def verificar_if(self):
        """Verifica un IF statement"""
        linea = self.current().linea
        self.advance()  # Saltar IF
        
        if self.current() and self.current().tipo == "DELIM_LPAREN":
            self.advance()
            
            # Evaluar condición
            tipo_condicion = self.evaluar_expresion_logica()
            
            if tipo_condicion:
                self.type_checker.verificar_condicion(tipo_condicion, "IF", linea, self.tabla.errores)
    
    def verificar_while(self):
        """Verifica un WHILE loop"""
        linea = self.current().linea
        self.advance()  # Saltar WHILE
        
        if self.current() and self.current().tipo == "DELIM_LPAREN":
            self.advance()
            
            # Evaluar condición
            tipo_condicion = self.evaluar_expresion_logica()
            
            if tipo_condicion:
                self.type_checker.verificar_condicion(tipo_condicion, "WHILE", linea, self.tabla.errores)
    
    def verificar_for(self):
        """Verifica un FOR loop"""
        linea = self.current().linea
        self.advance()  # Saltar FOR
        
        # Variable de control
        if self.current() and self.current().tipo == "ID":
            self.advance()
        
        if self.current() and self.current().tipo == "EQUAL":
            self.advance()
        
        # Valor inicial
        tipo_inicio = None
        if self.current() and self.current().tipo == "DATA_INT":
            tipo_inicio = "INT"
            self.advance()
        
        if self.current() and self.current().tipo == "THROUGH":
            self.advance()
        
        # Valor final
        tipo_fin = None
        if self.current() and self.current().tipo == "DATA_INT":
            tipo_fin = "INT"
            self.advance()
        
        if self.current() and self.current().tipo == "RATE":
            self.advance()
        
        # Paso
        tipo_paso = None
        if self.current() and self.current().tipo == "DATA_INT":
            tipo_paso = "INT"
            self.advance()
        
        if tipo_inicio and tipo_fin and tipo_paso:
            self.type_checker.verificar_for_loop(tipo_inicio, tipo_fin, tipo_paso, linea, self.tabla.errores)
    
    def verificar_switch(self):
        """Verifica un SWITCH statement"""
        linea = self.current().linea
        self.advance()  # Saltar SWITCH
        
        if self.current() and self.current().tipo == "DELIM_LPAREN":
            self.advance()
            
            # La expresión debe ser ID de tipo INT
            if self.current() and self.current().tipo == "ID":
                nombre = self.current().lexema
                entry = self.tabla.buscar(nombre)
                
                if entry:
                    self.tabla.verificar_tiene_valor(nombre, linea)
                    self.type_checker.verificar_switch(entry.tipo, linea, self.tabla.errores)
                
                self.advance()
    
    def verificar_read(self):
        """Verifica un READ statement"""
        linea = self.current().linea
        self.advance()  # Saltar READ
        
        if self.current() and self.current().tipo == "ID":
            nombre = self.current().lexema
            
            # Verificar que variable existe
            entry = self.tabla.buscar(nombre)
            if entry:
                # READ asigna valor a la variable
                self.tabla.marcar_asignacion(nombre, linea)
            
            self.advance()
    
    def verificar_write(self):
        """Verifica un WRITE statement"""
        self.advance()  # Saltar WRITE
        
        # WRITE puede tener múltiples expresiones separadas por comas
        while self.current() and self.current().tipo != "DELIM_LINE":
            if self.current().tipo == "ID":
                nombre = self.current().lexema
                linea = self.current().linea
                
                # Verificar que variable existe y tiene valor
                self.tabla.verificar_tiene_valor(nombre, linea)
                self.advance()
            
            elif self.current().tipo in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
                # Literales son válidos
                self.advance()
            
            elif self.current().tipo == "DELIM_COMMA":
                self.advance()
            
            else:
                self.advance()
    
    def evaluar_expresion(self):
        """Evalúa el tipo de una expresión hasta encontrar delimitador"""
        # Puede ser: literal, variable, función matemática, o expresión compuesta
        token = self.current()
        
        if not token:
            return None
        
        # Literal
        if token.tipo in ["DATA_INT", "DATA_DOUBLE", "DATA_STRING", "TRUE", "FALSE"]:
            tipo = self.type_checker.inferir_tipo_literal(token)
            self.advance()
            
            # Puede haber operador
            if self.current() and self.current().tipo in self.type_checker.ARITHMETIC_OPS:
                op = self.current().tipo
                linea = self.current().linea
                self.advance()
                tipo2 = self.evaluar_expresion()
                
                if tipo2:
                    if op == "PLUS" and self.type_checker.es_string(tipo):
                        return self.type_checker.verificar_concatenacion_string(tipo, tipo2, linea, self.tabla.errores)
                    else:
                        return self.type_checker.verificar_operacion_aritmetica(tipo, tipo2, op, linea, self.tabla.errores)
            
            return tipo
        
        # Variable
        elif token.tipo == "ID":
            nombre = token.lexema
            linea = token.linea
            
            entry = self.tabla.buscar(nombre)
            if entry:
                self.tabla.verificar_tiene_valor(nombre, linea)
                tipo = entry.tipo if not entry.es_funcion else entry.tipo_retorno
                self.advance()
                
                # Puede ser llamada a función
                if self.current() and self.current().tipo == "DELIM_LPAREN":
                    # Es una llamada a función, saltar parámetros
                    self.advance()
                    while self.current() and self.current().tipo != "DELIM_RPAREN":
                        self.advance()
                    if self.current():
                        self.advance()
                    return tipo
                
                # Puede haber operador
                if self.current() and self.current().tipo in self.type_checker.ARITHMETIC_OPS:
                    op = self.current().tipo
                    linea_op = self.current().linea
                    self.advance()
                    tipo2 = self.evaluar_expresion()
                    
                    if tipo2:
                        if op == "PLUS" and self.type_checker.es_string(tipo):
                            return self.type_checker.verificar_concatenacion_string(tipo, tipo2, linea_op, self.tabla.errores)
                        else:
                            return self.type_checker.verificar_operacion_aritmetica(tipo, tipo2, op, linea_op, self.tabla.errores)
                
                return tipo
            else:
                self.advance()
                return None
        
        # Función matemática
        elif token.tipo in self.type_checker.MATH_FUNCTIONS:
            funcion = token.tipo
            linea = token.linea
            self.advance()
            
            if self.current() and self.current().tipo == "DELIM_LPAREN":
                self.advance()
                
                # Evaluar argumento
                tipo_arg = self.evaluar_expresion()
                
                if self.current() and self.current().tipo == "DELIM_RPAREN":
                    self.advance()
                
                if tipo_arg:
                    return self.type_checker.verificar_funcion_matematica(funcion, tipo_arg, linea, self.tabla.errores)
        
        else:
            self.advance()
            return None
    
    def evaluar_expresion_logica(self):
        """Evalúa una expresión lógica (comparaciones y operadores lógicos)"""
        # Primer operando
        tipo1 = self.evaluar_operando_logico()
        
        if not tipo1:
            return None
        
        # Puede haber operador de comparación
        token = self.current()
        if token and token.tipo in self.type_checker.COMPARISON_OPS:
            op = token.tipo
            linea = token.linea
            self.advance()
            
            tipo2 = self.evaluar_operando_logico()
            
            if tipo2:
                return self.type_checker.verificar_operacion_comparacion(tipo1, tipo2, op, linea, self.tabla.errores)
        
        # Puede ser ya booleano
        return tipo1
    
    def evaluar_operando_logico(self):
        """Evalúa un operando en expresión lógica"""
        token = self.current()
        
        if not token:
            return None
        
        # Literal numérico
        if token.tipo in ["DATA_INT", "DATA_DOUBLE"]:
            tipo = self.type_checker.inferir_tipo_literal(token)
            self.advance()
            return tipo
        
        # Variable
        elif token.tipo == "ID":
            nombre = token.lexema
            linea = token.linea
            
            entry = self.tabla.buscar(nombre)
            if entry:
                self.tabla.verificar_tiene_valor(nombre, linea)
                self.advance()
                return entry.tipo
            else:
                self.advance()
                return None
        
        # Booleano literal
        elif token.tipo in ["TRUE", "FALSE"]:
            self.advance()
            return "BOOL"
        
        else:
            self.advance()
            return None