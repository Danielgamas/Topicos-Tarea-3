"""Ejemplo de métodos especiales y sobrecarga de operadores en Python.

Se define una clase ``Vector`` en dos dimensiones que implementa los métodos
especiales ``__str__`` (para mostrar una representación legible), ``__add__`` y
``__sub__`` (para sobrecargar los operadores de suma y resta, respectivamente).

Al ejecutar este archivo directamente se muestran ejemplos de uso.
"""

from __future__ import annotations


class Vector:
    """Representa un vector en dos dimensiones."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """Devuelve la representación en forma de tupla ordenada."""
        return f"({self.x}, {self.y})"

    def __add__(self, other: "Vector") -> "Vector":
        """Suma componente a componente con otro vector."""
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector") -> "Vector":
        """Resta componente a componente con otro vector."""
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)


if __name__ == "__main__":
    vector_1 = Vector(2, 3)
    vector_2 = Vector(4, 1)

    print("Vector 1:", vector_1)
    print("Vector 2:", vector_2)
    print("Suma:", vector_1 + vector_2)
    print("Resta:", vector_1 - vector_2)
