"""Demonstration of categorical encoding techniques with pandas and scikit-learn."""
from __future__ import annotations

from typing import Iterable

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder


def build_sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame with categorical employee information."""
    data = {
        "Cargo": ["Gerente", "Analista", "Asistente", "Gerente", "Analista", "Asistente"],
        "Departamento": [
            "Ventas",
            "Marketing",
            "Recursos Humanos",
            "Ventas",
            "Marketing",
            "Recursos Humanos",
        ],
        "Ubicacion": ["Norte", "Sur", "Norte", "Sur", "Este", "Oeste"],
    }
    return pd.DataFrame(data)


def one_hot_encode(df: pd.DataFrame) -> pd.DataFrame:
    """Apply scikit-learn's OneHotEncoder to the DataFrame."""
    encoder = OneHotEncoder(sparse=False)
    transformed = encoder.fit_transform(df)
    feature_names = encoder.get_feature_names_out(df.columns)
    return pd.DataFrame(transformed, columns=feature_names)


def pandas_get_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode categorical columns using pandas.get_dummies."""
    return pd.get_dummies(df)


def label_encode(df: pd.DataFrame) -> pd.DataFrame:
    """Apply LabelEncoder column by column, producing ordinal values."""
    df_encoded = df.copy()
    for column in df_encoded.columns:
        encoder = LabelEncoder()
        df_encoded[column] = encoder.fit_transform(df_encoded[column])
    return df_encoded


def ordinal_encode(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Apply OrdinalEncoder to the selected columns."""
    df_encoded = df.copy()
    encoder = OrdinalEncoder()
    df_encoded[list(columns)] = encoder.fit_transform(df_encoded[list(columns)])
    return df_encoded


def custom_label_encode(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Custom implementation of label encoding using mapping dictionaries."""
    df_encoded = df.copy()
    for column in columns:
        unique_values = df_encoded[column].unique()
        value_to_int = {value: idx for idx, value in enumerate(unique_values)}
        df_encoded[f"{column}_encoded"] = df_encoded[column].replace(value_to_int)
    return df_encoded


def main() -> None:
    df = build_sample_dataframe()
    print("DataFrame original:\n", df, "\n", sep="")

    df_one_hot = one_hot_encode(df)
    print("OneHotEncoder (scikit-learn):\n", df_one_hot, "\n", sep="")
    print("Shape tras OneHotEncoder:", df_one_hot.shape, "\n")

    df_dummies = pandas_get_dummies(df)
    print("pandas.get_dummies:\n", df_dummies, "\n", sep="")

    df_label = label_encode(df)
    print("LabelEncoder columna por columna:\n", df_label, "\n", sep="")

    df_ordinal = ordinal_encode(df, ["Cargo", "Departamento", "Ubicacion"])
    print("OrdinalEncoder con múltiples columnas:\n", df_ordinal, "\n", sep="")

    df_custom = custom_label_encode(df, ["Cargo", "Departamento", "Ubicacion"])
    print("Label encoding personalizado:\n", df_custom, "\n", sep="")


if __name__ == "__main__":
    main()
