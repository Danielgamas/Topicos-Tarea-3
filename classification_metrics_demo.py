"""Demostración de métricas de clasificación usando el dataset Iris.

El objetivo es replicar las ideas vistas en la explicación: cargar un
conjunto de datos con tres clases, generar predicciones aleatorias y
calcular métricas de clasificación (matriz de confusión, precisión,
recall, F1 y AUC de la curva ROC).

Para mantener el script auto contenido, se intenta usar ``scikit-learn``
y ``numpy`` cuando están disponibles. Si no lo están, se recurre a una
versión sintética del dataset Iris generada con números aleatorios
controlados y a implementaciones basadas únicamente en la biblioteca
estándar.
"""

from __future__ import annotations

import importlib.util
import random
from itertools import accumulate
from pathlib import Path
from statistics import mean
from typing import Iterable, List, Sequence, Tuple

_HAS_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
_HAS_SKLEARN = importlib.util.find_spec("sklearn") is not None

if _HAS_MATPLOTLIB:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
else:
    plt = None  # type: ignore

if _HAS_SKLEARN:
    from sklearn.datasets import load_iris as _sklearn_load_iris
else:
    _sklearn_load_iris = None


def _synthetic_iris() -> Tuple[List[List[float]], List[int]]:
    """Genera un dataset sintético similar al Iris original."""

    rng = random.Random(12345)
    centers = [
        (5.0, 3.5, 1.5, 0.2),
        (5.9, 2.8, 4.2, 1.3),
        (6.5, 3.0, 5.5, 2.0),
    ]
    spreads = [
        (0.4, 0.3, 0.3, 0.1),
        (0.6, 0.4, 0.5, 0.2),
        (0.7, 0.4, 0.6, 0.3),
    ]

    data: List[List[float]] = []
    target: List[int] = []

    for label, (center, spread) in enumerate(zip(centers, spreads)):
        for _ in range(50):
            features = [
                center[i] + spread[i] * (rng.random() - 0.5) * 2 for i in range(4)
            ]
            data.append(features)
            target.append(label)

    return data, target


def load_dataset() -> Tuple[List[List[float]], List[int]]:
    """Carga el dataset Iris o una aproximación sintética."""

    if _sklearn_load_iris is not None:
        iris = _sklearn_load_iris()
        data = [list(row) for row in iris.data]
        target = list(map(int, iris.target))
        return data, target

    return _synthetic_iris()


def predict_randomly(
    n_samples: int, n_classes: int, seed: int | None = None
) -> List[int]:
    """Genera etiquetas aleatorias con distribución uniforme."""

    rng = random.Random(seed)
    return [rng.randrange(n_classes) for _ in range(n_samples)]


def compute_confusion_matrix(
    y_true: Sequence[int], y_pred: Sequence[int]
) -> Tuple[List[List[int]], List[int]]:
    """Calcula la matriz de confusión y devuelve el orden de las clases."""

    labels = sorted(set(y_true) | set(y_pred))
    index = {label: pos for pos, label in enumerate(labels)}
    size = len(labels)
    matrix = [[0 for _ in range(size)] for _ in range(size)]

    for true_label, pred_label in zip(y_true, y_pred):
        matrix[index[true_label]][index[pred_label]] += 1

    return matrix, labels


def compute_precision(confusion_matrix: Sequence[Sequence[int]]) -> float:
    """Calcula la precisión macro-promediada."""

    size = len(confusion_matrix)
    precisions: List[float] = []

    for col in range(size):
        true_positive = confusion_matrix[col][col]
        predicted = sum(confusion_matrix[row][col] for row in range(size))
        if predicted == 0:
            precisions.append(0.0)
        else:
            precisions.append(true_positive / predicted)

    return mean(precisions) if precisions else 0.0


