"""Script de tratamiento de datos basado en el flujo descrito en el enunciado.

Este módulo carga un archivo CSV con información demográfica y económica,
limpia los datos aplicando un pipeline de pandas y muestra un resumen
estadístico e información general del resultado.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd


def ensure_numeric(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Intenta convertir ``column`` a un tipo numérico."""
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def remove_negative_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Reemplaza los valores negativos de ``column`` por ``NaN``.

    Parameters
    ----------
    df:
        DataFrame original.
    column:
        Nombre de la columna numérica a procesar.
    """
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    df[column] = df[column].apply(lambda x: np.nan if pd.notna(x) and x < 0 else x)
    return df


def remove_outliers_with_z_score(
    df: pd.DataFrame, column: str, threshold: float = 2.0
) -> pd.DataFrame:
    """Sustituye outliers usando la puntuación Z.

    Todo valor cuya distancia absoluta a la media supere ``threshold``
    desviaciones estándar se reemplaza por la media de la columna.
    """
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    series = df[column]
    if series.empty:
        return df

    mean = series.mean()
    std = series.std()

    if std == 0 or np.isnan(std):
        # Si no hay variabilidad, no hay outliers que reemplazar.
        return df

    z_score = (series - mean) / std
    mask = z_score.abs() > threshold
    df.loc[mask, column] = mean
    return df


def map_column_values(
    df: pd.DataFrame, column: str, mapping_dict: Dict[str, Any]
) -> pd.DataFrame:
    """Normaliza valores categóricos utilizando ``mapping_dict``.

    Los valores se pasan a minúsculas y se eliminan espacios sobrantes
    antes de consultarlos en el diccionario. Cuando un valor no aparece en
    ``mapping_dict`` se devuelve el texto original limpiado. Los valores
    nulos permanecen como ``NaN``.
    """
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    def _map(value: Any) -> Any:
        if pd.isna(value):
            return np.nan
        cleaned = str(value).strip().lower()
        return mapping_dict.get(cleaned, str(value).strip())

    df[column] = df[column].apply(_map)
    return df


def fill_na_in_column(df: pd.DataFrame, column: str, value: Any) -> pd.DataFrame:
    """Rellena ``NaN`` en ``column`` con ``value``."""
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    df[column] = df[column].fillna(value)
    return df


def fill_na_with_statistic(
    df: pd.DataFrame, column: str, strategy: str = "median"
) -> pd.DataFrame:
    """Imputa valores faltantes utilizando la estadística indicada."""
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    series = df[column]
    if strategy == "median":
        value = series.median()
    elif strategy == "mean":
        value = series.mean()
    elif strategy == "mode":
        mode_series = series.mode(dropna=True)
        value = mode_series.iat[0] if not mode_series.empty else np.nan
    else:
        raise ValueError("Estrategia no soportada. Usa 'median', 'mean' o 'mode'.")

    df[column] = series.fillna(value)
    return df


def cast_column_type(df: pd.DataFrame, column: str, dtype: str) -> pd.DataFrame:
    """Fuerza el tipo de dato de ``column`` a ``dtype`` si existe."""
    if column not in df.columns:
        raise KeyError(f"La columna '{column}' no existe en el DataFrame")

    target_dtype = np.dtype(dtype)
    if np.issubdtype(target_dtype, np.integer):
        df[column] = df[column].round().astype(dtype)
    else:
        df[column] = df[column].astype(dtype)
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta el pipeline de limpieza sobre ``df``."""
    education_mapping: Dict[str, Any] = {
        "bachelor": "Bachelor",
        "bachelors": "Bachelor",
        "master": "Master",
        "mre": "Master",
        "phd": "PhD",
        "no education": "No education",
        "none": "No education",
        "": np.nan,
    }

    gender_mapping: Dict[str, Any] = {
        "masculino": "Masculino",
        "femenino": "Femenino",
        "m": "Masculino",
        "f": "Femenino",
    }

    processed = (
        df.pipe(ensure_numeric, "edad")
        .pipe(ensure_numeric, "ingresos")
        .pipe(ensure_numeric, "altura")
        .pipe(ensure_numeric, "hijos")
        .pipe(remove_negative_values, "edad")
        .pipe(remove_negative_values, "ingresos")
        .pipe(remove_negative_values, "hijos")
        .pipe(remove_outliers_with_z_score, "edad", threshold=3.0)
        .pipe(remove_outliers_with_z_score, "ingresos", threshold=3.0)
        .pipe(remove_outliers_with_z_score, "altura", threshold=3.0)
        .pipe(remove_outliers_with_z_score, "hijos", threshold=3.0)
        .pipe(map_column_values, "nivel_educacion", education_mapping)
        .pipe(map_column_values, "genero", gender_mapping)
        .pipe(fill_na_with_statistic, "edad", strategy="median")
        .pipe(fill_na_with_statistic, "ingresos", strategy="median")
        .pipe(fill_na_with_statistic, "altura", strategy="median")
        .pipe(fill_na_with_statistic, "hijos", strategy="median")
        .pipe(fill_na_in_column, "nivel_educacion", "No education")
        .pipe(fill_na_with_statistic, "genero", strategy="mode")
        .pipe(fill_na_with_statistic, "ciudad", strategy="mode")
        .pipe(fill_na_in_column, "genero", "No especificado")
        .pipe(fill_na_in_column, "ciudad", "Desconocida")
        .pipe(cast_column_type, "edad", "int64")
        .pipe(cast_column_type, "hijos", "int64")
        .pipe(cast_column_type, "ingresos", "float64")
        .pipe(cast_column_type, "altura", "float64")
    )

    return processed


def load_dataset(path: Path) -> pd.DataFrame:
    """Carga un archivo CSV en un ``DataFrame``."""
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    return pd.read_csv(path, index_col=0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline de tratamiento de datos")
    parser.add_argument(
        "csv_path",
        type=Path,
        nargs="?",
        default=Path("data/dataset1.csv"),
        help="Ruta al archivo CSV a procesar",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/dataset1_limpio.csv"),
        help="Ruta donde se guardará el CSV limpio",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataset(args.csv_path)
    cleaned = preprocess_data(df.copy())

    cleaned.to_csv(args.output)

    # Mostrar un resumen rápido por consola.
    print("DESCRIPCIÓN ESTADÍSTICA:\n", cleaned.describe(include="all"))
    print("\nINFO DEL DATAFRAME:")
    cleaned.info()


if __name__ == "__main__":
    main()
