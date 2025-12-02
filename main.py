from Analizador_Lexico.Lexi import inicia_lexico
from Analizador_Sintactico.Sintac import inicia_sintactico
from Analizador_Semantico.Semanti import inicia_semantico
from pathlib import Path

file = input('Hola! Dime el nombre del archivo que quieres probar:) >>>')
nom = file
file = (f"Codigos/{file}.txt")

print("\n")

# Lexico
print(" Lexi ".center(90))
tokens = inicia_lexico(file)

if not tokens:
    print("Lexico todo mal")
    exit(1)

print(f" Tokens: {len(tokens)}")

# Tokens en res
t = ",".join([token.tipo for token in tokens])
folder = "Analizador_Lexico/Resultados"
nombre = f"Res_{nom}.txt"
folder_path = Path(folder)
file_path = folder_path / nombre
folder_path.mkdir(exist_ok=True)
file_path.write_text(t)
print(f" Tokens escritos en: '{file_path}'")

# Sintactico
print("\n")
print(" Sintac ".center(90))
print("\n")

s = inicia_sintactico(tokens)

if not s:
    print("Sintactico todo mal")
    exit(1)

print("Sintactico todo bien")

# Semantico
print("\n")
print(" Semantico ".center(90))
print("\n")

tabla, tiene_errores = inicia_semantico(tokens)

tabla.imprimir_tabla()

if tiene_errores:
    tabla.imprimir_errores()
    print("\n Semantico todo mal")
    exit(1)

print("Ta bien perro ")