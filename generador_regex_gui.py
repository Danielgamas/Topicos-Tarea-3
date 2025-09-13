import tkinter as tk
from tkinter import ttk, messagebox


def escape_regex(token: str) -> str:
    """Escape special regex characters in token."""
    special_chars = ".^$*+?{}[]\\|()"
    return "".join("\\" + ch if ch in special_chars else ch for ch in token)


def generar_regex():
    simbolos = entrada_simbolos.get().strip()
    if not simbolos:
        messagebox.showerror("Error", "Ingrese símbolos separados por comas.")
        return
    tokens = [s.strip() for s in simbolos.split(",") if s.strip()]
    if not tokens:
        messagebox.showerror("Error", "No se detectaron símbolos.")
        return
    grupo = "(" + "|".join(map(escape_regex, tokens)) + ")"
    cuantificador = var_cuantificador.get()
    regex = grupo + cuantificador
    var_salida.set(regex)


root = tk.Tk()
root.title("Generador de Expresión Regular")

marco = ttk.Frame(root, padding=10)
marco.grid(row=0, column=0)

# Entrada de símbolos
etq_simbolos = ttk.Label(marco, text="Símbolos (separados por comas):")
etq_simbolos.grid(row=0, column=0, sticky=tk.W)

entrada_simbolos = ttk.Entry(marco, width=40)
entrada_simbolos.grid(row=1, column=0, sticky=tk.W)

# Selección de cuantificador
etq_cuantificador = ttk.Label(marco, text="Cuantificador:")
etq_cuantificador.grid(row=2, column=0, sticky=tk.W)

var_cuantificador = tk.StringVar(value="")
combo_cuantificador = ttk.Combobox(
    marco, textvariable=var_cuantificador, state="readonly", width=5
)
combo_cuantificador['values'] = ("", "?", "*", "+")
combo_cuantificador.grid(row=3, column=0, sticky=tk.W)
combo_cuantificador.current(0)

# Botón generar
btn_generar = ttk.Button(marco, text="Generar", command=generar_regex)
btn_generar.grid(row=4, column=0, pady=5, sticky=tk.W)

# Salida
etq_salida = ttk.Label(marco, text="Expresión regular:")
etq_salida.grid(row=5, column=0, sticky=tk.W)

var_salida = tk.StringVar()
entrada_salida = ttk.Entry(marco, textvariable=var_salida, width=40, state="readonly")
entrada_salida.grid(row=6, column=0, sticky=tk.W)

root.mainloop()
