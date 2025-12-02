class TypeChecker:
    """Verifica compatibilidad de tipos en operaciones y expresiones"""
    
    # Tipos numéricos
    NUMERIC_TYPES = {"INT", "REAL"}
    
    # Operadores aritméticos
    ARITHMETIC_OPS = {"PLUS", "MINUS", "MULT", "DIV", "MODULO", "EXP"}
    
    # Operadores de comparación
    COMPARISON_OPS = {"LESS", "MORE", "SAME", "LESS_SAME", "MORE_SAME", "DIFF"}
    
    # Operadores lógicos
    LOGICAL_OPS = {"AND", "OR", "NOT"}
    
    # Funciones matemáticas
    MATH_FUNCTIONS = {"FUN_SQRT", "FUN_ABS", "FUN_LN", "FUN_EXP", 
                     "FUN_SEN", "FUN_COS", "FUN_ATAN", "FUN_TRUNC", 
                     "FUN_ROUND", "FUN_RAND"}
    
    @staticmethod
    def es_numerico(tipo):
        """Verifica si un tipo es numérico"""
        return tipo in TypeChecker.NUMERIC_TYPES
    
    @staticmethod
    def es_booleano(tipo):
        """Verifica si un tipo es booleano"""
        return tipo == "BOOL"
    
    @staticmethod
    def es_string(tipo):
        """Verifica si un tipo es string"""
        return tipo == "STRING"
    
    @staticmethod
    def inferir_tipo_literal(token):
        """Infiere el tipo de un token literal"""
        if token.tipo == "DATA_INT":
            return "INT"
        elif token.tipo == "DATA_DOUBLE":
            return "REAL"
        elif token.tipo == "DATA_STRING":
            return "STRING"
        elif token.tipo in ["TRUE", "FALSE"]:
            return "BOOL"
        return None
    
    @staticmethod
    def tipo_resultado_aritmetico(tipo1, tipo2):
        """
        Determina el tipo resultado de una operación aritmética
        REAL + INT = REAL
        INT + INT = INT
        """
        if not TypeChecker.es_numerico(tipo1) or not TypeChecker.es_numerico(tipo2):
            return None
        
        if tipo1 == "REAL" or tipo2 == "REAL":
            return "REAL"
        return "INT"
    
    @staticmethod
    def verificar_operacion_aritmetica(tipo1, tipo2, operador, linea, errores):
        """Verifica que una operación aritmética sea válida"""
        if not TypeChecker.es_numerico(tipo1):
            errores.append(f"Error línea {linea}: Operador '{operador}' requiere tipo numérico, se encontró '{tipo1}'")
            return None
        
        if not TypeChecker.es_numerico(tipo2):
            errores.append(f"Error línea {linea}: Operador '{operador}' requiere tipo numérico, se encontró '{tipo2}'")
            return None
        
        return TypeChecker.tipo_resultado_aritmetico(tipo1, tipo2)
    
    @staticmethod
    def verificar_operacion_comparacion(tipo1, tipo2, operador, linea, errores):
        """Verifica que una operación de comparación sea válida"""
        # Las comparaciones pueden ser entre tipos compatibles
        if tipo1 != tipo2:
            # Permitir comparación entre INT y REAL
            if TypeChecker.es_numerico(tipo1) and TypeChecker.es_numerico(tipo2):
                return "BOOL"
            
            errores.append(f"Error línea {linea}: Comparación '{operador}' entre tipos incompatibles: '{tipo1}' y '{tipo2}'")
            return None
        
        return "BOOL"
    
    @staticmethod
    def verificar_operacion_logica(tipo1, tipo2, operador, linea, errores):
        """Verifica que una operación lógica sea válida"""
        if operador == "NOT":
            # NOT es unario
            if not TypeChecker.es_booleano(tipo1):
                errores.append(f"Error línea {linea}: Operador 'NOT' requiere tipo BOOL, se encontró '{tipo1}'")
                return None
            return "BOOL"
        
        # AND, OR son binarios
        if not TypeChecker.es_booleano(tipo1):
            errores.append(f"Error línea {linea}: Operador '{operador}' requiere tipo BOOL, se encontró '{tipo1}'")
            return None
        
        if not TypeChecker.es_booleano(tipo2):
            errores.append(f"Error línea {linea}: Operador '{operador}' requiere tipo BOOL, se encontró '{tipo2}'")
            return None
        
        return "BOOL"
    
    @staticmethod
    def verificar_concatenacion_string(tipo1, tipo2, linea, errores):
        """Verifica concatenación de strings con PLUS"""
        if not TypeChecker.es_string(tipo1):
            errores.append(f"Error línea {linea}: Concatenación requiere STRING, se encontró '{tipo1}'")
            return None
        
        if not TypeChecker.es_string(tipo2):
            errores.append(f"Error línea {linea}: Concatenación requiere STRING, se encontró '{tipo2}'")
            return None
        
        return "STRING"
    
    @staticmethod
    def verificar_asignacion(tipo_variable, tipo_valor, linea, errores):
        """Verifica que una asignación sea válida"""
        if tipo_variable == tipo_valor:
            return True
        
        # Permitir asignación de INT a REAL (promoción automática)
        if tipo_variable == "REAL" and tipo_valor == "INT":
            return True
        
        errores.append(f"Error línea {linea}: No se puede asignar tipo '{tipo_valor}' a variable de tipo '{tipo_variable}'")
        return False
    
    @staticmethod
    def verificar_condicion(tipo_condicion, contexto, linea, errores):
        """Verifica que una condición (IF, WHILE) sea booleana"""
        if not TypeChecker.es_booleano(tipo_condicion):
            errores.append(f"Error línea {linea}: Condición de '{contexto}' debe ser BOOL, se encontró '{tipo_condicion}'")
            return False
        return True
    
    @staticmethod
    def verificar_funcion_matematica(funcion, tipo_argumento, linea, errores):
        """Verifica que una función matemática reciba el tipo correcto"""
        if not TypeChecker.es_numerico(tipo_argumento):
            errores.append(f"Error línea {linea}: Función '{funcion}' requiere argumento numérico, se encontró '{tipo_argumento}'")
            return None
        
        # Todas las funciones matemáticas retornan REAL
        return "REAL"
    
    @staticmethod
    def verificar_for_loop(tipo_inicio, tipo_fin, tipo_paso, linea, errores):
        """Verifica que un loop FOR tenga límites enteros"""
        if tipo_inicio != "INT":
            errores.append(f"Error línea {linea}: Valor inicial de FOR debe ser INT, se encontró '{tipo_inicio}'")
            return False
        
        if tipo_fin != "INT":
            errores.append(f"Error línea {linea}: Valor final de FOR debe ser INT, se encontró '{tipo_fin}'")
            return False
        
        if tipo_paso != "INT":
            errores.append(f"Error línea {linea}: Paso de FOR debe ser INT, se encontró '{tipo_paso}'")
            return False
        
        return True
    
    @staticmethod
    def verificar_switch(tipo_expresion, linea, errores):
        """Verifica que SWITCH use una expresión entera"""
        if tipo_expresion != "INT":
            errores.append(f"Error línea {linea}: SWITCH requiere expresión INT, se encontró '{tipo_expresion}'")
            return False
        return True