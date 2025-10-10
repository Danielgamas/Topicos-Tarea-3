"""Modelo predictivo para tiempos de entrega de última milla.

Este script simula un conjunto de datos con información geográfica,
características logísticas y contexto temporal para entrenar un modelo
de regresión que estime el tiempo de entrega. Además, evalúa el modelo
con métricas globales y desgloses por zona y horario.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, median_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class SimulationConfig:
    """Parámetros de la simulación."""

    n_samples: int = 5000
    random_state: int = 42

    # Coordenadas base para simular zonas dentro de una ciudad.
    city_center: Tuple[float, float] = (19.4326, -99.1332)  # Ciudad de México
    coord_jitter: float = 0.08

    # Distancia base en kilómetros.
    min_distance_km: float = 0.5
    max_distance_km: float = 18.0

    # Efectos en minutos según condiciones externas.
    weather_effects: dict[str, float] = None
    traffic_effects: dict[str, float] = None

    def __post_init__(self) -> None:
        if self.weather_effects is None:
            self.weather_effects = {
                "soleado": 0.0,
                "nublado": 4.0,
                "lluvia": 9.5,
                "tormenta": 16.0,
            }
        if self.traffic_effects is None:
            self.traffic_effects = {
                "bajo": -2.0,
                "medio": 0.0,
                "alto": 6.5,
            }


def generate_coordinates(
    base_lat: float, base_lon: float, jitter: float, size: int, rng: np.random.Generator
) -> Tuple[np.ndarray, np.ndarray]:
    """Genera coordenadas aleatorias alrededor de un punto base."""

    latitudes = rng.normal(loc=base_lat, scale=jitter, size=size)
    longitudes = rng.normal(loc=base_lon, scale=jitter, size=size)
    return latitudes, longitudes


def simulate_dataset(config: SimulationConfig) -> pd.DataFrame:
    """Crea un conjunto de datos sintético para entregas de última milla."""

    rng = np.random.default_rng(config.random_state)
    lat, lon = generate_coordinates(
        config.city_center[0], config.city_center[1], config.coord_jitter, config.n_samples, rng
    )

    distance_km = rng.uniform(config.min_distance_km, config.max_distance_km, config.n_samples)
    hour = rng.integers(6, 23, config.n_samples)
    day_of_week = rng.integers(0, 7, config.n_samples)

    weather = rng.choice(list(config.weather_effects.keys()), size=config.n_samples, p=[0.5, 0.25, 0.2, 0.05])
    traffic = rng.choice(list(config.traffic_effects.keys()), size=config.n_samples, p=[0.2, 0.55, 0.25])

    # Zona aproximada dentro de la ciudad basada en cuadrantes.
    zone_lat_bins = pd.qcut(lat, 4, labels=["norte", "centro_norte", "centro_sur", "sur"])
    zone_lon_bins = pd.qcut(lon, 4, labels=["oeste", "centro_oeste", "centro_este", "este"])
    zone = zone_lat_bins.astype(str) + "-" + zone_lon_bins.astype(str)

    base_speed_kmh = rng.normal(loc=18.0, scale=2.0, size=config.n_samples)

    weather_delay = np.vectorize(config.weather_effects.get)(weather)
    traffic_delay = np.vectorize(config.traffic_effects.get)(traffic)

    # Componente principal: tiempo = distancia / velocidad.
    base_time_hours = distance_km / np.clip(base_speed_kmh, 8, None)
    base_time_minutes = base_time_hours * 60

    # Impacto por hora (más tráfico en horas pico).
    peak_hour_penalty = np.where((hour >= 7) & (hour <= 9), 6.0, 0.0) + np.where(
        (hour >= 17) & (hour <= 20), 7.5, 0.0
    )

    weekend_bonus = np.where(day_of_week >= 5, -3.5, 0.0)

    noise = rng.normal(loc=0.0, scale=3.0, size=config.n_samples)

    delivery_time_min = (
        base_time_minutes
        + weather_delay
        + traffic_delay
        + peak_hour_penalty
        + weekend_bonus
        + noise
    )

    data = pd.DataFrame(
        {
            "latitud": lat,
            "longitud": lon,
            "distancia_km": distance_km,
            "clima": weather,
            "hora": hour,
            "dia_semana": day_of_week,
            "trafico": traffic,
            "zona": zone,
            "tiempo_entrega_min": delivery_time_min,
        }
    )

    return data


def build_model_pipeline() -> Pipeline:
    """Construye un pipeline de preprocesamiento y modelo."""

    numerical_features = ["latitud", "longitud", "distancia_km", "hora", "dia_semana"]
    categorical_features = ["clima", "trafico", "zona"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = GradientBoostingRegressor(random_state=42)

    pipeline = Pipeline(steps=[("preprocess", preprocessor), ("model", model)])
    return pipeline


def evaluate_by_group(
    y_true: pd.Series,
    y_pred: np.ndarray,
    groups: Iterable,
) -> pd.DataFrame:
    """Calcula MAE y MedAE por grupo definido."""

    df = pd.DataFrame({"grupo": groups, "y_true": y_true, "y_pred": y_pred})
    metrics = (
        df.groupby("grupo")
        .apply(
            lambda g: pd.Series(
                {
                    "MAE": mean_absolute_error(g["y_true"], g["y_pred"]),
                    "MedAE": median_absolute_error(g["y_true"], g["y_pred"]),
                    "n": len(g),
                }
            )
        )
        .sort_values("MAE")
    )
    return metrics


def compute_time_windows(hours: pd.Series) -> pd.Series:
    """Clasifica las horas en ventanas de tiempo relevantes."""

    bins = [-1, 6, 12, 18, 24]
    labels = ["madrugada", "mañana", "tarde", "noche"]
    return pd.cut(hours, bins=bins, labels=labels)


def main() -> None:
    config = SimulationConfig()
    data = simulate_dataset(config)

    train, test = train_test_split(
        data, test_size=0.25, random_state=config.random_state, stratify=data["zona"]
    )

    features = [
        "latitud",
        "longitud",
        "distancia_km",
        "clima",
        "hora",
        "dia_semana",
        "trafico",
        "zona",
    ]
    target = "tiempo_entrega_min"

    pipeline = build_model_pipeline()
    pipeline.fit(train[features], train[target])

    predictions = pipeline.predict(test[features])

    mae = mean_absolute_error(test[target], predictions)
    medae = median_absolute_error(test[target], predictions)

    print("Métricas globales:")
    print(f"\tMAE: {mae:.2f} minutos")
    print(f"\tMedAE: {medae:.2f} minutos")

    zone_metrics = evaluate_by_group(test[target], predictions, test["zona"])
    print("\nError por zona:")
    print(zone_metrics)

    time_windows = compute_time_windows(test["hora"])
    time_metrics = evaluate_by_group(test[target], predictions, time_windows)
    print("\nError por ventana horaria:")
    print(time_metrics)


if __name__ == "__main__":
    main()
