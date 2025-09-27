from __future__ import annotations

import string
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Iterable, List, Sequence

import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk


USERNAME_CHARS = set(string.ascii_letters + string.digits + ".")
DOMAIN_CHARS = set(string.ascii_letters + string.digits + "-")
TLD_CHARS = set(string.ascii_letters)

DEFAULT_STATE_BG = "#1e293b"
ACTIVE_STATE_BG = "#2563eb"
ERROR_STATE_BG = "#b91c1c"


class State(Enum):
    """Estados del autómata finito determinista."""

    START = auto()
    USERNAME = auto()
    AT = auto()
    DOMAIN = auto()
    DOT = auto()
    TLD = auto()
    ERROR = auto()


STATE_LABELS = {
    State.START: "INICIO",
    State.USERNAME: "USUARIO",
    State.AT: "ARROBA",
    State.DOMAIN: "DOMINIO",
    State.DOT: "PUNTO",
    State.TLD: "TLD",
    State.ERROR: "ERROR",
}


@dataclass
class Transition:
    """Descripción de una transición individual del autómata."""

    index: int
    char: str
    prev_state: State
    next_state: State
    description: str


@dataclass
class DFA:
    """Implementación del DFA para validar correos."""

    state: State = State.START
    username_len: int = 0
    domain_len: int = 0
    tld_len: int = 0
    tld_groups: int = 0
    tld_lengths: List[int] = field(default_factory=list)
    error_reason: str | None = None

    def process(self, text: str) -> bool:
        """Procesa ``text`` y devuelve si es aceptado."""

        accepted, _ = self.process_verbose(text)
        return accepted

    def process_verbose(self, text: str) -> tuple[bool, List[Transition]]:
        """Procesa ``text`` devolviendo el resultado y las transiciones."""

        transitions: List[Transition] = []
        for index, ch in enumerate(text):
            prev_state = self.state
            description = ""

            if self.state == State.START:
                if ch in USERNAME_CHARS:
                    self.state = State.USERNAME
                    self.username_len = 1
                    description = "Inicio del nombre de usuario."
                else:
                    description = "El primer carácter debe ser letra, dígito o punto."
                    self._reject(description)

            elif self.state == State.USERNAME:
                if ch in USERNAME_CHARS:
                    self.username_len += 1
                    description = "Carácter válido dentro del nombre de usuario."
                elif ch == "@":
                    if self.username_len == 0:
                        description = "Se requiere al menos un carácter antes de '@'."
                        self._reject(description)
                    else:
                        self.state = State.AT
                        description = "Separador '@' encontrado; comienza el dominio."
                else:
                    description = "Carácter inválido dentro del nombre de usuario."
                    self._reject(description)

            elif self.state == State.AT:
                if ch in DOMAIN_CHARS:
                    self.state = State.DOMAIN
                    self.domain_len = 1
                    description = "Primer carácter válido del dominio."
                else:
                    description = "El dominio solo acepta letras, dígitos o guiones."
                    self._reject(description)

            elif self.state == State.DOMAIN:
                if ch in DOMAIN_CHARS:
                    self.domain_len += 1
                    description = "Carácter válido dentro del dominio."
                elif ch == ".":
                    if self.domain_len == 0:
                        description = "El dominio principal no puede estar vacío."
                        self._reject(description)
                    else:
                        self.state = State.DOT
                        description = "Punto detectado; se espera un TLD."
                else:
                    description = "Carácter no permitido dentro del dominio."
                    self._reject(description)

            elif self.state == State.DOT:
                if ch in TLD_CHARS:
                    self.state = State.TLD
                    self.tld_len = 1
                    description = "Inicio de un TLD; solo se permiten letras."
                else:
                    description = "Tras un punto solo se aceptan letras para el TLD."
                    self._reject(description)

            elif self.state == State.TLD:
                if ch in TLD_CHARS:
                    self.tld_len += 1
                    description = "Letra válida dentro del TLD."
                elif ch == ".":
                    if self.tld_len < 2:
                        description = "Cada TLD debe tener al menos dos letras."
                        self._reject(description)
                    else:
                        self.tld_groups += 1
                        self.tld_lengths.append(self.tld_len)
                        self.state = State.DOT
                        self.tld_len = 0
                        description = "Nuevo punto; se espera otro TLD consecutivo."
                else:
                    description = "Solo se permiten letras dentro del TLD."
                    self._reject(description)

            else:
                description = "Transición no válida desde un estado de error."

            transitions.append(
                Transition(
                    index=index,
                    char=ch,
                    prev_state=prev_state,
                    next_state=self.state,
                    description=description,
                )
            )

            if self.state == State.ERROR:
                break

        if self.state == State.TLD and self.tld_len >= 2:
            self.tld_groups += 1
            self.tld_lengths.append(self.tld_len)

        accepted = (
            self.state == State.TLD
            and self.username_len > 0
            and self.domain_len > 0
            and self.tld_groups >= 1
        )

        if not accepted and self.error_reason is None:
            if self.state != State.TLD:
                self.error_reason = "La cadena terminó antes de completar el patrón."
            elif self.tld_len < 2:
                self.error_reason = "El último TLD debe tener al menos dos letras."
            elif self.tld_groups == 0:
                self.error_reason = "Se requiere al menos un TLD válido."

        final_description = (
            "Validación final exitosa; la dirección pertenece al lenguaje."
            if accepted
            else f"Rechazo final: {self.error_reason or 'Condiciones finales no satisfechas.'}"
        )
        transitions.append(
            Transition(
                index=len(text),
                char="∅",
                prev_state=self.state,
                next_state=self.state if accepted else State.ERROR,
                description=final_description,
            )
        )

        if not accepted and transitions[-1].next_state == State.ERROR:
            self.state = State.ERROR

        return accepted, transitions

    def _reject(self, reason: str) -> bool:
        self.state = State.ERROR
        self.error_reason = reason
        return False


