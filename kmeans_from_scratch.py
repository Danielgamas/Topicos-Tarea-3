"""Implementation of K-means clustering from scratch using NumPy.

This script follows the workflow described in the prompt:
* Define a simple KMeans class with ``fit`` and ``predict`` methods.
* Generate a synthetic dataset with ``sklearn.datasets.make_blobs``.
* Train the model and relabel the clusters according to the true labels.
* Produce a classification report and persist a scatter plot with cluster
  assignments and centroids.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import importlib.util

matplotlib_spec = importlib.util.find_spec("matplotlib")
if matplotlib_spec is not None and importlib.util.find_spec("matplotlib.pyplot") is not None:
    import matplotlib.pyplot as plt
else:  # pragma: no cover - optional dependency branch
    plt = None
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import classification_report, confusion_matrix


@dataclass
class KMeans:
    """Simple K-means clustering implementation using NumPy only."""

    n_clusters: int = 2
    max_iter: int = 300
    tol: float = 1e-4
    random_state: Optional[int] = None

    centroids: Optional[np.ndarray] = None
    labels_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray) -> "KMeans":
        """Train the clustering model and determine the centroids.

        Parameters
        ----------
        X:
            Training features with shape ``(n_samples, n_features)``.
        """

        if self.n_clusters < 2:
            raise ValueError("KMeans requires at least two clusters.")

        X = np.asarray(X, dtype=float)
        n_samples = X.shape[0]

        if n_samples < self.n_clusters:
            raise ValueError("Number of samples must be >= number of clusters.")

        rng = np.random.default_rng(self.random_state)
        indices = rng.choice(n_samples, size=self.n_clusters, replace=False)
        self.centroids = X[indices]

        for _ in range(self.max_iter):
            distances = np.linalg.norm(X[:, np.newaxis, :] - self.centroids[np.newaxis, :, :], axis=2)
            labels = np.argmin(distances, axis=1)

            new_centroids = np.array(
                [
                    X[labels == i].mean(axis=0) if np.any(labels == i) else self.centroids[i]
                    for i in range(self.n_clusters)
                ]
            )

            if np.all(np.linalg.norm(new_centroids - self.centroids, axis=1) <= self.tol):
                self.centroids = new_centroids
                self.labels_ = labels
                break

            self.centroids = new_centroids
            self.labels_ = labels

        else:
            # Loop completed without break: ensure labels_ reflect last iteration
            self.labels_ = labels

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Assign the closest centroid to each sample in ``X``."""

        if self.centroids is None:
            raise ValueError("The model must be fitted before calling predict().")

        X = np.asarray(X, dtype=float)
        distances = np.linalg.norm(X[:, np.newaxis, :] - self.centroids[np.newaxis, :, :], axis=2)
        return np.argmin(distances, axis=1)


def relabel_clusters(true_labels: np.ndarray, predicted_labels: np.ndarray) -> np.ndarray:
    """Relabel predicted clusters to best match the true labels.

    Parameters
    ----------
    true_labels:
        Ground-truth class labels for each sample.
    predicted_labels:
        Cluster indices returned by the KMeans model.
    """

    conf_matrix = confusion_matrix(true_labels, predicted_labels)

    # If a cluster was never predicted, ``argmax`` would default to the first
    # row; guard against that by keeping the original label in that case.
    mapping = conf_matrix.argmax(axis=0)
    for predicted_cluster in range(conf_matrix.shape[1]):
        if conf_matrix[:, predicted_cluster].sum() == 0:
            mapping[predicted_cluster] = predicted_cluster

    relabeled = np.array([mapping[label] for label in predicted_labels], dtype=int)
    return relabeled


def main() -> None:
    X, y_true = make_blobs(n_samples=300, centers=5, cluster_std=0.6, random_state=0)

    model = KMeans(n_clusters=5, random_state=0)
    model.fit(X)
    y_pred = model.predict(X)
    y_pred = relabel_clusters(y_true, y_pred)

    print("Classification report for relabeled predictions:\n")
    print(classification_report(y_true, y_pred))

    if plt is not None:
        plt.figure(figsize=(8, 6))
        plt.scatter(X[:, 0], X[:, 1], c=y_pred, cmap="viridis", s=40, alpha=0.8)
        plt.scatter(
            model.centroids[:, 0],
            model.centroids[:, 1],
            s=200,
            c="red",
            marker="x",
            label="Centroids",
        )
        plt.title("K-means clustering results")
        plt.xlabel("Feature 1")
        plt.ylabel("Feature 2")
        plt.legend()

        plt.tight_layout()
        plt.savefig("kmeans_clusters.png", dpi=150)
        plt.close()

        print("Scatter plot saved to 'kmeans_clusters.png'.")
    else:
        print("Matplotlib is not available; skipping scatter plot generation.")


if __name__ == "__main__":
    main()
