"""Phone number validation utility following US formatting conventions.

This module exposes a ``validate_phone_number`` function that checks
whether the provided string matches one of the common US phone formats:

* ``(xxx) xxx-xxxx`` – optional parentheses around the area code and a
  separating space before the next three digits.
* ``xxx-xxx-xxxx`` – digits separated by hyphens.
* ``xxxxxxxxxx`` – a continuous ten digit sequence without separators.

Run the module directly to launch an eye-catching Tkinter interface that
validates numbers in real time. A small CLI helper remains available via
``python -m phone_validation --cli`` for quick terminal checks.
"""

from __future__ import annotations

import argparse
import re
import tkinter as tk
from tkinter import ttk
from typing import Pattern

# Compile the regex once so it can be reused efficiently.
_PHONE_REGEX: Pattern[str] = re.compile(
    r"^"              # beginning of string
    r"(?:"            # start of non-capturing group for the three formats
    r"\(\d{3}\) \d{3}-\d{4}"  # (123) 456-7890
    r"|"             # or
    r"\d{3}-\d{3}-\d{4}"        # 123-456-7890
    r"|"             # or
    r"\d{10}"                      # 1234567890
    r")"              # end of non-capturing group
    r"$"              # end of string
)


def validate_phone_number(number: str) -> bool:
    """Return ``True`` when *number* matches an accepted phone format.

    Parameters
    ----------
    number:
        The string to validate. Leading and trailing whitespace is ignored.
    """

    number = number.strip()
    return bool(_PHONE_REGEX.match(number))


def _cli() -> None:
    """Read phone numbers from input and report whether they are valid."""

    print("Enter phone numbers to validate (empty line to quit):")
    while True:
        try:
            value = input("> ")
        except EOFError:
            print()  # ensure a newline on EOF
            break

        if not value.strip():
            break

        if validate_phone_number(value):
            print("✔️  Valid format")
        else:
            print("❌ Invalid format")


def _build_main_window(root: tk.Tk) -> None:
    """Create the Tkinter widgets and connect them to validation logic."""

    root.title("Validador de Números – Super Fancy Edition")
    root.geometry("420x260")
    root.minsize(360, 240)
    root.configure(padx=20, pady=20)

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"))
    style.configure("Result.TLabel", font=("Segoe UI", 14, "bold"))

    header = ttk.Label(
        root,
        text="Introduce un número telefónico gringo y recibe la verdad al instante",
        anchor="center",
        justify="center",
        wraplength=360,
        font=("Segoe UI", 12, "bold"),
    )
    header.pack(fill=tk.X, pady=(0, 16))

    phone_var = tk.StringVar()
    result_var = tk.StringVar(value="Esperando tu número más perrón…")

    entry_frame = ttk.Frame(root)
    entry_frame.pack(fill=tk.X)

    entry = ttk.Entry(entry_frame, textvariable=phone_var, font=("Consolas", 14))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    entry.focus()

    def update_status(*_: object) -> None:
        number = phone_var.get()
        if not number:
            result_var.set("Esperando tu número más perrón…")
            result_label.configure(foreground="#555555")
            return

        if validate_phone_number(number):
            result_var.set("✅ ¡Formato impecable!")
            result_label.configure(foreground="#1b8a5a")
        else:
            result_var.set("❌ Ese formato no pasa la vibra.")
            result_label.configure(foreground="#c22727")

    def clear_entry() -> None:
        phone_var.set("")
        entry.focus()
        update_status()

    entry.bind("<KeyRelease>", update_status)

    buttons = ttk.Frame(root)
    buttons.pack(fill=tk.X, pady=12)

    validate_button = ttk.Button(
        buttons,
        text="Validar ahora",
        style="Accent.TButton",
        command=update_status,
    )
    validate_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

    clear_button = ttk.Button(buttons, text="Limpiar", command=clear_entry)
    clear_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

    result_label = ttk.Label(
        root,
        textvariable=result_var,
        style="Result.TLabel",
        anchor="center",
        padding=12,
    )
    result_label.pack(fill=tk.BOTH, expand=True)

    info_text = (
        "Formatos aceptados: (123) 456-7890, 123-456-7890 o 1234567890."
    )
    info_label = ttk.Label(root, text=info_text, justify="center", wraplength=360)
    info_label.pack(fill=tk.X, pady=(8, 0))

    update_status()


def launch_gui() -> None:
    """Start the graphical interface for validating phone numbers."""

    root = tk.Tk()
    _build_main_window(root)
    root.mainloop()


def main() -> None:
    """Entry point that decides between GUI mode and CLI mode."""

    parser = argparse.ArgumentParser(description="Validate US phone numbers")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="run in command-line mode instead of launching the GUI",
    )
    args = parser.parse_args()

    if args.cli:
        _cli()
    else:
        launch_gui()


if __name__ == "__main__":
    main()
