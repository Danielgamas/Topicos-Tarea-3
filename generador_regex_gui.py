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


def limpiar():
    """Limpiar todos los campos de la interfaz."""
    entrada_simbolos.delete(0, tk.END)
    var_cuantificador.set("")
    var_salida.set("")


root = tk.Tk()
root.title("Generador de Expresión Regular")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 11))
style.configure("TButton", font=("Segoe UI", 11))
style.configure("TEntry", font=("Segoe UI", 11))

marco = ttk.Frame(root, padding=20)
marco.grid(row=0, column=0, sticky="nsew")
marco.columnconfigure(0, weight=1)

# Entrada de símbolos
etq_simbolos = ttk.Label(marco, text="Símbolos (separados por comas):")
etq_simbolos.grid(row=0, column=0, sticky=tk.W)

entrada_simbolos = ttk.Entry(marco, width=40)
entrada_simbolos.grid(row=1, column=0, pady=(0, 10), sticky="ew")

# Selección de cuantificador
etq_cuantificador = ttk.Label(marco, text="Cuantificador:")
etq_cuantificador.grid(row=2, column=0, sticky=tk.W)

var_cuantificador = tk.StringVar(value="")
combo_cuantificador = ttk.Combobox(
    marco, textvariable=var_cuantificador, state="readonly", width=5
)
combo_cuantificador["values"] = ("", "?", "*", "+")
combo_cuantificador.grid(row=3, column=0, pady=(0, 10), sticky=tk.W)
combo_cuantificador.current(0)

# Botones
frame_botones = ttk.Frame(marco)
frame_botones.grid(row=4, column=0, pady=(0, 10), sticky=tk.W)

btn_generar = ttk.Button(frame_botones, text="Generar", command=generar_regex)
btn_generar.grid(row=0, column=0, padx=(0, 5))

btn_limpiar = ttk.Button(frame_botones, text="Limpiar", command=limpiar)
btn_limpiar.grid(row=0, column=1)

# Salida
etq_salida = ttk.Label(marco, text="Expresión regular:")
etq_salida.grid(row=5, column=0, sticky=tk.W)

var_salida = tk.StringVar()
entrada_salida = ttk.Entry(marco, textvariable=var_salida, width=40, state="readonly")
entrada_salida.grid(row=6, column=0, sticky="ew")

root.mainloop()
