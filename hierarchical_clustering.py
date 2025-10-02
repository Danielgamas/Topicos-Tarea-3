"""Implementación simple de clustering jerárquico aglomerativo.

Incluye una clase para realizar agrupamiento y un ejemplo de uso
con datos sintéticos generados mediante ``make_blobs`` de scikit-learn.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class HierarchicalClustering:
    """Implementación básica del clustering jerárquico aglomerativo.

    Parameters
    ----------
    n_clusters:
        Número de clústeres a generar.
    """

    n_clusters: int
    clusters_: List[List[int]] | None = None
    centroids_: np.ndarray | None = None

    def fit(self, X: np.ndarray) -> "HierarchicalClustering":
        """Ajusta el modelo a los datos ``X``.

        Parameters
        ----------
        X:
            Matriz de características con forma ``(n_muestras, n_features)``.
        """

        if X.ndim != 2:
            raise ValueError("X debe ser una matriz bidimensional")

        n_samples = X.shape[0]
        self.clusters_ = [[i] for i in range(n_samples)]

        # Matriz de distancias completa entre todos los puntos.
        distance_matrix = np.linalg.norm(
            X[:, np.newaxis, :] - X[np.newaxis, :, :], axis=2
        )

        while len(self.clusters_) > self.n_clusters:
            min_dist = np.inf
            pair: Tuple[int | None, int | None] = (None, None)

            for i in range(len(self.clusters_)):
                for j in range(i + 1, len(self.clusters_)):
                    dist = np.min(
                        distance_matrix[np.ix_(self.clusters_[i], self.clusters_[j])]
                    )
                    if dist < min_dist:
                        min_dist = dist
                        pair = (i, j)

            i, j = pair
            if i is None or j is None:
                break

            self.clusters_[i].extend(self.clusters_[j])
            self.clusters_.pop(j)

        self.centroids_ = np.array(
            [X[cluster].mean(axis=0) for cluster in self.clusters_]
        )
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Asigna etiquetas al nuevo conjunto de datos ``X``."""

        if self.centroids_ is None:
            raise ValueError("Debes entrenar el modelo con 'fit' antes de predecir")

        distances = np.linalg.norm(
            X[:, np.newaxis, :] - self.centroids_[np.newaxis, :, :], axis=2
        )
        return np.argmin(distances, axis=1)

    def relabel(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Alinea etiquetas predichas con las verdaderas usando mayoría."""

        mapping: Dict[int, int] = {}
        for cluster_idx in range(self.n_clusters):
            mask = y_pred == cluster_idx
            if np.any(mask):
                majority = np.bincount(y_true[mask]).argmax()
                mapping[cluster_idx] = majority
        return np.vectorize(lambda c: mapping.get(c, c))(y_pred)


def _run_example() -> None:
    """Ejecuta un ejemplo con datos sintéticos."""

    try:
        from sklearn.datasets import make_blobs
        from sklearn.metrics import classification_report
    except ModuleNotFoundError as exc:  # pragma: no cover - dependencia opcional
        raise SystemExit(
            "scikit-learn es necesario para ejecutar el ejemplo de uso"
        ) from exc

    X, y = make_blobs(
        n_samples=100, centers=2, cluster_std=0.95, random_state=42
    )

    model = HierarchicalClustering(n_clusters=2).fit(X)
    labels = model.predict(X)
    labels = model.relabel(y, labels)

    print(classification_report(y, labels))

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print(
            "matplotlib no está instalado; omitiendo la visualización del gráfico."
        )
        return

    plt.figure(figsize=(6, 5))
    plt.scatter(X[:, 0], X[:, 1], c=labels, cmap="viridis", s=40)
    plt.title("Clustering jerárquico aglomerativo")
    plt.xlabel("x₁")
    plt.ylabel("x₂")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    _run_example()