def validate_email(email: str) -> bool:
    """Valida ``email`` utilizando el DFA descrito."""

    if email.count("@") != 1:
        return False

    machine = DFA()
    return machine.process(email)


def analyze_email(email: str) -> tuple[bool, List[Transition], Sequence[dict[str, object]], str]:
    """Ejecuta la validación devolviendo detalles completos para la GUI."""

    requirements = build_requirements(email)

    if email.count("@") != 1:
        transitions = [
            Transition(
                index=0,
                char="∅",
                prev_state=State.START,
                next_state=State.ERROR,
                description="La dirección debe contener exactamente un símbolo '@'.",
            )
        ]
        summary = "Rechazada: la dirección debe contener exactamente un símbolo '@'."
        return False, transitions, requirements, summary

    machine = DFA()
    accepted, transitions = machine.process_verbose(email)
    summary = (
        "Dirección válida aceptada por el autómata."
        if accepted
        else f"Rechazada: {machine.error_reason or 'Condiciones finales no satisfechas.'}"
    )
    return accepted, transitions, requirements, summary


def build_requirements(email: str) -> List[dict[str, object]]:
    """Calcula el estado de los requisitos individuales del patrón."""

    requirements: List[dict[str, object]] = []
    single_at = email.count("@") == 1
    username, domain_full = (email.split("@", 1) + [""])[:2] if single_at else (email, "")
    domain_parts = domain_full.split(".") if domain_full else []
    domain_root = domain_parts[0] if domain_parts else ""
    tld_parts = domain_parts[1:] if len(domain_parts) > 1 else []

    requirements.append(
        {
            "name": "Único símbolo '@'",
            "ok": single_at,
            "detail": "La dirección debe contener exactamente un símbolo '@'.",
        }
    )

    username_ok = bool(username) and all(ch in USERNAME_CHARS for ch in username)
    requirements.append(
        {
            "name": "Nombre de usuario válido",
            "ok": username_ok,
            "detail": "Solo letras, dígitos y puntos; debe existir al menos un carácter.",
        }
    )

    domain_ok = bool(domain_root) and all(ch in DOMAIN_CHARS for ch in domain_root)
    requirements.append(
        {
            "name": "Dominio principal válido",
            "ok": domain_ok,
            "detail": "Debe haber texto entre '@' y el primer punto, con letras, dígitos o guiones.",
        }
    )

    tld_ok = bool(tld_parts) and all(len(seg) >= 2 and set(seg).issubset(TLD_CHARS) for seg in tld_parts)
    requirements.append(
        {
            "name": "TLD estructurado",
            "ok": tld_ok,
            "detail": "Se requieren uno o más TLDs de solo letras con al menos dos caracteres cada uno.",
        }
    )

    clean_ok = " " not in email and "\t" not in email and 3 <= len(email) <= 254
    requirements.append(
        {
            "name": "Formato limpio",
            "ok": clean_ok,
            "detail": "Sin espacios en blanco y longitud entre 3 y 254 caracteres.",
        }
    )

    return requirements


