import re
from dataclasses import dataclass
from typing import List
import tkinter as tk
from tkinter import ttk, messagebox


@dataclass
class Token:
    tipo: str
    valor: str

# Expresiones regulares para cada tipo de token
TOKEN_SPEC = [
    ("NUMBER",   r"\d+\.?\d*"),
    ("EQ",       r"=="),
    ("NE",       r"!="),
    ("GE",       r">="),
    ("LE",       r"<="),
    ("GT",       r">"),
    ("LT",       r"<"),
    ("ASSIGN",   r"="),
    ("OP",       r"[+\-*/^]"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("IDENT",    r"[A-Za-z_]+"),
    ("SKIP",     r"[ \t]+"),
    ("MISMATCH", r".")
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


def analizar_expresion() -> None:
    """Toma la expresión del cuadro de texto y muestra los tokens."""
    expresion = entrada.get()
    tabla.delete(*tabla.get_children())
    try:
        for tok in analizar(expresion):
            tabla.insert("", tk.END, values=(tok.valor, tok.tipo))
    except ValueError as e:
        messagebox.showerror("Error", str(e))


def limpiar() -> None:
    """Limpia la entrada y la tabla de tokens."""
    entrada.delete(0, tk.END)
    tabla.delete(*tabla.get_children())


# Construcción de la interfaz
raiz = tk.Tk()
raiz.title("ANALIZADOR LEXICO")
raiz.configure(bg="#0093ff")

etiqueta = tk.Label(
    raiz,
    text="INGRESE LA EXPRESIÓN A VALIDAR",
    bg="#0093ff",
    fg="white",
    font=("Arial", 12, "bold"),
)
etiqueta.pack(pady=(10, 5))

entrada = tk.Entry(raiz, width=40)
entrada.pack()

botonera = tk.Frame(raiz, bg="#0093ff")
botonera.pack(pady=5)

btn_analizar = tk.Button(botonera, text="ANALIZAR", bg="#7fff00", command=analizar_expresion)
btn_analizar.pack(side=tk.LEFT, padx=5)

btn_limpiar = tk.Button(botonera, text="LIMPIAR", bg="#7fff00", command=limpiar)
btn_limpiar.pack(side=tk.LEFT, padx=5)

# Tabla para mostrar tokens
columnas = ("Token", "Tipo")
tabla = ttk.Treeview(raiz, columns=columnas, show="headings", height=8)
for col in columnas:
    tabla.heading(col, text=col)
tabla.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

raiz.mainloop()
