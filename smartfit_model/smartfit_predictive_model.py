"""Pipeline para predecir la cantidad de personas que entran a SmartFit en ventanas de 4 horas.

Este script entrena un modelo de machine learning usando datos históricos con variables
climáticas y de operación. El pipeline está pensado para funcionar con un archivo CSV que
contenga registros horarios (o con la frecuencia disponible) con al menos las columnas:

- ``timestamp``: fecha y hora de inicio del intervalo (ej. ``2024-05-01 06:00:00``).
- ``visitors_count``: número de personas que ingresaron durante ese intervalo.
- ``temperature_c``: temperatura promedio externa en grados Celsius.
- ``precipitation_mm``: precipitación acumulada en milímetros.
- ``is_holiday``: 1 si es feriado/fin de semana especial, 0 en caso contrario.
- ``marketing_push``: 1 si hubo promoción/campaña activa, 0 en caso contrario.

Puedes añadir más columnas numéricas o categóricas según la disponibilidad.

El pipeline:
1. Carga el archivo CSV.
2. Limpia datos faltantes.
3. Crea características derivadas (día de la semana, bloque de 4 horas, etc.).
4. Agrega los datos a ventanas de 4 horas.
5. Entrena un modelo ``HistGradientBoostingRegressor``.
6. Evalúa el modelo con validación cruzada y genera métricas.
7. Guarda el modelo entrenado y el transformador de características para uso futuro.

Uso:
```
python smartfit_predictive_model.py \
    --data smartfit_model/data/smartfit_hourly_visits_sample.csv \
    --model-out smartfit_model/models/smartfit_model.joblib \
    --transformer-out smartfit_model/models/smartfit_transformer.joblib
```

Los datos de ejemplo incluidos son ficticios. Reemplázalos por tus registros reales
exportados del sistema de control de acceso de SmartFit.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


FOUR_HOURS = pd.Timedelta(hours=4)


@dataclass
class TrainingArtifacts:
    """Objeto para agrupar artefactos del entrenamiento."""

    model: HistGradientBoostingRegressor
    transformer: ColumnTransformer
    feature_names: Iterable[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Entrena un modelo para predecir asistentes a SmartFit en ventanas de 4 horas."
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Ruta al CSV con datos históricos horarios de visitantes y variables exógenas.",
    )
    parser.add_argument(
        "--model-out",
        type=Path,
        default=Path("smartfit_model/models/smartfit_model.joblib"),
        help="Ruta donde se guardará el modelo entrenado.",
    )
    parser.add_argument(
        "--transformer-out",
        type=Path,
        default=Path("smartfit_model/models/smartfit_transformer.joblib"),
        help="Ruta donde se guardará el transformador de características.",
    )
    parser.add_argument(
        "--cv-folds",
        type=int,
        default=5,
        help="Número de folds para validación cruzada (por defecto 5).",
    )
    return parser.parse_args()


def load_hourly_data(csv_path: Path) -> pd.DataFrame:
    """Carga datos horarios desde un CSV."""
    df = pd.read_csv(csv_path, comment="#")
    if "timestamp" not in df.columns:
        raise ValueError("El CSV debe contener la columna 'timestamp'.")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=False)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def fill_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Rellena valores faltantes con estrategias simples."""
    filled = df.copy()
    numeric_cols = filled.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        filled[col] = filled[col].interpolate(limit_direction="both")
    categorical_cols = filled.select_dtypes(exclude=[np.number]).columns
    for col in categorical_cols:
        filled[col] = filled[col].fillna(method="ffill").fillna(method="bfill")
    return filled


def aggregate_to_four_hours(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa registros horarios a ventanas de 4 horas sumando los visitantes."""
    df = df.set_index("timestamp")
    visitors = df[["visitors_count"]].resample(FOUR_HOURS).sum()
    other_cols = df.drop(columns=["visitors_count"])

    aggregated = (
        other_cols.resample(FOUR_HOURS).mean()
        .join(visitors, how="inner")
        .dropna(subset=["visitors_count"])
        .reset_index()
    )

    aggregated.rename(columns={"timestamp": "window_start"}, inplace=True)
    aggregated["window_end"] = aggregated["window_start"] + FOUR_HOURS
    return aggregated


def engineer_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Genera características numéricas y categóricas para el modelo."""
    features = df.copy()
    features["day_of_week"] = features["window_start"].dt.day_name()
    features["hour_block"] = features["window_start"].dt.hour // 4
    features["is_weekend"] = features["window_start"].dt.dayofweek >= 5

    target = features.pop("visitors_count")
    return features, target


def build_pipeline(numeric_features: Iterable[str], categorical_features: Iterable[str]) -> Pipeline:
    """Construye el pipeline completo de preprocesamiento y modelo."""
    transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), list(numeric_features)),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                list(categorical_features),
            ),
        ]
    )

    model = HistGradientBoostingRegressor(
        learning_rate=0.1,
        max_depth=8,
        max_iter=300,
        min_samples_leaf=15,
        l2_regularization=0.01,
        random_state=42,
    )

    pipeline = Pipeline(steps=[("preprocessor", transformer), ("regressor", model)])
    return pipeline


