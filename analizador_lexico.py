import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    tipo: str
    valor: str

# Definimos las expresiones regulares para cada tipo de token
TOKEN_SPEC = [
    ("NUMBER",   r"\d+\.?\d*"),      # Números enteros o decimales
    ("EQ",       r"=="),              # Igualdad
    ("NE",       r"!="),             # Distinto
    ("GE",       r">="),             # Mayor o igual
    ("LE",       r"<="),             # Menor o igual
    ("GT",       r">"),              # Mayor que
    ("LT",       r"<"),              # Menor que
    ("ASSIGN",   r"="),              # Asignación
    ("OP",       r"[+\-*/^]"),      # Operadores aritméticos
    ("LPAREN",   r"\("),            # Paréntesis izquierdo
    ("RPAREN",   r"\)"),            # Paréntesis derecho
    ("IDENT",    r"[A-Za-z_]+"),     # Variables
    ("SKIP",     r"[ \t]+"),        # Espacios en blanco
    ("MISMATCH", r".")               # Cualquier otro carácter
]

def analizar(cadena: str) -> List[Token]:
    """Analiza la cadena y retorna una lista de tokens."""
    token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
    regex = re.compile(token_regex)
    tokens: List[Token] = []
    for match in regex.finditer(cadena):
        tipo = match.lastgroup
        valor = match.group()
        if tipo == "SKIP":
            continue
        if tipo == "MISMATCH":
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
