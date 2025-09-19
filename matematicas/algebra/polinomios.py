"""Rutinas para trabajar con polinomios."""
from typing import Iterable


def evaluar_polinomio(coeficientes: Iterable[float], x: float) -> float:
    """Evalúa un polinomio en el punto ``x``.

    Los coeficientes deben estar ordenados desde el término independiente
    hasta el de mayor grado. Por ejemplo, los coeficientes ``[2, 3, 1]``
    representan ``2 + 3x + x**2``.
    """
    resultado = 0.0
    for potencia, coeficiente in enumerate(coeficientes):
        resultado += coeficiente * (x ** potencia)
    return resultado