class EmailValidatorApp:
    """Aplicación Tkinter con una interfaz rica en detalles."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Validador DFA de Correos Electrónicos")
        self.root.geometry("1100x750")
        self.root.configure(bg="#0f172a")
        self.root.minsize(1024, 680)
        self.root.option_add("*Font", "{Segoe UI} 11")

        self.email_var = tk.StringVar()
        self.result_var = tk.StringVar(value="Introduce un correo y presiona Validar")

        self.style = ttk.Style()
        self._configure_theme()
        self._build_ui()

    def _configure_theme(self) -> None:
        self.style.theme_use("clam")
        self.style.configure(
            "TFrame",
            background="#0f172a",
        )
        self.style.configure(
            "Card.TFrame",
            background="#1f2937",
            relief="flat",
        )
        self.style.configure(
            "CardAccent.TFrame",
            background="#111827",
            relief="flat",
        )
        self.style.configure(
            "TLabel",
            background="#0f172a",
            foreground="#e2e8f0",
        )
        self.style.configure(
            "Card.TLabel",
            background="#1f2937",
            foreground="#f8fafc",
        )
        self.style.configure(
            "Result.TLabel",
            background="#1f2937",
            foreground="#fbbf24",
            font=("{Segoe UI Semibold}", 16),
        )
        self.style.configure(
            "Success.Result.TLabel",
            background="#1f2937",
            foreground="#34d399",
            font=("{Segoe UI Semibold}", 16),
        )
        self.style.configure(
            "Danger.Result.TLabel",
            background="#1f2937",
            foreground="#f87171",
            font=("{Segoe UI Semibold}", 16),
        )
        self.style.configure(
            "Accent.TButton",
            background="#f97316",
            foreground="#0f172a",
            padding=10,
            font=("{Segoe UI Semibold}", 11),
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", "#fb923c")],
            foreground=[("active", "#0f172a")],
        )
        self.style.configure(
            "Secondary.TButton",
            background="#1f2937",
            foreground="#cbd5f5",
            padding=10,
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#334155")],
            foreground=[("active", "#f8fafc")],
        )
        self.style.configure(
            "TEntry",
            fieldbackground="#111827",
            foreground="#f8fafc",
            insertcolor="#f8fafc",
            padding=8,
        )
        self.style.configure(
            "Treeview",
            background="#111827",
            fieldbackground="#111827",
            foreground="#e2e8f0",
            rowheight=28,
            borderwidth=0,
        )
        self.style.map("Treeview", background=[("selected", "#1d4ed8")])
        self.style.configure(
            "Treeview.Heading",
            background="#1f2937",
            foreground="#f8fafc",
            font=("{Segoe UI Semibold}", 11),
        )

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg="#1e293b", bd=0, relief="ridge")
        header.pack(fill="x", padx=24, pady=(20, 12))

        title = tk.Label(
            header,
            text="Validador de correos con Autómata Finito",
            font=("{Segoe UI Semibold}", 22),
            fg="#f8fafc",
            bg="#1e293b",
        )
        title.pack(anchor="w", padx=24, pady=(16, 4))

        subtitle = tk.Label(
            header,
            text="Visualiza cada transición del DFA y comprueba en tiempo real cómo se cumplen los requisitos del patrón.",
            font=("{Segoe UI}", 12),
            fg="#cbd5f5",
            bg="#1e293b",
            wraplength=900,
            justify="left",
        )
        subtitle.pack(anchor="w", padx=24, pady=(0, 16))

        content = ttk.Frame(self.root, padding=20)
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)

        left_column = ttk.Frame(content, style="Card.TFrame", padding=20)
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left_column.columnconfigure(0, weight=1)

        input_frame = ttk.Frame(left_column, style="Card.TFrame")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        input_frame.columnconfigure(1, weight=1)

        entry_label = ttk.Label(
            input_frame,
            text="Dirección de correo",
            style="Card.TLabel",
            font=("{Segoe UI Semibold}", 12),
        )
        entry_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        entry = ttk.Entry(input_frame, textvariable=self.email_var, width=50, font=("{Segoe UI}", 14))
        entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        entry.focus_set()

        button_frame = ttk.Frame(input_frame, style="Card.TFrame")
        button_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)

        validate_btn = ttk.Button(
            button_frame,
            text="Validar",
            style="Accent.TButton",
            command=self.on_validate,
        )
        validate_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        clear_btn = ttk.Button(
            button_frame,
            text="Limpiar",
            style="Secondary.TButton",
            command=self.on_clear,
        )
        clear_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        result_frame = ttk.Frame(left_column, style="CardAccent.TFrame", padding=(16, 12))
        result_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        result_frame.columnconfigure(0, weight=1)

        self.result_label = ttk.Label(
            result_frame,
            textvariable=self.result_var,
            style="Result.TLabel",
            wraplength=600,
            justify="left",
        )
        self.result_label.grid(row=0, column=0, sticky="w")

        state_panel = tk.Frame(left_column, bg="#0f172a")
        state_panel.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        state_title = tk.Label(
            state_panel,
            text="Estados recorridos por el autómata",
            font=("{Segoe UI Semibold}", 12),
            fg="#f8fafc",
            bg="#0f172a",
        )
        state_title.grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.state_badges: dict[State, tk.Label] = {}
        badge_frame = tk.Frame(state_panel, bg="#0f172a")
        badge_frame.grid(row=1, column=0, sticky="ew")
        for idx, state in enumerate(State):
            label = tk.Label(
                badge_frame,
                text=STATE_LABELS[state],
                font=("{Segoe UI}", 10),
                bg=DEFAULT_STATE_BG,
                fg="#cbd5f5",
                padx=12,
                pady=6,
                relief="ridge",
                bd=1,
            )
            label.grid(row=0, column=idx, padx=6, pady=4, sticky="ew")
            self.state_badges[state] = label

        tree_frame = ttk.Frame(left_column, style="Card.TFrame", padding=10)
        tree_frame.grid(row=3, column=0, sticky="nsew")
        left_column.rowconfigure(3, weight=1)

        tree_label = ttk.Label(
            tree_frame,
            text="Transiciones del DFA",
            style="Card.TLabel",
            font=("{Segoe UI Semibold}", 12),
        )
        tree_label.pack(anchor="w", pady=(0, 8))

        columns = ("index", "char", "prev", "next", "description")
        self.transition_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Treeview",
            selectmode="browse",
            height=12,
        )
        self.transition_tree.heading("index", text="#")
        self.transition_tree.heading("char", text="Símbolo")
        self.transition_tree.heading("prev", text="Estado previo")
        self.transition_tree.heading("next", text="Estado siguiente")
        self.transition_tree.heading("description", text="Descripción")
        self.transition_tree.column("index", width=60, anchor="center")
        self.transition_tree.column("char", width=80, anchor="center")
        self.transition_tree.column("prev", width=150, anchor="center")
        self.transition_tree.column("next", width=160, anchor="center")
        self.transition_tree.column("description", width=520, anchor="w")
        self.transition_tree.pack(fill="both", expand=True, side="left")
        self.transition_tree.tag_configure("error", foreground="#fca5a5")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.transition_tree.yview)
        tree_scroll.pack(fill="y", side="right")
        self.transition_tree.configure(yscrollcommand=tree_scroll.set)

        right_column = ttk.Frame(content, style="CardAccent.TFrame", padding=20)
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        requirements_label = ttk.Label(
            right_column,
            text="Requisitos del patrón",
            style="Card.TLabel",
            font=("{Segoe UI Semibold}", 13),
        )
        requirements_label.grid(row=0, column=0, sticky="w")

        self.requirement_vars: list[tk.StringVar] = []
        requirements_frame = ttk.Frame(right_column, style="CardAccent.TFrame")
        requirements_frame.grid(row=1, column=0, sticky="ew", pady=(8, 16))
        for idx in range(5):
            var = tk.StringVar()
            lbl = ttk.Label(
                requirements_frame,
                textvariable=var,
                style="Card.TLabel",
                wraplength=320,
                justify="left",
            )
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            self.requirement_vars.append(var)

        info_label = ttk.Label(
            right_column,
            text="Acerca del autómata",
            style="Card.TLabel",
            font=("{Segoe UI Semibold}", 13),
        )
        info_label.grid(row=2, column=0, sticky="w", pady=(12, 4))

        info_text = (
            "El autómata finito determinista recorre siete estados para validar "
            "el correo. Cada transición refleja las reglas estudiadas: el nombre "
            "de usuario admite letras, dígitos y puntos; el dominio exige letras, "
            "dígitos o guiones; los TLD se forman únicamente con letras y "
            "necesitan dos o más caracteres."
        )
        info_content = ttk.Label(
            right_column,
            text=info_text,
            style="Card.TLabel",
            wraplength=340,
            justify="left",
        )
        info_content.grid(row=3, column=0, sticky="w")

        history_label = ttk.Label(
            right_column,
            text="Bitácora de validaciones",
            style="Card.TLabel",
            font=("{Segoe UI Semibold}", 13),
        )
        history_label.grid(row=4, column=0, sticky="w", pady=(16, 4))

        self.history_box = scrolledtext.ScrolledText(
            right_column,
            height=12,
            wrap="word",
            bg="#111827",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            font=("{Segoe UI}", 10),
        )
        self.history_box.grid(row=5, column=0, sticky="nsew")
        self.history_box.configure(state="disabled")
        right_column.rowconfigure(5, weight=1)

        footer = tk.Label(
            self.root,
            text="Diseñado para explorar el comportamiento interno del DFA.",
            font=("{Segoe UI}", 10),
            fg="#64748b",
            bg="#0f172a",
        )
        footer.pack(pady=(0, 16))

        self.on_clear()

    def on_validate(self) -> None:
        email = self.email_var.get().strip()
        if not email:
            messagebox.showinfo("Campo vacío", "Introduce una dirección de correo para evaluarla.")
            return

        accepted, transitions, requirements, summary = analyze_email(email)
        self._populate_transitions(transitions)
        self._update_result(accepted, summary)
        self._update_requirements(requirements)
        self._update_state_badges(transitions)
        self._append_history(email, accepted, summary)

    def on_clear(self) -> None:
        self.email_var.set("")
        self.result_var.set("Introduce un correo y presiona Validar")
        self.result_label.configure(style="Result.TLabel")
        for item in self.transition_tree.get_children():
            self.transition_tree.delete(item)
        for badge in self.state_badges.values():
            badge.configure(bg=DEFAULT_STATE_BG)
        placeholder_transitions = [
            Transition(0, "∅", State.START, State.START, "El autómata espera la entrada."),
            Transition(1, "∅", State.START, State.ERROR, "Cuando ocurren errores se mostrará aquí el motivo."),
        ]
        self._populate_transitions(placeholder_transitions)
        self._update_requirements(build_requirements(""))

    def _populate_transitions(self, transitions: Iterable[Transition]) -> None:
        for item in self.transition_tree.get_children():
            self.transition_tree.delete(item)
        for transition in transitions:
            tag = "error" if transition.next_state == State.ERROR else ""
            self.transition_tree.insert(
                "",
                "end",
                values=(
                    transition.index,
                    transition.char,
                    STATE_LABELS[transition.prev_state],
                    STATE_LABELS[transition.next_state],
                    transition.description,
                ),
                tags=(tag,),
            )

    def _update_requirements(self, requirements: Sequence[dict[str, object]]) -> None:
        for var, req in zip(self.requirement_vars, requirements):
            status = "✅" if req.get("ok") else "❌"
            var.set(f"{status} {req.get('name')}: {req.get('detail')}")

        for idx in range(len(requirements), len(self.requirement_vars)):
            self.requirement_vars[idx].set("")

    def _update_result(self, accepted: bool, summary: str) -> None:
        self.result_var.set(summary)
        if accepted:
            self.result_label.configure(style="Success.Result.TLabel")
        else:
            self.result_label.configure(style="Danger.Result.TLabel")

    def _update_state_badges(self, transitions: Iterable[Transition]) -> None:
        visited: set[State] = set()
        error_present = False
        for transition in transitions:
            visited.add(transition.prev_state)
            visited.add(transition.next_state)
            if transition.next_state == State.ERROR:
                error_present = True
        for state, label in self.state_badges.items():
            if state == State.ERROR and not error_present:
                label.configure(bg=DEFAULT_STATE_BG)
                continue
            if state in visited:
                label.configure(bg=ERROR_STATE_BG if state == State.ERROR else ACTIVE_STATE_BG)
            else:
                label.configure(bg=DEFAULT_STATE_BG)

    def _append_history(self, email: str, accepted: bool, summary: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        verdict = "VÁLIDO" if accepted else "INVÁLIDO"
        self.history_box.configure(state="normal")
        self.history_box.insert(
            "end",
            f"[{timestamp}] {verdict} → {email}\n   {summary}\n\n",
        )
        self.history_box.configure(state="disabled")
        self.history_box.see("end")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    app = EmailValidatorApp()
    app.run()


if __name__ == "__main__":
    main()
