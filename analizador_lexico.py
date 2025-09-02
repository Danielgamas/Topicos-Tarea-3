import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    tipo: str
    valor: str

# Definimos las expresiones regulares para cada tipo de token
# Los nombres de los tokens se encuentran en español para mostrarlos así en la interfaz
TOKEN_SPEC = [
    ("NUMERO",         r"\d+\.?\d*"),  # Números enteros o decimales
    ("IGUAL",          r"=="),           # Igual
    ("NO_IGUAL",       r"!="),           # Distinto
    ("MAYOR_IGUAL",    r">="),          # Mayor o igual
    ("MENOR_IGUAL",    r"<="),          # Menor o igual
    ("MAYOR_QUE",      r">"),           # Mayor que
    ("MENOR_QUE",      r"<"),           # Menor que
    ("ASIGNACION",     r"="),           # Asignación
    ("OPERADOR",       r"[+\-*/^]"),   # Operadores aritméticos
    ("PAREN_IZQ",      r"\("),         # Paréntesis izquierdo
    ("PAREN_DER",      r"\)"),         # Paréntesis derecho
    ("IDENTIFICADOR",  r"[A-Za-z_]+"),  # Identificadores
    ("ESPACIO",        r"[ \t]+"),     # Espacios en blanco
    ("DESCONOCIDO",    r".")           # Cualquier otro carácter
]

def analizar(cadena: str) -> List[Token]:
    """Analiza la cadena y retorna una lista de tokens."""
    token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
    regex = re.compile(token_regex)
    tokens: List[Token] = []
    for match in regex.finditer(cadena):
        tipo = match.lastgroup
        valor = match.group()
        if tipo == "ESPACIO":
            continue
        if tipo == "DESCONOCIDO":
            raise ValueError(f"Carácter inesperado: {valor}")
        tokens.append(Token(tipo, valor))
    return tokens

if __name__ == "__main__":
    expresion = input("Ingrese la expresión a analizar: ")
    try:
        for tok in analizar(expresion):
            print(f"{tok.valor}\t{tok.tipo}")
    except ValueError as e:
        print(e)
