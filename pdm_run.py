"""pdm_run.py — Predictive Maintenance (falla en 72h) end-to-end demo.

Este script genera un conjunto de datos sintético de sensores, entrena un
clasificador de bosques aleatorios y reporta métricas enfocadas en el
horizonte de 72 horas. El objetivo es contar con un ejemplo reproducible
para probar un pipeline básico de mantenimiento predictivo.

Uso:
    python pdm_run.py

Salida:
    - datasets/ (CSV simulados)
    - models/ (modelo entrenado en joblib)
    - figures/ (curva Precision-Recall)
    - métricas en consola (classification_report y PR-AUC)
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_dependencies() -> None:
    """Verifica dependencias requeridas e imprime instrucciones si faltan."""
    missing = []
    for module, package in {
        "numpy": "numpy",
        "pandas": "pandas",
        "sklearn": "scikit-learn",
        "matplotlib": "matplotlib",
    }.items():
        try:
            __import__(module)
        except ModuleNotFoundError:
            missing.append((module, package))

    if missing:
        print("\n[ERROR] Dependencias faltantes detectadas:\n", file=sys.stderr)
        for module, package in missing:
            print(f"  - Módulo '{module}' (instala con: pip install {package})", file=sys.stderr)

        print(
            "\nInstala las dependencias ejecutando:\n"
            "  pip install -r requirements.txt\n"
            "o instala los paquetes listados individualmente.\n",
            file=sys.stderr,
        )
        raise SystemExit(1)


def main() -> None:
    _ensure_dependencies()

    import numpy as np
    import pandas as pd
    from datetime import datetime  # noqa: F401 - importado para compatibilidad con el código original
    import os  # noqa: F401 - importado para compatibilidad con el código original

    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        average_precision_score,
        classification_report,
        precision_recall_curve,
    )
    from sklearn.model_selection import train_test_split  # noqa: F401 - mantenido por claridad histórica
    import sklearn
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    import matplotlib
    import matplotlib.pyplot as plt

    try:
        import joblib
    except ModuleNotFoundError:
        joblib = None

    print("=== Dependencias detectadas ===")
    print(f"numpy: {np.__version__}")
    print(f"pandas: {pd.__version__}")
    print(f"scikit-learn: {sklearn.__version__}")
    print(f"matplotlib: {matplotlib.__version__}")
    if joblib is not None:
        print(f"joblib: {joblib.__version__}")
    else:
        print("joblib: no disponible (se omitirá el guardado del modelo)")

    np.random.seed(42)

    DATA_DIR = Path("datasets")
    MODEL_DIR = Path("models")
    FIG_DIR = Path("figures")
    for directory in (DATA_DIR, MODEL_DIR, FIG_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    # 1) Simulación de datos (3 equipos, 3 meses, cada 5 min)
    start = pd.Timestamp("2025-01-01 00:00:00")
    end = pd.Timestamp("2025-03-31 23:55:00")
    freq = "5min"
    time_index = pd.date_range(start, end, freq=freq)

    equipos = [
        {"id_equipo": "MOTOR_A", "rpm_base": 1750, "crit": 5},
        {"id_equipo": "BOMBA_B", "rpm_base": 2950, "crit": 4},
        {"id_equipo": "RODILLO_C", "rpm_base": 1200, "crit": 3},
    ]

    def inject_failures(series_len, fail_count, horizon_hours, step_eff=1.0):
        margin = int((horizon_hours * 60) / 5) + 24
        cand = np.arange(margin, series_len - margin)
        fail_idxs = np.sort(np.random.choice(cand, size=fail_count, replace=False))
        mask_deterioration = np.zeros(series_len, dtype=float)
        for fx in fail_idxs:
            w = int((horizon_hours * 60) / 5)
            ramp = np.linspace(0, 1, w)
            start_fail = fx - w
            mask_deterioration[start_fail:fx] += ramp * step_eff
        return fail_idxs, mask_deterioration

    rows, eventos = [], []
    for equipo in equipos:
        n = len(time_index)
        ambient = 20 + 8 * np.sin(2 * np.pi * (np.arange(n) / (24 * 12)))
        load = 0.5 + 0.5 * np.sin(2 * np.pi * (np.arange(n) / (7 * 24 * 12)))
        load = (load - load.min()) / (load.max() - load.min())

        temp = 55 + 6 * load + ambient * 0.15 + np.random.normal(0, 0.7, n)
        vibr = 1.5 + 0.8 * load + np.random.normal(0, 0.2, n)
        current = 60 + 8 * load + np.random.normal(0, 1.0, n)
        rpm = (
            equipo["rpm_base"]
            + 10 * np.sin(2 * np.pi * (np.arange(n) / 60))
            + np.random.normal(0, 3, n)
        )

        fail_count = np.random.randint(4, 7)
        W_hours = 72
        fail_indexes, deterioration = inject_failures(
            n, fail_count, horizon_hours=W_hours, step_eff=1.4
        )

        temp = temp + 6.0 * deterioration
        vibr = vibr + 1.2 * deterioration
        current = current + 2.0 * deterioration

        for fail_index in fail_indexes:
            ts_falla = time_index[fail_index]
            eventos.append(
                {
                    "id_equipo": equipo["id_equipo"],
                    "ts_inicio": ts_falla,
                    "ts_fin": ts_falla
                    + pd.Timedelta(hours=float(np.random.uniform(2, 8))),
                    "tipo_evento": "falla",
                    "causa": np.random.choice(
                        [
                            "rodamientos",
                            "sobrecalentamiento",
                            "desalineación",
                            "cavitación",
                        ]
                    ),
                    "costo": float(np.random.randint(800, 5000)),
                }
            )

        df_equipo = pd.DataFrame(
            {
                "ts": time_index,
                "id_equipo": equipo["id_equipo"],
                "temp_c": temp,
                "vibr_rms": vibr,
                "corriente_a": current,
                "rpm": rpm,
                "turno": np.where(
                    (time_index.hour >= 6) & (time_index.hour < 14),
                    "M1",
                    np.where(
                        (time_index.hour >= 14) & (time_index.hour < 22),
                        "M2",
                        "N",
                    ),
                ),
            }
        )
        rows.append(df_equipo)

    sensores_raw = pd.concat(rows, ignore_index=True)
    events_df = pd.DataFrame(eventos)

    # 2) Etiquetado (falla en próximas 72h)
    events_df["ts_inicio"] = pd.to_datetime(events_df["ts_inicio"])
    horizon = pd.Timedelta(hours=72)

    labels = []
    for eq_id, df_eq in sensores_raw.groupby("id_equipo"):
        df_eq = df_eq.sort_values("ts").copy()
        fail_times = (
            events_df.loc[events_df["id_equipo"] == eq_id, "ts_inicio"]
            .sort_values()
            .to_numpy()
        )
        y = np.zeros(len(df_eq), dtype=int)
        ft_idx = 0
        ts_vals = df_eq["ts"].to_numpy()
        for i, current_ts in enumerate(ts_vals):
            while ft_idx < len(fail_times) and fail_times[ft_idx] < current_ts:
                ft_idx += 1
            if ft_idx < len(fail_times) and fail_times[ft_idx] <= current_ts + horizon:
                y[i] = 1
        df_eq["y_falla_72h"] = y
        labels.append(df_eq)

    labeled = pd.concat(labels, ignore_index=True)

    # 3) Features (rolling index-based: 12=1h, 72=6h)
    def add_features(group_df):
        group_df = group_df.sort_values("ts").reset_index(drop=True)
        for col in ["temp_c", "vibr_rms", "corriente_a"]:
            group_df[f"{col}_mean_1h"] = group_df[col].rolling(12, min_periods=12).mean()
            group_df[f"{col}_std_1h"] = group_df[col].rolling(12, min_periods=12).std()
            group_df[f"{col}_mean_6h"] = group_df[col].rolling(72, min_periods=72).mean()
            group_df[f"{col}_delta_1h"] = group_df[col] - group_df[col].shift(12)
            group_df[f"{col}_slope_6h"] = (group_df[col] - group_df[col].shift(72)) / 72.0
        group_df["hora"] = group_df["ts"].dt.hour
        group_df["dia_semana"] = group_df["ts"].dt.dayofweek
        return group_df

    features = (
        labeled.groupby("id_equipo", group_keys=False).apply(add_features).dropna().reset_index(drop=True)
    )

    # Guardar datasets
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sensores_raw.to_csv(DATA_DIR / "sensores_raw.csv", index=False)
    events_df.to_csv(DATA_DIR / "eventos.csv", index=False)
    features.to_csv(DATA_DIR / "features_labels.csv", index=False)

    # 4) Train/Test temporal (80/20 por fecha)
    df = features.sort_values(["id_equipo", "ts"]).reset_index(drop=True)
    cut = df["ts"].quantile(0.8)
    train_df = df[df["ts"] < cut].copy()
    test_df = df[df["ts"] >= cut].copy()

    target = "y_falla_72h"
    num_cols = [
        col
        for col in df.columns
        if any(col.startswith(prefix) for prefix in ["temp_c", "vibr_rms", "corriente_a"])
        and any(tag in col for tag in ("mean_", "std_", "delta_", "slope_"))
    ]
    num_cols += ["hora", "dia_semana"]
    cat_cols = ["turno", "id_equipo"]

    X_train = train_df[num_cols + cat_cols]
    y_train = train_df[target].values
    X_test = test_df[num_cols + cat_cols]
    y_test = test_df[target].values

    preprocessor = ColumnTransformer(
        [
            ("num", StandardScaler(), num_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
        class_weight="balanced_subsample",
    )

    pipeline = Pipeline([("pre", preprocessor), ("clf", clf)])
    pipeline.fit(X_train, y_train)

    proba = pipeline.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    # 5) Métricas y curvas
    from sklearn.metrics import classification_report as sk_classification_report

    print("\n=== Classification Report (Test) ===")
    print(sk_classification_report(y_test, pred, digits=3))

    ap = average_precision_score(y_test, proba)
    print("Average Precision (PR-AUC):", round(ap, 4))

    precision, recall, _ = precision_recall_curve(y_test, proba)
    plt.figure()
    plt.plot(recall, precision)
    plt.title("Precision-Recall Curve (Test)")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.grid(True, alpha=0.3)
    fig_path = FIG_DIR / "pr_curve_test.png"
    plt.savefig(fig_path, bbox_inches="tight")
    print(f"Guardada curva PR en: {fig_path}")

    # 6) Persistir modelo si joblib está disponible
    if joblib is not None:
        model_path = MODEL_DIR / "rf_pdm_pipeline.joblib"
        joblib.dump(pipeline, model_path)
        print(f"Modelo guardado en: {model_path}")
    else:
        print("joblib no disponible; omitiendo guardado de modelo.")

    print("\nListo. Datasets en 'datasets/', figuras en 'figures/', modelo en 'models/'.")


if __name__ == "__main__":
    main()
