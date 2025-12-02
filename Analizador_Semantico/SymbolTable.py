class SymbolEntry:
    """Representa una entrada en la tabla de símbolos"""
    def __init__(self, nombre, tipo, linea_declaracion, scope, id_unico):
        self.nombre = nombre
        self.tipo = tipo  # INT, REAL, BOOL, STRING, CHAR, FUNCTION
        self.linea_declaracion = linea_declaracion
        self.scope = scope  # 0 = global, 1+ = funciones/bloques
        self.id_unico = id_unico  # VAR_001, FUNC_001, etc.
        self.lineas_uso = []  # Lista de líneas donde se usa
        
        # Para funciones
        self.es_funcion = False
        self.parametros = []  # Lista de nombres de parámetros
        self.tipo_retorno = None
    
    def agregar_uso(self, linea):
        """Agrega una línea donde se usa este símbolo"""
        if linea not in self.lineas_uso:
            self.lineas_uso.append(linea)
    
    def __repr__(self):
        if self.es_funcion:
            return f"SymbolEntry({self.id_unico}, func={self.nombre}, params={self.parametros}, scope={self.scope}, L{self.linea_declaracion})"
        return f"SymbolEntry({self.id_unico}, {self.nombre}:{self.tipo}, scope={self.scope}, L{self.linea_declaracion}, usos={self.lineas_uso})"


class SymbolTable:
    """Tabla de símbolos para el análisis semántico"""
    def __init__(self):
        self.simbolos = {}  # key: nombre_variable, value: SymbolEntry
        self.contador_var = 0
        self.contador_func = 0
        self.scope_actual = 0
        self.errores = []
    
    def generar_id_variable(self):
        """Genera un ID único para variables"""
        self.contador_var += 1
        return f"VAR_{self.contador_var:03d}"
    
    def generar_id_funcion(self):
        """Genera un ID único para funciones"""
        self.contador_func += 1
        return f"FUNC_{self.contador_func:03d}"
    
    def entrar_scope(self):
        """Incrementa el nivel de scope"""
        self.scope_actual += 1
    
    def salir_scope(self):
        """Decrementa el nivel de scope"""
        if self.scope_actual > 0:
            self.scope_actual -= 1
    
    def agregar_variable(self, nombre, tipo, linea):
        """Agrega una nueva variable a la tabla"""
        # Verificar si ya existe en el scope actual
        if nombre in self.simbolos:
            entry = self.simbolos[nombre]
            if entry.scope == self.scope_actual:
                self.errores.append(f"Error línea {linea}: Variable '{nombre}' ya declarada en línea {entry.linea_declaracion}")
                return None
        
        id_unico = self.generar_id_variable()
        entry = SymbolEntry(nombre, tipo, linea, self.scope_actual, id_unico)
        self.simbolos[nombre] = entry
        return entry
    
    def agregar_funcion(self, nombre, tipo_retorno, parametros, linea):
        """Agrega una nueva función a la tabla"""
        if nombre in self.simbolos:
            self.errores.append(f"Error línea {linea}: Función '{nombre}' ya declarada en línea {self.simbolos[nombre].linea_declaracion}")
            return None
        
        id_unico = self.generar_id_funcion()
        entry = SymbolEntry(nombre, "FUNCTION", linea, self.scope_actual, id_unico)
        entry.es_funcion = True
        entry.parametros = parametros
        entry.tipo_retorno = tipo_retorno
        self.simbolos[nombre] = entry
        return entry
    
    def buscar(self, nombre):
        """Busca un símbolo en la tabla"""
        return self.simbolos.get(nombre, None)
    
    def registrar_uso(self, nombre, linea):
        """Registra el uso de una variable/función"""
        entry = self.buscar(nombre)
        if entry:
            entry.agregar_uso(linea)
            return entry
        else:
            self.errores.append(f"Error línea {linea}: Variable/Función '{nombre}' no declarada")
            return None
    
    def imprimir_tabla(self):
        """Imprime la tabla de símbolos de forma legible"""
        print("\n" + "="*80)
        print("TABLA DE SÍMBOLOS")
        print("="*80)
        
        # Separar variables y funciones
        variables = [s for s in self.simbolos.values() if not s.es_funcion]
        funciones = [s for s in self.simbolos.values() if s.es_funcion]
        
        if funciones:
            print("\n--- FUNCIONES ---")
            for func in funciones:
                params_str = ", ".join(func.parametros) if func.parametros else "sin parámetros"
                print(f"{func.id_unico:10} | {func.nombre:20} | Retorna: {func.tipo_retorno or 'void':8} | Params: ({params_str})")
                print(f"           | Declarada: L{func.linea_declaracion:3} | Usada en: {func.lineas_uso if func.lineas_uso else 'No usada'}")
        
        if variables:
            print("\n--- VARIABLES ---")
            print(f"{'ID':10} | {'Nombre':20} | {'Tipo':8} | {'Scope':5} | {'Declaración':12} | {'Usos'}")
            print("-"*80)
            for var in sorted(variables, key=lambda x: x.linea_declaracion):
                usos_str = f"L{var.lineas_uso}" if var.lineas_uso else "No usada"
                print(f"{var.id_unico:10} | {var.nombre:20} | {var.tipo:8} | {var.scope:5} | L{var.linea_declaracion:11} | {usos_str}")
        
        print("="*80 + "\n")
    
    def imprimir_errores(self):
        """Imprime todos los errores encontrados"""
        if self.errores:
            print("\n" + "!"*80)
            print("ERRORES SEMÁNTICOS")
            print("!"*80)
            for error in self.errores:
                print(f"  {error}")
            print("!"*80 + "\n")
            return True
        return False


