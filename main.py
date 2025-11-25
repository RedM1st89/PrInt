from Analizador_Lexico.Lexi import inicia_lexico
from Analizador_Sintactico.Sintac import inicia_sintactico
from pathlib import Path

file = input('Hola! Dime el nombre del archivo que quieres probar:) >>>')
nom = file
file = (f"Codigos/{file}.txt")

t = ",".join(inicia_lexico(file))
from pathlib import Path

folder = "Analizador_Lexico/Resultados"
nombre = f"Res_{nom}.txt"

folder_path = Path(folder)

file_path = folder_path / nombre

folder_path.mkdir(exist_ok=True)

file_path.write_text(t)

print(f"\n Escrito a '{file_path}'")

s = inicia_sintactico(t)

print(f"\n Análisis Sintáctico: {':)' if s else 'D:'}")

if not s:
    exit(1)

print("\n Compilacion hecha :3")