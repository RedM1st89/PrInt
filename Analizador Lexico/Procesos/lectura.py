#Inspirado por el trabajo de Abraham Salvidar
def lectura(input: str) -> str:
    try:
        with open(input, "r", encoding="utf-8") as t:
            resultado = t.read()
    except FileNotFoundError:
        print(f"Directorio equivocado: {input}")
        raise
    return resultado