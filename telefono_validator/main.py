"""Aplicación gráfica para validar números telefónicos."""

from __future__ import annotations

import re
import tkinter as tk
from tkinter import ttk


PATTERN = re.compile(
    r"""
    ^
    (?P<area>
        (?:\(\d{3}\))  # Código de área entre paréntesis
        |
        \d{3}            # o solo 3 dígitos
    )
    (?P<sep1>[\s.-]?)    # Separador opcional
    (?P<central>\d{3})   # Siguientes 3 dígitos
    (?P<sep2>[\s.-]?)    # Segundo separador opcional
    (?P<linea>\d{4})     # Últimos 4 dígitos
    $
    """,
    re.VERBOSE,
)


class PhoneValidatorApp(ttk.Frame):
    """Interfaz principal para validar números telefónicos."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=20)
        self.master.title("Validador de números telefónicos")
        self.master.geometry("960x620")
        self.master.configure(background="#1f2430")
        self.pack(fill="both", expand=True)

        self.style = ttk.Style()
        self._configure_styles()
        self._build_layout()

    # ------------------------------------------------------------------
    def _configure_styles(self) -> None:
        """Configura estilos modernos para la interfaz."""
        self.style.theme_use("clam")
        self.style.configure("Card.TLabelframe", background="#2b3040", foreground="#f0f3ff")
        self.style.configure("Card.TLabelframe.Label", foreground="#8bd5ff", font=("Segoe UI", 13, "bold"))
        self.style.configure("Main.TFrame", background="#1f2430")
        self.style.configure("Title.TLabel", background="#1f2430", foreground="#f0f3ff", font=("Segoe UI", 22, "bold"))
        self.style.configure("Subtitle.TLabel", background="#1f2430", foreground="#c8d3f5", font=("Segoe UI", 12))
        self.style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)
        self.style.configure("TLabel", background="#2b3040", foreground="#f0f3ff", font=("Segoe UI", 11))
        self.style.configure("Status.TLabel", background="#2b3040", font=("Segoe UI", 14, "bold"))
        self.style.configure("Treeview", background="#1f2430", foreground="#f0f3ff", fieldbackground="#1f2430")
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground="#8bd5ff")

    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        """Crea la estructura principal de la interfaz."""
        container = ttk.Frame(self, style="Main.TFrame")
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Validador de números telefónicos", style="Title.TLabel")
        title.pack(anchor="w")

        subtitle = ttk.Label(
            container,
            text=(
                "Verifica números según un autómata inspirado en el formato estadounidense: "
                "código de área opcional entre paréntesis, separadores con espacio, punto o guion, "
                "y bloques 3-3-4 de dígitos."
            ),
            style="Subtitle.TLabel",
            wraplength=860,
            justify="left",
        )
        subtitle.pack(anchor="w", pady=(0, 16))

        input_frame = ttk.Labelframe(container, text="Entrada", style="Card.TLabelframe")
        input_frame.pack(fill="x", pady=(0, 16))

        ttk.Label(input_frame, text="Número a validar:").grid(row=0, column=0, sticky="w", padx=(12, 6), pady=12)
        self.number_var = tk.StringVar()
        self.entry = ttk.Entry(input_frame, textvariable=self.number_var, font=("Consolas", 14))
        self.entry.grid(row=0, column=1, sticky="ew", padx=6, pady=12)
        self.entry.focus()
        input_frame.columnconfigure(1, weight=1)

        button_frame = ttk.Frame(input_frame, style="Main.TFrame")
        button_frame.grid(row=0, column=2, padx=(6, 12), pady=12)
        validate_btn = ttk.Button(button_frame, text="Validar", command=self.validate_number)
        validate_btn.pack(side="top", fill="x")
        reset_btn = ttk.Button(button_frame, text="Limpiar", command=self.reset_form)
        reset_btn.pack(side="top", fill="x", pady=(8, 0))

        info_frame = ttk.Frame(container, style="Main.TFrame")
        info_frame.pack(fill="both", expand=True)
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)

        self.status_card = ttk.Labelframe(info_frame, text="Resultado", style="Card.TLabelframe")
        self.status_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.status_canvas = tk.Canvas(self.status_card, width=36, height=36, bg="#2b3040", highlightthickness=0)
        self.status_canvas.grid(row=0, column=0, padx=16, pady=16)
        self.status_label = ttk.Label(self.status_card, text="Esperando entrada", style="Status.TLabel")
        self.status_label.grid(row=0, column=1, sticky="w")

        detail_frame = ttk.Labelframe(info_frame, text="Desglose del autómata", style="Card.TLabelframe")
        detail_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.tree = ttk.Treeview(
            detail_frame,
            columns=("state", "input", "description"),
            show="headings",
            selectmode="none",
            height=10,
        )
        self.tree.heading("state", text="Estado")
        self.tree.heading("input", text="Entrada")
        self.tree.heading("description", text="Descripción")
        self.tree.column("state", width=110, anchor="center")
        self.tree.column("input", width=140, anchor="center")
        self.tree.column("description", anchor="w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)

        formats = ttk.Labelframe(container, text="Formatos aceptados", style="Card.TLabelframe")
        formats.pack(fill="x", pady=(16, 0))
        formats.columnconfigure(0, weight=1)
        accepted_formats = (
            "1234567890",
            "123 456 7890",
            "123-456-7890",
            "123.456.7890",
            "(123)456-7890",
            "(123) 456 7890",
            "(123)4567890",
        )
        format_list = tk.Text(
            formats,
            height=len(accepted_formats) + 2,
            bg="#1f2430",
            fg="#f0f3ff",
            relief="flat",
            font=("Consolas", 12),
            highlightthickness=0,
            wrap="word",
        )
        format_list.insert("end", "\n".join(accepted_formats))
        format_list.configure(state="disabled")
        format_list.grid(row=0, column=0, sticky="ew", padx=12, pady=12)

    # ------------------------------------------------------------------
    def reset_form(self) -> None:
        """Restablece el formulario y limpia los resultados."""
        self.number_var.set("")
        self.entry.focus()
        self.status_label.configure(text="Esperando entrada", foreground="#f0f3ff")
        self._draw_status_circle("#4b556a")
        for row in self.tree.get_children():
            self.tree.delete(row)

    # ------------------------------------------------------------------
    def validate_number(self) -> None:
        """Valida el número y actualiza la interfaz con los resultados."""
        number = self.number_var.get().strip()
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not number:
            self.status_label.configure(text="Ingresa un número", foreground="#ffdd57")
            self._draw_status_circle("#ffdd57")
            return

        match = PATTERN.fullmatch(number)
        if match:
            self._render_success(number, match)
        else:
            self._render_error(number)

    # ------------------------------------------------------------------
    def _render_success(self, number: str, match: re.Match[str]) -> None:
        """Muestra la información cuando el número es válido."""
        area = match.group("area").strip("()")
        sep1 = match.group("sep1") or "(sin separador)"
        sep2 = match.group("sep2") or "(sin separador)"
        central = match.group("central")
        linea = match.group("linea")

        self.status_label.configure(
            text=f"Número válido: +1 ({area}) {central}-{linea}",
            foreground="#a3f7bf",
        )
        self._draw_status_circle("#32d296")

        steps = self._build_automaton_steps(number, area, sep1, central, sep2, linea)
        for step in steps:
            self.tree.insert("", "end", values=(step["state"], step["input"], step["description"]))

    # ------------------------------------------------------------------
    def _render_error(self, number: str) -> None:
        """Muestra información detallada cuando el número es inválido."""
        self.status_label.configure(
            text="Formato inválido. Revisa los separadores y la cantidad de dígitos.",
            foreground="#ff6b6b",
        )
        self._draw_status_circle("#ff6b6b")

        observed = self._inspect_number(number)
        for step in observed:
            self.tree.insert("", "end", values=(step["state"], step["input"], step["description"]))

    # ------------------------------------------------------------------
    def _draw_status_circle(self, color: str) -> None:
        """Dibuja un círculo de estado con el color proporcionado."""
        self.status_canvas.delete("all")
        self.status_canvas.create_oval(4, 4, 32, 32, fill=color, outline="")

    # ------------------------------------------------------------------
    def _build_automaton_steps(
        self,
        original: str,
        area: str,
        sep1: str,
        central: str,
        sep2: str,
        linea: str,
    ) -> list[dict[str, str]]:
        """Crea un desglose paso a paso del autómata para un número válido."""
        sep1_display = sep1 if sep1 != "(sin separador)" else "—"
        sep2_display = sep2 if sep2 != "(sin separador)" else "—"
        formatted = [
            {"state": "q0", "input": original, "description": "Inicio: cadena completa"},
            {
                "state": "q1",
                "input": area,
                "description": "Se lee el código de área (3 dígitos).",
            },
            {
                "state": "q2",
                "input": sep1_display,
                "description": "Separador opcional después del área.",
            },
            {
                "state": "q3",
                "input": central,
                "description": "Se consumen los 3 dígitos centrales.",
            },
            {
                "state": "q4",
                "input": sep2_display,
                "description": "Segundo separador opcional.",
            },
            {
                "state": "q5",
                "input": linea,
                "description": "Se leen los 4 dígitos finales.",
            },
            {"state": "qf", "input": "—", "description": "Estado de aceptación."},
        ]
        return formatted

    # ------------------------------------------------------------------
    def _inspect_number(self, number: str) -> list[dict[str, str]]:
        """Analiza un número inválido y devuelve observaciones."""
        observations: list[dict[str, str]] = []
        digit_count = sum(ch.isdigit() for ch in number)
        separators = [ch for ch in number if ch in " -." or ch in "()-"]

        observations.append(
            {
                "state": "q0",
                "input": number,
                "description": "Cadena recibida para analizar.",
            }
        )
        observations.append(
            {
                "state": "Σ",
                "input": str(digit_count),
                "description": "Cantidad de dígitos detectados (se esperan exactamente 10).",
            }
        )

        if digit_count != 10:
            observations.append(
                {
                    "state": "error",
                    "input": "dígitos",
                    "description": "El autómata rechaza porque no hay exactamente 10 dígitos.",
                }
            )

        if not all(ch.isdigit() or ch in " ()-." for ch in number):
            observations.append(
                {
                    "state": "error",
                    "input": "caracter",
                    "description": "Se encontraron caracteres no permitidos.",
                }
            )

        if number.count("(") != number.count(")"):
            observations.append(
                {
                    "state": "error",
                    "input": "paréntesis",
                    "description": "Uso inconsistente de paréntesis en el código de área.",
                }
            )

        if separators:
            observations.append(
                {
                    "state": "Σ",
                    "input": "".join(separators),
                    "description": "Separadores presentes. Deben ser espacios, puntos o guiones.",
                }
            )

        if len(observations) == 2:
            observations.append(
                {
                    "state": "error",
                    "input": "estructura",
                    "description": "Revisa la posición de los bloques (formato 3-3-4).",
                }
            )

        observations.append(
            {
                "state": "qf",
                "input": "—",
                "description": "El autómata termina en estado de rechazo.",
            }
        )
        return observations


def main() -> None:
    root = tk.Tk()
    PhoneValidatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
