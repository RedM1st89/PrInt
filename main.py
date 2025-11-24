from Analizador_Lexico.Lexi import inicia_lexico
from pathlib import Path

t = ",".join(inicia_lexico())
from pathlib import Path

folder = "Analizador_Lexico/Resultados"
nombre = "Resultado.txt"

# Create a Path object for the folder
folder_path = Path(folder)

# Create a Path object for the file within the folder
file_path = folder_path / nombre
# Ensure the folder exists (create if it doesn't)
folder_path.mkdir(exist_ok=True)

# Write the content to the file
file_path.write_text(t)

print(f"\n Escrito a '{file_path}'")