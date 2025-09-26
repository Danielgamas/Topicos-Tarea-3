"""Data normalization utilities with optional plotting support.

This module generates random data, applies min-max and standard
normalization, and plots the results when Matplotlib is available.
It avoids failing when Matplotlib is not installed by checking for
its availability before attempting to import pyplot.
"""
from __future__ import annotations

import importlib.util
import random
from statistics import mean, pstdev
from typing import Iterable, List


MATPLOTLIB_AVAILABLE = importlib.util.find_spec("matplotlib") is not None
if MATPLOTLIB_AVAILABLE:
    import matplotlib.pyplot as plt  # type: ignore
else:  # pragma: no cover - defensive logging branch
    plt = None


NumberList = List[float]


def min_max_scaler(data: NumberList) -> NumberList:
    """Scale ``data`` to the [0, 1] range using min-max normalization."""
    if not data:
        return []
    data_min = min(data)
    data_max = max(data)
    range_ = data_max - data_min
    if range_ == 0:
        return [0.0 for _ in data]
    return [(value - data_min) / range_ for value in data]


def standard_scaler(data: NumberList) -> NumberList:
    """Standardize ``data`` to have zero mean and unit variance."""
    if not data:
        return []
    data_mean = mean(data)
    data_std = pstdev(data)
    if data_std == 0:
        return [0.0 for _ in data]
    return [(value - data_mean) / data_std for value in data]


def _generate_sample_data(size: int = 1_000) -> NumberList:
    """Generate reproducible random data in the range [-50, 50)."""
    rng = random.Random(42)
    return [rng.random() * 100 - 50 for _ in range(size)]


def _plot_series(series: Iterable[float], title: str) -> None:
    """Plot ``series`` if Matplotlib is installed, otherwise log a message."""
    if plt is None:
        print(f"Matplotlib no está instalado. Saltando la gráfica: {title}.")
        return
    plt.figure()
    plt.plot(list(series))
    plt.title(title)
    plt.show()


def main() -> None:
    """Generate data, normalize it, and display the results."""
    data = _generate_sample_data()
    _plot_series(data, "Datos originales")

    norm_data = min_max_scaler(data)
    _plot_series(norm_data, "Datos normalizados (min-max)")

    std_data = standard_scaler(data)
    _plot_series(std_data, "Datos estandarizados")


if __name__ == "__main__":
    main()
