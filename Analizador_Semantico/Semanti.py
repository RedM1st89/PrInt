class SymbolEntry:
    """Represents an entry in the symbol table"""
    def __init__(self, nombre, tipo, linea_declaracion, scope, id_unico):
        self.nombre = nombre
        self.tipo = tipo  # INT, REAL, BOOL, STRING, CHAR
        self.linea_declaracion = linea_declaracion
        self.scope = scope  # 0 = global, 1+ = nested blocks
        self.id_unico = id_unico  # VAR_001, FUNC_001, etc.
        self.lineas_uso = []  # Lines where it's used
        self.tiene_valor = False  # Has been assigned a value
        
        # For functions
        self.es_funcion = False
        self.parametros = []
        self.tipo_retorno = None
        self.es_parametro = False  # If it's a function parameter
    
    def agregar_uso(self, linea):
        """Add a line where this symbol is used"""
        if linea not in self.lineas_uso:
            self.lineas_uso.append(linea)
    
    def marcar_asignado(self):
        """Mark that this variable has been assigned"""
        self.tiene_valor = True
    
    def puede_usarse(self):
        """Check if variable can be used (has value or is parameter)"""
        return self.tiene_valor or self.es_parametro or self.es_funcion


class SymbolTable:
    """Symbol table for semantic analysis"""
    def __init__(self):
        self.tabla = {}  # Stores all symbols by name
        self.scopes = [{}]  # Stack of scopes (list of dicts)
        self.contador_var = 0
        self.contador_func = 0
        self.errores = []
    
    def scope_actual(self):
        """Get current scope level"""
        return len(self.scopes) - 1
    
    def entrar_scope(self):
        """Enter new scope"""
        self.scopes.append({})
    
    def salir_scope(self):
        """Exit current scope"""
        if len(self.scopes) > 1:
            self.scopes.pop()
    
    def generar_id_variable(self):
        """Generate unique ID for variables"""
        self.contador_var += 1
        return f"VAR_{self.contador_var:03d}"
    
    def generar_id_funcion(self):
        """Generate unique ID for functions"""
        self.contador_func += 1
        return f"FUNC_{self.contador_func:03d}"
    
    def agregar_variable(self, nombre, tipo, linea, es_parametro=False):
        """Add a variable to the symbol table"""
        scope = self.scope_actual()
        
        # Check if already declared in current scope
        if nombre in self.scopes[scope]:
            entry = self.scopes[scope][nombre]
            self.errores.append(
                f"Error línea {linea}: Variable '{nombre}' ya declarada en línea {entry.linea_declaracion}"
            )
            return None
        
        id_unico = self.generar_id_variable()
        entry = SymbolEntry(nombre, tipo, linea, scope, id_unico)
        entry.es_parametro = es_parametro
        
        # Parameters automatically have value
        if es_parametro:
            entry.tiene_valor = True
        
        self.scopes[scope][nombre] = entry
        self.tabla[nombre] = entry  # Also keep in global table for easy lookup
        return entry
    
    def agregar_funcion(self, nombre, tipo_retorno, parametros, linea):
        """Add a function to the symbol table"""
        scope = self.scope_actual()
        
        if nombre in self.scopes[scope]:
            self.errores.append(
                f"Error línea {linea}: Función '{nombre}' ya declarada"
            )
            return None
        
        id_unico = self.generar_id_funcion()
        entry = SymbolEntry(nombre, "FUNCTION", linea, scope, id_unico)
        entry.es_funcion = True
        entry.parametros = parametros
        entry.tipo_retorno = tipo_retorno
        entry.tiene_valor = True  # Functions always "have value"
        
        self.scopes[scope][nombre] = entry
        self.tabla[nombre] = entry
        return entry
    
    def buscar(self, nombre):
        """Search for a symbol in scopes (from inner to outer)"""
        # Search from current scope outward
        for scope in reversed(self.scopes):
            if nombre in scope:
                return scope[nombre]
        return None
    
    def marcar_asignacion(self, nombre, linea):
        """Mark that a variable has been assigned a value"""
        entry = self.buscar(nombre)
        if entry:
            entry.marcar_asignado()
            entry.agregar_uso(linea)
    
    def verificar_tiene_valor(self, nombre, linea):
        """Verify that a variable has a value before using it"""
        entry = self.buscar(nombre)
        if not entry:
            self.errores.append(
                f"Error línea {linea}: Variable '{nombre}' no declarada"
            )
            return False
        
        entry.agregar_uso(linea)
        
        if not entry.puede_usarse():
            self.errores.append(
                f"Error línea {linea}: Variable '{nombre}' usada sin valor asignado"
            )
            return False
        
        return True
    
    def imprimir_tabla(self):
        """Print the symbol table"""
        print("\n" + "="*100)
        print(" TABLA DE SÍMBOLOS ".center(100))
        print("="*100)
        
        variables = [s for s in self.tabla.values() if not s.es_funcion]
        funciones = [s for s in self.tabla.values() if s.es_funcion]
        
        if funciones:
            print("\n--- FUNCIONES ---")
            print(f"{'ID':<12} | {'Nombre':<20} | {'Retorna':<10} | {'Parámetros':<30} | {'Declarada':<12}")
            print("-"*100)
            for func in funciones:
                params_str = ", ".join(func.parametros) if func.parametros else "sin parámetros"
                print(f"{func.id_unico:<12} | {func.nombre:<20} | {func.tipo_retorno or 'void':<10} | {params_str:<30} | L{func.linea_declaracion}")
        
        if variables:
            print("\n--- VARIABLES ---")
            print(f"{'ID':<12} | {'Nombre':<20} | {'Tipo':<10} | {'Scope':<7} | {'Declarada':<12} | {'Valor':<7} | {'Usos'}")
            print("-"*100)
            for var in sorted(variables, key=lambda x: x.linea_declaracion):
                valor_str = "✓" if var.tiene_valor else "✗"
                usos_str = f"L{var.lineas_uso}" if var.lineas_uso else "Sin uso"
                param = " (param)" if var.es_parametro else ""
                print(f"{var.id_unico:<12} | {var.nombre:<20} | {var.tipo:<10} | {var.scope:<7} | L{var.linea_declaracion:<11} | {valor_str:<7} | {usos_str}{param}")
        
        print("="*100 + "\n")
    
    def imprimir_errores(self):
        """Print all semantic errors"""
        if self.errores:
            print("\n" + "!"*100)
            print(" ERRORES SEMÁNTICOS ".center(100))
            print("!"*100)
            for error in self.errores:
                print(f"  • {error}")
            print("!"*100 + "\n")
            return True
        return False


