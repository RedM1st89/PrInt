from Analizador_Lexico.Lexi import inicia_lexico
from Analizador_Sintactico.Sintac import inicia_sintactico
from Analizador_Semantico.Semanti import inicia_semantico
from pathlib import Path

file = input('Hola! Dime el nombre del archivo que quieres probar:) >>>')
nom = file
file = (f"Codigos/{file}.txt")

print("\n" + "="*90)
print(" COMPILADOR - ANÁLISIS COMPLETO ".center(90))
print("="*90)

# ============= ANÁLISIS LÉXICO =============
print("\n" + "="*90)
print(" FASE 1: ANÁLISIS LÉXICO ".center(90))
print("="*90)

tokens_ricos = inicia_lexico(file)

if not tokens_ricos:
    print("✗ Error en análisis léxico")
    exit(1)

print(f"✓ Tokens generados: {len(tokens_ricos)}")

# Guardar tokens en archivo
t = ",".join([token.tipo for token in tokens_ricos])
folder = "Analizador_Lexico/Resultados"
nombre = f"Res_{nom}.txt"
folder_path = Path(folder)
file_path = folder_path / nombre
folder_path.mkdir(exist_ok=True)
file_path.write_text(t)
print(f"✓ Tokens guardados en '{file_path}'")

# ============= ANÁLISIS SINTÁCTICO =============
print("\n" + "="*90)
print(" FASE 2: ANÁLISIS SINTÁCTICO ".center(90))
print("="*90)

s = inicia_sintactico(tokens_ricos)

if not s:
    print("✗ Error en análisis sintáctico")
    exit(1)

print("✓ Estructura sintáctica válida")

# ============= ANÁLISIS SEMÁNTICO =============
print("\n" + "="*90)
print(" FASE 3: ANÁLISIS SEMÁNTICO ".center(90))
print("="*90)

tabla, tiene_errores = inicia_semantico(tokens_ricos)

tabla.imprimir_tabla()

if tiene_errores:
    tabla.imprimir_errores()
    print("\n✗ Compilación fallida: errores semánticos encontrados")
    exit(1)

# ============= RESULTADO FINAL =============
print("\n" + "="*90)
print(" ✓ COMPILACIÓN EXITOSA ".center(90))
print("="*90)
print(f"  • Tokens procesados: {len(tokens_ricos)}")
print(f"  • Variables declaradas: {tabla.contador_var}")
print(f"  • Funciones declaradas: {tabla.contador_func}")
print(f"  • Errores semánticos: 0")
print("="*90 + "\n")