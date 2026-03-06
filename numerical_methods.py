"""Lógica matemática para la Calculadora de Métodos Numéricos.

Este módulo contiene implementaciones reutilizables de:
- Método de la Secante.
- Método de Gauss-Seidel.
- Interpolación de Lagrange.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


@dataclass
class IteracionSecante:
    """Representa una fila de iteración del método de la secante."""

    iteracion: int
    x_prev: float
    x_actual: float
    x_siguiente: float
    error_abs: float


@dataclass
class ResultadoSecante:
    """Resultado final del método de la secante."""

    raiz_aproximada: float
    iteraciones: list[IteracionSecante]


@dataclass
class ResultadoGaussSeidel:
    """Resultado final del método de Gauss-Seidel."""

    solucion: np.ndarray
    historial: list[np.ndarray]
    iteraciones: int


def parsear_funcion(funcion_texto: str) -> Callable[[float], float]:
    """Convierte un texto matemático (ej. ``x^2 + sin(x)``) en función evaluable.

    Parameters
    ----------
    funcion_texto:
        Función en formato de texto.

    Returns
    -------
    Callable[[float], float]
        Función numérica evaluable.

    Raises
    ------
    ValueError
        Si la función no se puede interpretar correctamente.
    """

    x = sp.symbols("x")
    try:
        expresion = parse_expr(funcion_texto, transformations=TRANSFORMATIONS)
        funcion = sp.lambdify(x, expresion, modules=["numpy", "sympy"])
    except Exception as exc:  # noqa: BLE001 - convertimos a error amigable
        raise ValueError("No se pudo interpretar la función ingresada.") from exc

    def wrapper(valor: float) -> float:
        try:
            resultado = funcion(valor)
            return float(resultado)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Error al evaluar la función con el valor ingresado.") from exc

    return wrapper


def metodo_secante(
    funcion_texto: str,
    x0: float,
    x1: float,
    tolerancia: float,
    max_iter: int = 100,
) -> ResultadoSecante:
    """Calcula una raíz aproximada usando el método de la secante."""

    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")

    f = parsear_funcion(funcion_texto)
    iteraciones: list[IteracionSecante] = []

    for i in range(1, max_iter + 1):
        fx0 = f(x0)
        fx1 = f(x1)
        denominador = fx1 - fx0

        if denominador == 0:
            raise ValueError(
                "División por cero en la secante. Intenta con valores iniciales distintos."
            )

        x2 = x1 - fx1 * (x1 - x0) / denominador
        error = abs(x2 - x1)

        iteraciones.append(
            IteracionSecante(
                iteracion=i,
                x_prev=x0,
                x_actual=x1,
                x_siguiente=x2,
                error_abs=error,
            )
        )

        if error < tolerancia:
            return ResultadoSecante(raiz_aproximada=x2, iteraciones=iteraciones)

        x0, x1 = x1, x2

    raise ValueError("No se alcanzó convergencia con el número máximo de iteraciones.")


def metodo_gauss_seidel(
    matriz_a: np.ndarray,
    vector_b: np.ndarray,
    tolerancia: float,
    max_iter: int = 200,
) -> ResultadoGaussSeidel:
    """Resuelve ``Ax=b`` por Gauss-Seidel y retorna historial de iteraciones."""

    if tolerancia <= 0:
        raise ValueError("La tolerancia debe ser mayor que cero.")

    A = np.array(matriz_a, dtype=float)
    b = np.array(vector_b, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("La matriz A debe ser cuadrada.")
    if b.ndim != 1 or b.shape[0] != A.shape[0]:
        raise ValueError("El vector b debe tener el mismo tamaño que A.")

    n = A.shape[0]

    if np.any(np.diag(A) == 0):
        raise ValueError("La matriz tiene ceros en la diagonal principal.")

    x = np.zeros(n, dtype=float)
    historial: list[np.ndarray] = [x.copy()]

    for k in range(1, max_iter + 1):
        x_anterior = x.copy()

        for i in range(n):
            suma_1 = np.dot(A[i, :i], x[:i])
            suma_2 = np.dot(A[i, i + 1 :], x_anterior[i + 1 :])
            x[i] = (b[i] - suma_1 - suma_2) / A[i, i]

        historial.append(x.copy())

        if np.linalg.norm(x - x_anterior, ord=np.inf) < tolerancia:
            return ResultadoGaussSeidel(solucion=x, historial=historial, iteraciones=k)

    raise ValueError("Gauss-Seidel no convergió dentro del máximo de iteraciones.")


def polinomio_lagrange(x_vals: list[float], y_vals: list[float]) -> sp.Expr:
    """Construye el polinomio simbólico de Lagrange para pares (x, y)."""

    if len(x_vals) != len(y_vals):
        raise ValueError("Las listas x e y deben tener la misma longitud.")
    if len(x_vals) < 2:
        raise ValueError("Se necesitan al menos dos puntos para interpolar.")

    x = sp.symbols("x")
    puntos_x = [float(v) for v in x_vals]

    if len(set(puntos_x)) != len(puntos_x):
        raise ValueError("Los valores de x deben ser distintos entre sí.")

    polinomio = 0
    n = len(x_vals)

    for i in range(n):
        termino = y_vals[i]
        for j in range(n):
            if i != j:
                termino *= (x - x_vals[j]) / (x_vals[i] - x_vals[j])
        polinomio += termino

    return sp.expand(sp.simplify(polinomio))


def evaluar_lagrange(x_vals: list[float], y_vals: list[float], x_eval: float) -> float:
    """Evalúa el polinomio interpolante de Lagrange en un valor de ``x``."""

    x = sp.symbols("x")
    polinomio = polinomio_lagrange(x_vals, y_vals)
    evaluado = polinomio.subs(x, x_eval)
    return float(sp.N(evaluado))
