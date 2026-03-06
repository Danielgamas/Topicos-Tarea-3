"""Interfaz gráfica moderna para la Calculadora de Métodos Numéricos."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import numpy as np
import sympy as sp

from numerical_methods import (
    evaluar_lagrange,
    metodo_gauss_seidel,
    metodo_secante,
    polinomio_lagrange,
)


class NumericMethodsApp(ctk.CTk):
    """Ventana principal con menú y módulos independientes."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Calculadora de Métodos Numéricos")
        self.geometry("1120x760")
        self.minsize(980, 680)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="#141821", corner_radius=14)
        self.container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="⚙️ Calculadora de Métodos Numéricos",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Secante · Gauss-Seidel · Lagrange",
            text_color="#98A3B3",
            font=ctk.CTkFont(size=14),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    def _build_tabs(self) -> None:
        tabs = ctk.CTkTabview(self.container, corner_radius=12)
        tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 18))

        self.tab_secante = tabs.add("Método de la Secante")
        self.tab_gauss = tabs.add("Gauss-Seidel")
        self.tab_lagrange = tabs.add("Interpolación de Lagrange")

        self._build_secante_tab(self.tab_secante)
        self._build_gauss_tab(self.tab_gauss)
        self._build_lagrange_tab(self.tab_lagrange)

    def _build_secante_tab(self, tab: ctk.CTkFrame) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(1, weight=1)

        panel = ctk.CTkFrame(tab, corner_radius=12)
        panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(12, 8), pady=12)
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Parámetros", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8)
        )

        self.func_entry = self._labeled_entry(panel, "f(x)", "x^3 - x - 2", 1)
        self.x0_entry = self._labeled_entry(panel, "x₀", "1", 2)
        self.x1_entry = self._labeled_entry(panel, "x₁", "2", 3)
        self.tol_sec_entry = self._labeled_entry(panel, "Tolerancia", "1e-6", 4)

        ctk.CTkButton(
            panel,
            text="Calcular raíz",
            corner_radius=10,
            height=40,
            command=self.calcular_secante,
        ).grid(row=5, column=0, padx=14, pady=(16, 12), sticky="ew")

        out = ctk.CTkFrame(tab, corner_radius=12)
        out.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(8, 12), pady=12)
        out.grid_rowconfigure(2, weight=1)
        out.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(out, text="Resultado", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 6)
        )

        self.secante_result = ctk.CTkLabel(out, text="Raíz aproximada: -", anchor="w")
        self.secante_result.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))

        self.secante_table = ctk.CTkTextbox(out, wrap="none", corner_radius=8)
        self.secante_table.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 14))

    def _build_gauss_tab(self, tab: ctk.CTkFrame) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        control = ctk.CTkFrame(tab, corner_radius=12)
        control.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 8))

        ctk.CTkLabel(control, text="Tamaño del sistema (n x n):").grid(
            row=0, column=0, padx=(12, 6), pady=12
        )
        self.n_entry = ctk.CTkEntry(control, width=70)
        self.n_entry.insert(0, "3")
        self.n_entry.grid(row=0, column=1, padx=6, pady=12)

        ctk.CTkButton(
            control,
            text="Generar matriz",
            corner_radius=10,
            command=self.generar_matriz,
        ).grid(row=0, column=2, padx=(8, 12), pady=12)

        self.matrix_frame = ctk.CTkFrame(tab, corner_radius=12)
        self.matrix_frame.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(0, 8))

        self.config_frame = ctk.CTkFrame(tab, corner_radius=12)
        self.config_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 8))

        self.gauss_output = ctk.CTkTextbox(tab, corner_radius=10)
        self.gauss_output.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))

        self.a_entries: list[list[ctk.CTkEntry]] = []
        self.b_entries: list[ctk.CTkEntry] = []

        self.generar_matriz()

    def _build_lagrange_tab(self, tab: ctk.CTkFrame) -> None:
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        left = ctk.CTkFrame(tab, corner_radius=12)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(12, 6), pady=12)

        ctk.CTkLabel(left, text="Puntos (x, y)", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(10, 8)
        )

        ctk.CTkLabel(left, text="Cantidad de puntos:").grid(row=1, column=0, padx=(12, 6), pady=8)
        self.points_count = ctk.CTkEntry(left, width=70)
        self.points_count.insert(0, "4")
        self.points_count.grid(row=1, column=1, pady=8)

        ctk.CTkButton(
            left,
            text="Generar campos",
            corner_radius=10,
            command=self.generar_puntos,
        ).grid(row=1, column=2, padx=(8, 12), pady=8)

        self.points_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.points_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))

        right = ctk.CTkFrame(tab, corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=(12, 8))
        right.grid_columnconfigure(0, weight=1)

        self.x_eval_entry = self._labeled_entry(right, "Evaluar en x =", "1.5", 0)
        ctk.CTkButton(
            right,
            text="Interpolar",
            corner_radius=10,
            height=40,
            command=self.calcular_lagrange,
        ).grid(row=1, column=0, padx=12, pady=(6, 12), sticky="ew")

        self.lagrange_output = ctk.CTkTextbox(tab, corner_radius=10)
        self.lagrange_output.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=(0, 12))

        self.point_entries: list[tuple[ctk.CTkEntry, ctk.CTkEntry]] = []
        self.generar_puntos()

    @staticmethod
    def _labeled_entry(
        parent: ctk.CTkFrame,
        label: str,
        default: str,
        row: int,
    ) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label).grid(row=row * 2 - 1, column=0, sticky="w", padx=14)
        entry = ctk.CTkEntry(parent)
        entry.insert(0, default)
        entry.grid(row=row * 2, column=0, sticky="ew", padx=14, pady=(2, 10))
        return entry

    def calcular_secante(self) -> None:
        try:
            resultado = metodo_secante(
                self.func_entry.get().strip(),
                float(self.x0_entry.get()),
                float(self.x1_entry.get()),
                float(self.tol_sec_entry.get()),
            )

            self.secante_result.configure(
                text=f"Raíz aproximada: {resultado.raiz_aproximada:.10f}"
            )

            self.secante_table.delete("1.0", tk.END)
            header = f"{'i':>3} | {'x_prev':>12} | {'x_actual':>12} | {'x_sig':>12} | {'error':>12}\n"
            self.secante_table.insert(tk.END, header)
            self.secante_table.insert(tk.END, "-" * len(header) + "\n")
            for it in resultado.iteraciones:
                self.secante_table.insert(
                    tk.END,
                    f"{it.iteracion:>3} | {it.x_prev:>12.6f} | {it.x_actual:>12.6f} | "
                    f"{it.x_siguiente:>12.6f} | {it.error_abs:>12.6e}\n",
                )
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error en Secante", str(exc))

    def generar_matriz(self) -> None:
        try:
            n = int(self.n_entry.get())
            if n < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Dato inválido", "El tamaño n debe ser un entero >= 2.")
            return

        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        for widget in self.config_frame.winfo_children():
            widget.destroy()

        self.a_entries = []
        self.b_entries = []

        ctk.CTkLabel(self.matrix_frame, text="Matriz A y vector b").grid(
            row=0, column=0, columnspan=n + 2, padx=10, pady=(8, 6)
        )

        for i in range(n):
            fila = []
            for j in range(n):
                e = ctk.CTkEntry(self.matrix_frame, width=60)
                e.grid(row=i + 1, column=j, padx=3, pady=3)
                e.insert(0, "1" if i == j else "0")
                fila.append(e)
            self.a_entries.append(fila)

            ctk.CTkLabel(self.matrix_frame, text="|").grid(row=i + 1, column=n, padx=4)
            b_e = ctk.CTkEntry(self.matrix_frame, width=70)
            b_e.grid(row=i + 1, column=n + 1, padx=3, pady=3)
            b_e.insert(0, "0")
            self.b_entries.append(b_e)

        self.tol_gs_entry = self._labeled_entry(self.config_frame, "Tolerancia", "1e-6", 1)
        self.max_gs_entry = self._labeled_entry(self.config_frame, "Máx. iteraciones", "200", 2)

        ctk.CTkButton(
            self.config_frame,
            text="Resolver sistema",
            corner_radius=10,
            command=self.calcular_gauss,
        ).grid(row=5, column=0, padx=12, pady=(8, 12), sticky="ew")

    def calcular_gauss(self) -> None:
        try:
            n = len(self.a_entries)
            A = np.array(
                [[float(self.a_entries[i][j].get()) for j in range(n)] for i in range(n)],
                dtype=float,
            )
            b = np.array([float(self.b_entries[i].get()) for i in range(n)], dtype=float)
            tol = float(self.tol_gs_entry.get())
            max_iter = int(self.max_gs_entry.get())

            resultado = metodo_gauss_seidel(A, b, tol, max_iter=max_iter)

            self.gauss_output.delete("1.0", tk.END)
            self.gauss_output.insert(
                tk.END,
                f"Convergió en {resultado.iteraciones} iteraciones.\n"
                f"Solución aproximada: {resultado.solucion}\n\n",
            )
            self.gauss_output.insert(tk.END, "Historial:\n")
            for i, vec in enumerate(resultado.historial):
                self.gauss_output.insert(tk.END, f"Iter {i:>3}: {vec}\n")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error en Gauss-Seidel", str(exc))

    def generar_puntos(self) -> None:
        try:
            n = int(self.points_count.get())
            if n < 2:
                raise ValueError
        except ValueError:
            messagebox.showerror("Dato inválido", "Debes ingresar al menos 2 puntos.")
            return

        for widget in self.points_frame.winfo_children():
            widget.destroy()

        self.point_entries = []
        ctk.CTkLabel(self.points_frame, text="x").grid(row=0, column=0, padx=4)
        ctk.CTkLabel(self.points_frame, text="y").grid(row=0, column=1, padx=4)

        for i in range(n):
            ex = ctk.CTkEntry(self.points_frame, width=90)
            ey = ctk.CTkEntry(self.points_frame, width=90)
            ex.grid(row=i + 1, column=0, padx=4, pady=3)
            ey.grid(row=i + 1, column=1, padx=4, pady=3)
            ex.insert(0, str(i))
            ey.insert(0, str(i**2))
            self.point_entries.append((ex, ey))

    def calcular_lagrange(self) -> None:
        try:
            x_vals = [float(ex.get()) for ex, _ in self.point_entries]
            y_vals = [float(ey.get()) for _, ey in self.point_entries]
            x_eval = float(self.x_eval_entry.get())

            polinomio = polinomio_lagrange(x_vals, y_vals)
            y_eval = evaluar_lagrange(x_vals, y_vals, x_eval)

            self.lagrange_output.delete("1.0", tk.END)
            self.lagrange_output.insert(tk.END, "Polinomio de Lagrange:\n")
            self.lagrange_output.insert(tk.END, f"P(x) = {sp.sstr(polinomio)}\n\n")
            self.lagrange_output.insert(tk.END, f"Evaluación:\nP({x_eval}) = {y_eval:.10f}\n")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Error en Lagrange", str(exc))


if __name__ == "__main__":
    app = NumericMethodsApp()
    app.mainloop()
