class SymbolEntry:
    """Representa una entrada en la tabla de símbolos"""
    def __init__(self, nombre, tipo, linea_declaracion, scope, id_unico):
        self.nombre = nombre
        self.tipo = tipo  # INT, REAL, BOOL, STRING, CHAR, FUNCTION
        self.linea_declaracion = linea_declaracion
        self.scope = scope  # 0 = global, 1+ = funciones/bloques
        self.id_unico = id_unico  # VAR_001, FUNC_001, etc.
        self.lineas_uso = []  # Lista de líneas donde se usa
        self.has_value = False  # Si la variable ha sido asignada
        
        # Para funciones
        self.es_funcion = False
        self.parametros = []  # Lista de nombres de parámetros
        self.tipo_retorno = None
        
        # Para parámetros de función
        self.es_parametro = False
    
    def agregar_uso(self, linea):
        """Agrega una línea donde se usa este símbolo"""
        if linea not in self.lineas_uso:
            self.lineas_uso.append(linea)
    
    def marcar_asignado(self):
        """Marca que esta variable ha recibido un valor"""
        self.has_value = True
    
    def puede_usarse(self):
        """Verifica si la variable puede usarse (tiene valor o es parámetro)"""
        return self.has_value or self.es_parametro or self.es_funcion
    
    def __repr__(self):
        if self.es_funcion:
            return f"SymbolEntry({self.id_unico}, func={self.nombre}, params={self.parametros}, scope={self.scope}, L{self.linea_declaracion})"
        estado = "✓" if self.has_value else "✗"
        return f"SymbolEntry({self.id_unico}, {self.nombre}:{self.tipo}, val={estado}, scope={self.scope}, L{self.linea_declaracion})"