class SymbolTableBuilder:
    """Construye la tabla de símbolos a partir de tokens"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla = SymbolTable()
    
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
    
    def construir(self):
        """Construye la tabla de símbolos recorriendo todos los tokens"""
        while self.pos < len(self.tokens):
            token = self.current()
            
            if not token:
                break
            
            # Detectar declaración de variable: DEFINIR ID TIPO
            if token.tipo == "DEFINIR":
                self.procesar_declaracion()
            
            # Detectar declaración de función: FUNCTION ID EQUAL ID DELIM_LPAREN
            elif token.tipo == "FUNCTION":
                self.procesar_funcion()
            
            # Detectar uso de ID (variable o función)
            elif token.tipo == "ID":
                nombre = token.lexema
                linea = token.linea
                self.tabla.registrar_uso(nombre, linea)
                self.advance()
            
            # Manejo de scopes
            elif token.tipo == "DELIM_LKEY":
                self.tabla.entrar_scope()
                self.advance()
            
            elif token.tipo == "DELIM_RKEY":
                self.tabla.salir_scope()
                self.advance()
            
            else:
                self.advance()
        
        return self.tabla
    
    def procesar_declaracion(self):
        """Procesa una declaración de variable: DEFINIR ID TIPO"""
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
        """Procesa una declaración de función: FUNCTION resultado EQUAL nombre (params)"""
        self.advance()  # Saltar FUNCTION
        
        # Primer ID: variable de retorno
        token_retorno = self.current()
        if not token_retorno or token_retorno.tipo != "ID":
            self.advance()
            return
        
        var_retorno = token_retorno.lexema
        self.advance()
        
        # EQUAL
        if not self.current() or self.current().tipo != "EQUAL":
            return
        self.advance()
        
        # Segundo ID: nombre de la función
        token_nombre = self.current()
        if not token_nombre or token_nombre.tipo != "ID":
            self.advance()
            return
        
        nombre_funcion = token_nombre.lexema
        linea = token_nombre.linea
        self.advance()
        
        # Paréntesis y parámetros
        if not self.current() or self.current().tipo != "DELIM_LPAREN":
            return
        self.advance()
        
        # Recolectar parámetros
        parametros = []
        while self.current() and self.current().tipo != "DELIM_RPAREN":
            if self.current().tipo == "ID":
                parametros.append(self.current().lexema)
            self.advance()
        
        # Agregar función a la tabla
        self.tabla.agregar_funcion(nombre_funcion, var_retorno, parametros, linea)
        
        # La variable de retorno también debe estar en la tabla
        # (se declarará dentro de la función típicamente)


def construir_tabla_simbolos(tokens):
    """Función principal para construir la tabla de símbolos"""
    builder = SymbolTableBuilder(tokens)
    tabla = builder.construir()
    return tabla