def evaluate_pipeline(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series, cv_folds: int) -> dict:
    """Ejecuta validación cruzada y devuelve métricas promedio."""
    scoring = {
        "rmse": "neg_root_mean_squared_error",
        "mae": "neg_mean_absolute_error",
        "r2": "r2",
    }
    cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)
    scores = cross_validate(pipeline, X, y, cv=cv, scoring=scoring, return_train_score=False)

    metrics = {
        "rmse": -scores["test_rmse"].mean(),
        "mae": -scores["test_mae"].mean(),
        "r2": scores["test_r2"].mean(),
    }
    return metrics


def train_final_model(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> Pipeline:
    """Entrena el pipeline en todos los datos disponibles."""
    pipeline.fit(X, y)
    return pipeline


def save_artifacts(pipeline: Pipeline, model_path: Path, transformer_path: Path) -> TrainingArtifacts:
    """Guarda el modelo y el transformador en disco."""
    model: HistGradientBoostingRegressor = pipeline.named_steps["regressor"]
    transformer: ColumnTransformer = pipeline.named_steps["preprocessor"]

    model_path.parent.mkdir(parents=True, exist_ok=True)
    transformer_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, model_path)
    joblib.dump(transformer, transformer_path)

    feature_names = transformer.get_feature_names_out()
    return TrainingArtifacts(model=model, transformer=transformer, feature_names=feature_names)


def main() -> None:
    args = parse_args()
    df = load_hourly_data(args.data)
    df = fill_missing_values(df)
    df = aggregate_to_four_hours(df)
    X, y = engineer_features(df)

    numeric_features = [
        col
        for col in X.select_dtypes(include=[np.number]).columns
        if col not in {"is_weekend"}
    ]
    # ``is_weekend`` se trata como categórica aunque sea booleana para permitir one-hot.
    categorical_features = [
        col
        for col in X.columns
        if col not in numeric_features and col not in {"window_start", "window_end"}
    ]

    # Convertimos ventanas a características temporales basadas en segundos desde época.
    X = X.assign(
        window_start_ts=X["window_start"].astype("int64") // 10**9,
        window_end_ts=X["window_end"].astype("int64") // 10**9,
    )
    numeric_features.extend(["window_start_ts", "window_end_ts"])

    pipeline = build_pipeline(numeric_features=numeric_features, categorical_features=categorical_features)

    metrics = evaluate_pipeline(pipeline, X, y, cv_folds=args.cv_folds)
    print("Resultados de validación cruzada:")
    for metric, value in metrics.items():
        print(f"  {metric.upper()}: {value:.3f}")

    trained_pipeline = train_final_model(pipeline, X, y)

    artifacts = save_artifacts(
        trained_pipeline,
        model_path=args.model_out,
        transformer_path=args.transformer_out,
    )

    predictions = trained_pipeline.predict(X)
    rmse = mean_squared_error(y, predictions, squared=False)
    mae = mean_absolute_error(y, predictions)
    r2 = r2_score(y, predictions)

    print("\nMétricas finales sobre todos los datos disponibles:")
    print(f"  RMSE: {rmse:.3f}")
    print(f"  MAE: {mae:.3f}")
    print(f"  R^2: {r2:.3f}")

    print("\nArtefactos guardados:")
    print(f"  Modelo: {artifacts.model.__class__.__name__} -> {args.model_out}")
    print(f"  Transformador: ColumnTransformer -> {args.transformer_out}")
    print("  Características procesadas:")
    for feature in artifacts.feature_names:
        print(f"    - {feature}")


if __name__ == "__main__":
    main()
