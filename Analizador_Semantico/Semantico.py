from .SemanticAnalyzer import SemanticAnalyzer

def inicia_semantico(tokens):
    """
    Función principal para iniciar el análisis semántico
    
    Args:
        tokens: Lista de objetos Token del análisis léxico
    
    Returns:
        tuple: (tabla_simbolos, tiene_errores)
    """
    analyzer = SemanticAnalyzer(tokens)
    tabla = analyzer.analizar()
    
    return tabla, len(tabla.errores) > 0