class SemanticAnalyzer:
    """Performs semantic analysis on tokens"""
    
    # Type compatibility rules
    NUMERIC_TYPES = {"INT", "REAL"}
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla = SymbolTable()
    
    def current(self):
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def peek(self, offset=1):
        """Look ahead at token"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def advance(self):
        """Move to next token"""
        self.pos += 1
    
    def analizar(self):
        """Perform complete semantic analysis"""
        print("  → Pasada 1: Construcción de tabla de símbolos...")
        self.construir_tabla_simbolos()
        
        print("  → Pasada 2: Verificación de tipos y uso de variables...")
        self.pos = 0
        self.verificar_semantica()
        
        return self.tabla
    
    def construir_tabla_simbolos(self):
        """Build symbol table (first pass)"""
        while self.pos < len(self.tokens):
            token = self.current()
            if not token:
                break
            
            if token.tipo == "DEFINIR":
                self.procesar_declaracion()
            elif token.tipo == "FUNCTION":
                self.procesar_funcion()
            elif token.tipo == "DELIM_LKEY":
                self.tabla.entrar_scope()
                self.advance()
            elif token.tipo == "DELIM_RKEY":
                self.tabla.salir_scope()
                self.advance()
            else:
                self.advance()
    
    def procesar_declaracion(self):
        """Process variable declaration: DEFINIR ID TIPO"""
        self.advance()  # Skip DEFINIR
        
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
        """Process function declaration"""
        self.advance()  # Skip FUNCTION
        
        token_retorno = self.current()
        if not token_retorno or token_retorno.tipo != "ID":
            return
        var_retorno = token_retorno.lexema
        self.advance()
        
        if not self.current() or self.current().tipo != "EQUAL":
            return
        self.advance()
        
        token_nombre = self.current()
        if not token_nombre or token_nombre.tipo != "ID":
            return
        nombre_funcion = token_nombre.lexema
        linea = token_nombre.linea
        self.advance()
        
        if not self.current() or self.current().tipo != "DELIM_LPAREN":
            return
        self.advance()
        
        parametros = []
        while self.current() and self.current().tipo != "DELIM_RPAREN":
            if self.current().tipo == "ID":
                parametros.append(self.current().lexema)
            self.advance()
        
        self.tabla.agregar_funcion(nombre_funcion, var_retorno, parametros, linea)
        
        if self.current() and self.current().tipo == "DELIM_RPAREN":
            self.advance()
        
        if self.current() and self.current().tipo == "DELIM_LKEY":
            self.tabla.entrar_scope()
            self.advance()
            
            # Add parameters as variables in function scope
            for param in parametros:
                self.tabla.agregar_variable(param, "INT", linea, es_parametro=True)
    
    def verificar_semantica(self):
        """Verify semantics (second pass)"""
        while self.pos < len(self.tokens):
            token = self.current()
            if not token:
                break
            
            if token.tipo == "ID" and self.peek() and self.peek().tipo == "EQUAL":
                self.verificar_asignacion()
            elif token.tipo == "READ":
                self.verificar_read()
            elif token.tipo == "WRITE":
                self.verificar_write()
            elif token.tipo == "IF":
                self.verificar_condicion()
            elif token.tipo == "WHILE":
                self.verificar_condicion()
            elif token.tipo == "DELIM_LKEY":
                self.tabla.entrar_scope()
                self.advance()
            elif token.tipo == "DELIM_RKEY":
                self.tabla.salir_scope()
                self.advance()
            else:
                self.advance()
    
    def verificar_asignacion(self):
        """Verify assignment: ID = expression"""
        token_id = self.current()
        nombre = token_id.lexema
        linea = token_id.linea
        
        entry = self.tabla.buscar(nombre)
        if not entry:
            self.tabla.errores.append(
                f"Error línea {linea}: Variable '{nombre}' no declarada"
            )
            self.advance()
            return
        
        tipo_var = entry.tipo
        self.advance()  # Skip ID
        self.advance()  # Skip EQUAL
        
        tipo_expr = self.evaluar_expresion()
        
        if tipo_expr:
            self.verificar_compatibilidad_tipos(tipo_var, tipo_expr, linea)
            self.tabla.marcar_asignacion(nombre, linea)
    
    def verificar_read(self):
        """Verify READ statement - assigns value to variable"""
        linea = self.current().linea
        self.advance()  # Skip READ
        
        if self.current() and self.current().tipo == "ID":
            nombre = self.current().lexema
            entry = self.tabla.buscar(nombre)
            
            if entry:
                # READ assigns value to variable
                self.tabla.marcar_asignacion(nombre, linea)
            else:
                self.tabla.errores.append(
                    f"Error línea {linea}: Variable '{nombre}' no declarada en READ"
                )
            
            self.advance()
    
    def verificar_write(self):
        """Verify WRITE statement - checks variables have values"""
        self.advance()  # Skip WRITE
        
        while self.current() and self.current().tipo != "DELIM_LINE":
            if self.current().tipo == "ID":
                nombre = self.current().lexema
                linea = self.current().linea
                self.tabla.verificar_tiene_valor(nombre, linea)
            
            self.advance()
    
    def verificar_condicion(self):
        """Verify IF/WHILE condition"""
        linea = self.current().linea
        self.advance()  # Skip IF/WHILE
        
        if self.current() and self.current().tipo == "DELIM_LPAREN":
            self.advance()
            
            # Check that variables in condition exist and have values
            while self.current() and self.current().tipo != "DELIM_RPAREN":
                if self.current().tipo == "ID":
                    nombre = self.current().lexema
                    linea = self.current().linea
                    self.tabla.verificar_tiene_valor(nombre, linea)
                
                self.advance()
    
    def evaluar_expresion(self):
        """Evaluate expression type"""
        token = self.current()
        
        if not token:
            return None
        
        # Literal values
        if token.tipo == "DATA_INT":
            self.advance()
            return "INT"
        elif token.tipo == "DATA_DOUBLE":
            self.advance()
            return "REAL"
        elif token.tipo == "DATA_STRING":
            self.advance()
            return "STRING"
        elif token.tipo in ["TRUE", "FALSE"]:
            self.advance()
            return "BOOL"
        
        # Variable
        elif token.tipo == "ID":
            nombre = token.lexema
            linea = token.linea
            
            entry = self.tabla.buscar(nombre)
            if entry:
                self.tabla.verificar_tiene_valor(nombre, linea)
                self.advance()
                
                # Check for function call
                if self.current() and self.current().tipo == "DELIM_LPAREN":
                    self.skip_until("DELIM_RPAREN")
                    if self.current():
                        self.advance()
                
                return entry.tipo
            else:
                self.advance()
                return None
        
        # Skip expression
        while self.current() and self.current().tipo not in ["DELIM_LINE", "DELIM_RPAREN", "DELIM_COMMA"]:
            self.advance()
        
        return None
    
    def skip_until(self, token_tipo):
        """Skip tokens until finding specific type"""
        while self.current() and self.current().tipo != token_tipo:
            self.advance()
    
    def verificar_compatibilidad_tipos(self, tipo_var, tipo_expr, linea):
        """Check type compatibility"""
        if tipo_var == tipo_expr:
            return True
        
        # Allow INT -> REAL promotion
        if tipo_var == "REAL" and tipo_expr == "INT":
            return True
        
        self.tabla.errores.append(
            f"Error línea {linea}: Incompatibilidad de tipos: no se puede asignar '{tipo_expr}' a '{tipo_var}'"
        )
        return False


def inicia_semantico(tokens):
    """Main function to start semantic analysis"""
    analyzer = SemanticAnalyzer(tokens)
    tabla = analyzer.analizar()
    return tabla, len(tabla.errores) > 0