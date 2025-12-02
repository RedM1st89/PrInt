class SymbolEntry:
    """Represents an entry in the symbol table"""
    def __init__(self, nombre, tipo, linea_declaracion, scope, id_unico):
        self.nombre = nombre
        self.tipo = tipo  # INT, REAL, BOOL, STRING, CHAR
        self.linea_declaracion = linea_declaracion
        self.scope = scope  # 0 = global/class, 1+ = functions
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
        self.tabla = {}  # Stores all symbols by unique key (name + scope)
        self.scope_actual_num = 0  # Current scope: 0 = class, 1+ = functions
        self.contador_var = 0
        self.contador_func = 0
        self.errores = []
    
    def generar_id_variable(self):
        """Generate unique ID for variables"""
        self.contador_var += 1
        return f"VAR_{self.contador_var:03d}"
    
    def generar_id_funcion(self):
        """Generate unique ID for functions"""
        self.contador_func += 1
        return f"FUNC_{self.contador_func:03d}"
    
    def _generar_clave(self, nombre, scope):
        """Generate unique key for symbol lookup"""
        return f"{nombre}@{scope}"
    
    def agregar_variable(self, nombre, tipo, linea, es_parametro=False):
        """Add a variable to the symbol table"""
        clave = self._generar_clave(nombre, self.scope_actual_num)
        
        # Check if already declared in current scope
        if clave in self.tabla:
            entry = self.tabla[clave]
            self.errores.append(
                f"Error línea {linea}: Variable '{nombre}' ya declarada en línea {entry.linea_declaracion}"
            )
            return None
        
        id_unico = self.generar_id_variable()
        entry = SymbolEntry(nombre, tipo, linea, self.scope_actual_num, id_unico)
        entry.es_parametro = es_parametro
        
        # Parameters automatically have value
        if es_parametro:
            entry.tiene_valor = True
        
        self.tabla[clave] = entry
        return entry
    
    def agregar_funcion(self, nombre, tipo_retorno, parametros, linea):
        """Add a function to the symbol table (always in global scope)"""
        clave = self._generar_clave(nombre, 0)  # Functions always in scope 0
        
        if clave in self.tabla:
            self.errores.append(
                f"Error línea {linea}: Función '{nombre}' ya declarada"
            )
            return None
        
        id_unico = self.generar_id_funcion()
        entry = SymbolEntry(nombre, "FUNCTION", linea, 0, id_unico)
        entry.es_funcion = True
        entry.parametros = parametros
        entry.tipo_retorno = tipo_retorno
        entry.tiene_valor = True  # Functions always "have value"
        
        self.tabla[clave] = entry
        return entry
    
    def buscar(self, nombre):
        """Search for a symbol (current scope first, then global)"""
        # First try current scope
        clave_actual = self._generar_clave(nombre, self.scope_actual_num)
        if clave_actual in self.tabla:
            return self.tabla[clave_actual]
        
        # If not in current scope and we're in a function, try global scope
        if self.scope_actual_num > 0:
            clave_global = self._generar_clave(nombre, 0)
            if clave_global in self.tabla:
                return self.tabla[clave_global]
        
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
        print("  → Análisis semántico en progreso...")
        
        # Single pass: process declarations and usage together
        while self.pos < len(self.tokens):
            token = self.current()
            if not token:
                break
            
            if token.tipo == "DEFINIR":
                self.procesar_declaracion()
            elif token.tipo == "FUNCTION":
                self.procesar_funcion()
            elif token.tipo == "ID" and self.peek() and self.peek().tipo == "EQUAL":
                self.verificar_asignacion()
            elif token.tipo == "READ":
                self.verificar_read()
            elif token.tipo == "WRITE":
                self.verificar_write()
            elif token.tipo == "IF":
                self.verificar_condicion()
            elif token.tipo == "WHILE":
                self.verificar_condicion()
            else:
                self.advance()
        
        return self.tabla
    
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
            # Enter function scope
            self.tabla.scope_actual_num += 1
            self.advance()
            
            # Add parameters as variables in function scope
            for param in parametros:
                self.tabla.agregar_variable(param, "INT", linea, es_parametro=True)
            
            # Process function body until we find END_FUNCTION
            depth = 1
            while self.current() and depth > 0:
                token = self.current()
                
                if token.tipo == "DELIM_LKEY":
                    depth += 1
                    self.advance()
                elif token.tipo == "DELIM_RKEY":
                    depth -= 1
                    if depth == 0:
                        # Exiting function scope
                        self.tabla.scope_actual_num -= 1
                    self.advance()
                elif token.tipo == "DEFINIR":
                    self.procesar_declaracion()
                elif token.tipo == "ID" and self.peek() and self.peek().tipo == "EQUAL":
                    self.verificar_asignacion()
                elif token.tipo == "READ":
                    self.verificar_read()
                elif token.tipo == "WRITE":
                    self.verificar_write()
                elif token.tipo == "IF":
                    self.verificar_condicion()
                elif token.tipo == "WHILE":
                    self.verificar_condicion()
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
            # Skip to end of statement
            while self.current() and self.current().tipo != "DELIM_LINE":
                self.advance()
            if self.current():
                self.advance()
            return
        
        self.advance()  # Skip ID
        self.advance()  # Skip EQUAL
        
        # Check all IDs in the expression
        while self.current() and self.current().tipo != "DELIM_LINE":
            if self.current().tipo == "ID":
                expr_nombre = self.current().lexema
                expr_linea = self.current().linea
                self.tabla.verificar_tiene_valor(expr_nombre, expr_linea)
            self.advance()
        
        # Mark assignment after evaluating expression
        self.tabla.marcar_asignacion(nombre, linea)
        
        if self.current() and self.current().tipo == "DELIM_LINE":
            self.advance()
    
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
        
        # Skip to end of statement
        while self.current() and self.current().tipo != "DELIM_LINE":
            self.advance()
        if self.current():
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
        
        if self.current() and self.current().tipo == "DELIM_LINE":
            self.advance()
    
    def verificar_condicion(self):
        """Verify IF/WHILE condition"""
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
            
            if self.current() and self.current().tipo == "DELIM_RPAREN":
                self.advance()


def inicia_semantico(tokens):
    """Main function to start semantic analysis"""
    analyzer = SemanticAnalyzer(tokens)
    tabla = analyzer.analizar()
    return tabla, len(tabla.errores) > 0