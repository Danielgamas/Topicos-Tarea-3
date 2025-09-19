"""Demostración de uso del módulo ``operations`` y del paquete ``matematicas``."""

import operations
from matematicas import algebra, operaciones_basicas


def main() -> None:
    """Ejecuta ejemplos de uso para los módulos creados."""
    print("=== Uso del módulo operations ===")
    print("Suma 4 + 5:", operations.suma(4, 5))
    print("Resta 9 - 4:", operations.resta(9, 4))
    print("Multiplicación 3 * 4:", operations.multiplicacion(3, 4))

    print("\n=== Uso del paquete matematicas ===")
    coeficientes = [1.3, 4.5, 2.6]
    print(
        "Evaluar polinomio 1.3 + 4.5x + 2.6x^2 en x=2:",
        algebra.evaluar_polinomio(coeficientes, 2),
    )
    print("Suma 3 + 4 usando el paquete:", operaciones_basicas.suma(3, 4))
    print("Resta 3 - 4 usando el paquete:", operaciones_basicas.resta(3, 4))


if __name__ == "__main__":
    main()
