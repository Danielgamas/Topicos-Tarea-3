"""Aplicación de escritorio para validar códigos postales de varios países.

Esta interfaz gráfica está inspirada en el ejemplo proporcionado y permite validar
entradas según el formato oficial de Canadá, México, Estados Unidos, Francia y España.
"""
from __future__ import annotations

import re
import tkinter as tk
from dataclasses import dataclass
from typing import Pattern
from tkinter import ttk, messagebox, filedialog


@dataclass(frozen=True)
class PostalCodeFormat:
    """Describe un formato de código postal con su regex y ejemplos."""

    country: str
    regex: str
    description: str
    examples: tuple[str, ...]
    pattern: Pattern[str]

    @classmethod
    def create(
        cls,
        *,
        country: str,
        regex: str,
        description: str,
        examples: tuple[str, ...],
    ) -> "PostalCodeFormat":
        return cls(
            country=country,
            regex=regex,
            description=description,
            examples=examples,
            pattern=re.compile(regex),
        )


POSTAL_CODE_FORMATS: dict[str, PostalCodeFormat] = {
    "Canadá": PostalCodeFormat.create(
        country="Canadá",
        regex=r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$",
        description="Alternancia letra/dígito con espacio opcional en medio (A1A 1A1).",
        examples=("K1A 0B1", "H0H 0H0", "A1A1A1"),
    ),
    "México": PostalCodeFormat.create(
        country="México",
        regex=r"^\d{5}$",
        description="Cinco dígitos sin espacios ni guiones.",
        examples=("01000", "20010", "97139"),
    ),
    "Estados Unidos": PostalCodeFormat.create(
        country="Estados Unidos",
        regex=r"^\d{5}(-\d{4})?$",
        description="Formato ZIP de cinco dígitos o ZIP+4 con guion intermedio.",
        examples=("02115", "94105", "30301-1234"),
    ),
    "Francia": PostalCodeFormat.create(
        country="Francia",
        regex=r"^\d{5}$",
        description="Cinco dígitos; los dos primeros representan el departamento.",
        examples=("75001", "13008", "97100"),
    ),
    "España": PostalCodeFormat.create(
        country="España",
        regex=r"^(0[1-9]|[1-4]\d|5[0-2])\d{3}$",
        description="Cinco dígitos; los dos primeros indican la provincia (01–52).",
        examples=("28013", "08002", "41001"),
    ),
}


@dataclass
class ValidationResult:
    """Representa el resultado de una validación de código postal."""

    raw_value: str
    normalized_value: str
    is_valid: bool
    message: str


