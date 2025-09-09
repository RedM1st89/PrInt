import re
#Usando regex encontramos los comentarios y los borramos
def remueve_comentarios(input: str) -> str:
    #Reemplaza los comentarios de una sola palabra que usan el menos con vacio
    text = re.sub(r"-(el|la|los|las|al|a|lo|le|les|un|una|unos|unas)\b", "", input)
    #Reemplaza los comentarios entre lineas que usan el /* y cierran con */
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    #Reemplaza los comentarios de una sola linea que usan unicamente el /
    text = re.sub(r"^.*?/\*.*$", "", text, flags=re.M)

    return text

def limpia(input: str) -> str:
    #Remueve comentarios
    text = remueve_comentarios(input)
    #Remueve espacios
    text = ''.join(ch for ch in text if not ch.isspace())
    return text