def compute_recall(confusion_matrix: Sequence[Sequence[int]]) -> float:
    """Calcula el recall macro-promediado."""

    size = len(confusion_matrix)
    recalls: List[float] = []

    for row in range(size):
        true_positive = confusion_matrix[row][row]
        actual = sum(confusion_matrix[row])
        if actual == 0:
            recalls.append(0.0)
        else:
            recalls.append(true_positive / actual)

    return mean(recalls) if recalls else 0.0


def compute_f1_score(precision: float, recall: float) -> float:
    """Calcula el F1-score a partir de precisión y recall."""

    if precision == 0 and recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_roc_curve(
    y_true: Sequence[int], scores: Sequence[float]
) -> Tuple[List[float], List[float]]:
    """Calcula la curva ROC para datos binarios (clase positiva = 1)."""

    order = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)
    y_sorted = [y_true[idx] for idx in order]

    tp_cumsum = list(accumulate(1 if label == 1 else 0 for label in y_sorted))
    fp_cumsum = list(accumulate(1 if label != 1 else 0 for label in y_sorted))

    total_positive = tp_cumsum[-1] if tp_cumsum else 0
    total_negative = fp_cumsum[-1] if fp_cumsum else 0

    if total_positive == 0:
        tpr = [0.0 for _ in tp_cumsum]
    else:
        tpr = [value / total_positive for value in tp_cumsum]

    if total_negative == 0:
        fpr = [0.0 for _ in fp_cumsum]
    else:
        fpr = [value / total_negative for value in fp_cumsum]

    return fpr, tpr


def compute_auc(fpr: Sequence[float], tpr: Sequence[float]) -> float:
    """Calcula el área bajo la curva con la regla del trapecio."""

    if not fpr or not tpr or len(fpr) != len(tpr):
        return 0.0

    area = 0.0
    for i in range(1, len(fpr)):
        base = fpr[i] - fpr[i - 1]
        height = tpr[i] + tpr[i - 1]
        area += base * height / 2

    return area


def _print_confusion_matrix(matrix: Sequence[Sequence[int]], labels: Sequence[int]) -> None:
    header = "\t".join([" "] + [str(label) for label in labels])
    print(header)
    for label, row in zip(labels, matrix):
        values = "\t".join(f"{value:3d}" for value in row)
        print(f"{label}\t{values}")


def main() -> None:
    X, y = load_dataset()
    print("Características (primeras 5 filas):")
    for row in X[:5]:
        print(" ", [f"{value:.2f}" for value in row])
    print("Etiquetas (primeros 10 valores):", y[:10])

    y_pred = predict_randomly(len(y), len(set(y)), seed=7)
    confusion_matrix, labels = compute_confusion_matrix(y, y_pred)
    print("\nMatriz de confusión:")
    _print_confusion_matrix(confusion_matrix, labels)

    precision = compute_precision(confusion_matrix)
    recall = compute_recall(confusion_matrix)
    f1 = compute_f1_score(precision, recall)

    print(f"\nPrecisión promedio: {precision:.3f}")
    print(f"Recall promedio: {recall:.3f}")
    print(f"F1-score: {f1:.3f}")

    rng = random.Random(42)
    y_binary = [rng.randrange(2) for _ in range(1000)]
    scores = [rng.random() for _ in range(1000)]

    fpr, tpr = compute_roc_curve(y_binary, scores)
    auc = compute_auc(fpr, tpr)
    print(f"\nAUC (predicciones aleatorias): {auc:.3f}")

    if _HAS_MATPLOTLIB and plt is not None:
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(exist_ok=True)
        plot_path = artifacts_dir / "roc_curve_random.png"

        plt.figure()
        plt.plot(fpr, tpr, label="Curva ROC")
        plt.plot([0, 1], [0, 1], "k--", label="Azar")
        plt.xlim(0.0, 1.0)
        plt.ylim(0.0, 1.0)
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title(f"ROC Curve (AUC = {auc:.2f})")
        plt.legend(loc="lower right")
        plt.savefig(plot_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Curva ROC guardada en: {plot_path}")
    else:
        print("Matplotlib no está disponible; se omite la generación de la curva ROC.")


if __name__ == "__main__":
    main()