class PostalCodeValidatorApp(tk.Tk):
    """Ventana principal para validar códigos postales."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Validador de Código Postal")
        self.geometry("780x480")
        self.minsize(720, 420)
        self.configure(background="#e3f0ed")

        self._create_styles()
        self._create_widgets()

    # ------------------------------------------------------------------
    # Configuración de estilos
    # ------------------------------------------------------------------
    def _create_styles(self) -> None:
        style = ttk.Style(self)
        # En muchos entornos la temática predeterminada es "clam"; la activamos
        # para habilitar personalización de colores.
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure("Title.TLabel", font=("Calibri", 20, "bold"),
                        foreground="#0b4b5a", background="#e3f0ed")
        style.configure("Subtitle.TLabel", font=("Calibri", 12),
                        foreground="#0b4b5a", background="#e3f0ed")
        style.configure("Card.TLabelframe", background="#c9dfda",
                        bordercolor="#0b4b5a", relief="solid")
        style.configure("Card.TLabelframe.Label", font=("Calibri", 11, "bold"),
                        foreground="#0b4b5a", background="#c9dfda")
        style.configure("Card.TFrame", background="#c9dfda")
        style.configure("Action.TButton", font=("Calibri", 12, "bold"),
                        padding=6)
        style.configure("Input.TEntry", font=("Consolas", 14))
        style.configure("Result.TLabel", font=("Calibri", 14, "bold"))
        style.map("Action.TButton", background=[("active", "#0b4b5a")],
                   foreground=[("active", "#ffffff")])

    # ------------------------------------------------------------------
    # Creación de widgets
    # ------------------------------------------------------------------
    def _create_widgets(self) -> None:
        container = ttk.Frame(self, padding=18, style="Card.TFrame")
        container.pack(expand=True, fill="both")

        title = ttk.Label(container, text="Validación de Códigos Postales", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=2, sticky="w")

        self.subtitle_var = tk.StringVar()
        subtitle = ttk.Label(
            container,
            textvariable=self.subtitle_var,
            style="Subtitle.TLabel",
            wraplength=540,
            justify="left",
        )
        subtitle.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 16))

        ttk.Label(container, text="País", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky="w", pady=(0, 6)
        )

        self.country_var = tk.StringVar()
        self.country_combo = ttk.Combobox(
            container,
            textvariable=self.country_var,
            values=list(POSTAL_CODE_FORMATS.keys()),
            state="readonly",
        )
        self.country_combo.grid(row=2, column=1, sticky="w", pady=(0, 6))
        self.country_combo.bind("<<ComboboxSelected>>", self._on_country_changed)

        # Campo de entrada principal
        ttk.Label(container, text="Código Postal", style="Subtitle.TLabel").grid(
            row=3, column=0, sticky="w", pady=(0, 6)
        )

        self.postal_code_var = tk.StringVar(value="K1A 0B1")
        postal_entry = ttk.Entry(
            container,
            textvariable=self.postal_code_var,
            width=18,
            justify="center",
            style="Input.TEntry",
        )
        postal_entry.grid(row=3, column=1, sticky="w", pady=(0, 6))
        postal_entry.focus()

        # Opciones avanzadas
        options_frame = ttk.Labelframe(container, text="Opciones", padding=14, style="Card.TLabelframe")
        options_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(12, 16))

        self.auto_upper_var = tk.BooleanVar(value=True)
        auto_upper = ttk.Checkbutton(
            options_frame,
            text="Convertir a mayúsculas automáticamente",
            variable=self.auto_upper_var,
        )
        auto_upper.grid(row=0, column=0, sticky="w")

        self.auto_trim_var = tk.BooleanVar(value=True)
        auto_trim = ttk.Checkbutton(
            options_frame,
            text="Eliminar espacios extra al validar",
            variable=self.auto_trim_var,
        )
        auto_trim.grid(row=1, column=0, sticky="w")

        self.show_steps_var = tk.BooleanVar(value=True)
        show_steps = ttk.Checkbutton(
            options_frame,
            text="Mostrar pasos de validación",
            variable=self.show_steps_var,
        )
        show_steps.grid(row=2, column=0, sticky="w")

        # Área de resultados
        result_frame = ttk.Labelframe(container, text="Resultado", padding=14, style="Card.TLabelframe")
        result_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")

        self.result_label = ttk.Label(result_frame, text="Introduce un código para validar.",
                                      style="Result.TLabel", foreground="#555555")
        self.result_label.pack(anchor="w")

        self.steps_text = tk.Text(result_frame, height=6, state="disabled", wrap="word",
                                  relief="flat", background="#e9f5f2", font=("Consolas", 11))
        self.steps_text.pack(fill="both", expand=True, pady=(8, 0))

        # Barra de acciones
        action_frame = ttk.Frame(container, style="Card.TFrame")
        action_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=0)

        self.sample_list = tk.StringVar(value=[])
        self.sample_box = tk.Listbox(
            action_frame,
            listvariable=self.sample_list,
            height=5,
            selectmode="browse",
            activestyle="none",
            exportselection=False,
        )
        self.sample_box.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.sample_box.bind("<<ListboxSelect>>", self._on_sample_selected)

        buttons_frame = ttk.Frame(action_frame, style="Card.TFrame")
        buttons_frame.grid(row=0, column=1, sticky="n")

        validate_button = ttk.Button(buttons_frame, text="Validar", style="Action.TButton",
                                     command=self._on_validate_clicked)
        validate_button.grid(row=0, column=0, sticky="ew")

        clear_button = ttk.Button(buttons_frame, text="Limpiar", command=self._clear_inputs)
        clear_button.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        export_button = ttk.Button(buttons_frame, text="Exportar Resultado",
                                   command=self._export_result)
        export_button.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)
        action_frame.rowconfigure(0, weight=1)

        self._initialize_defaults()

    # ------------------------------------------------------------------
    # Eventos de la interfaz
    # ------------------------------------------------------------------
    def _on_sample_selected(self, event: tk.Event) -> None:  # pragma: no cover - UI
        selection = event.widget.curselection()
        if selection:
            value = event.widget.get(selection[0])
            self.postal_code_var.set(value)
            self._append_step(f"Se cargó el ejemplo: {value}")

    def _on_validate_clicked(self) -> None:
        result = self._validate_postal_code(self.postal_code_var.get())
        self._show_result(result)

    def _on_country_changed(self, event: tk.Event | None = None) -> None:  # pragma: no cover - UI
        current_format = self._get_current_format()
        self._update_subtitle(current_format)
        self._populate_sample_box(current_format.examples)
        self._append_step(f"Se seleccionó {current_format.country}.")

    def _clear_inputs(self) -> None:
        self.postal_code_var.set("")
        self.result_label.configure(text="Introduce un código para validar.", foreground="#555555")
        self._set_steps_text("")

    def _export_result(self) -> None:  # pragma: no cover - UI
        result_content = self.steps_text.get("1.0", tk.END).strip()
        if not result_content:
            messagebox.showinfo("Exportar", "No hay contenido para exportar.")
            return

        filepath = filedialog.asksaveasfilename(
            title="Guardar informe",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")],
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(result_content)
        messagebox.showinfo("Exportar", f"Informe guardado en: {filepath}")

    # ------------------------------------------------------------------
    # Lógica de validación
    # ------------------------------------------------------------------
    def _validate_postal_code(self, value: str) -> ValidationResult:
        original_value = value
        steps: list[str] = []
        current_format = self._get_current_format()
        steps.append(f"País seleccionado: {current_format.country}.")

        if self.auto_trim_var.get():
            value = value.strip()
            steps.append("Se eliminaron espacios iniciales y finales.")

        if self.auto_upper_var.get():
            value = value.upper()
            steps.append("Se transformó el texto a mayúsculas.")

        normalized = value
        steps.append(f"Valor normalizado: '{normalized}'")
        steps.append(f"Se utilizará la expresión regular: {current_format.regex}")

        if not normalized:
            steps.append("El campo está vacío.")
            result = ValidationResult(
                raw_value=original_value,
                normalized_value=normalized,
                is_valid=False,
                message="El código postal no puede estar vacío.",
            )
        elif current_format.pattern.fullmatch(normalized):
            steps.append("La expresión regular coincide con el patrón esperado.")
            result = ValidationResult(
                raw_value=original_value,
                normalized_value=normalized,
                is_valid=True,
                message=f"¡Código postal válido para {current_format.country}!",
            )
        else:
            steps.extend([
                "La expresión regular no coincide con el patrón esperado.",
                current_format.description,
            ])
            result = ValidationResult(
                raw_value=original_value,
                normalized_value=normalized,
                is_valid=False,
                message=f"El código postal no cumple el formato de {current_format.country}.",
            )

        if self.show_steps_var.get():
            self._set_steps_text("\n".join(steps))
        else:
            self._set_steps_text("")

        return result

    # ------------------------------------------------------------------
    # Actualización de la interfaz tras la validación
    # ------------------------------------------------------------------
    def _show_result(self, result: ValidationResult) -> None:
        color = "#0b5a3c" if result.is_valid else "#b03a2e"
        self.result_label.configure(text=result.message, foreground=color)

    def _initialize_defaults(self) -> None:
        self.country_var.set("Canadá")
        self._on_country_changed()

    def _append_step(self, message: str) -> None:
        previous = self.steps_text.get("1.0", tk.END).strip()
        combined = f"{previous}\n{message}" if previous else message
        self._set_steps_text(combined)

    def _set_steps_text(self, text: str) -> None:
        self.steps_text.configure(state="normal")
        self.steps_text.delete("1.0", tk.END)
        if text:
            self.steps_text.insert(tk.END, text)
        self.steps_text.configure(state="disabled")

    def _get_current_format(self) -> PostalCodeFormat:
        return POSTAL_CODE_FORMATS[self.country_var.get()]

    def _update_subtitle(self, code_format: PostalCodeFormat) -> None:
        subtitle = (
            f"Formato para {code_format.country}: {code_format.description}\n"
            f"Regex: {code_format.regex}\n"
            f"Ejemplos: {', '.join(code_format.examples)}"
        )
        self.subtitle_var.set(subtitle)

    def _populate_sample_box(self, examples: tuple[str, ...]) -> None:
        self.sample_box.delete(0, tk.END)
        for example in examples:
            self.sample_box.insert(tk.END, example)


def main() -> None:
    app = PostalCodeValidatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
