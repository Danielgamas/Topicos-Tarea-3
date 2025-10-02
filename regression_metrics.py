import math
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


def main() -> None:
    data_path = Path(__file__).with_name("Salary_Data.csv")
    data = pd.read_csv(data_path)

    X = data[["YearsExperience"]]
    y = data["Salary"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    squared_errors = (y_test - y_pred) ** 2
    sum_squared_error = float(squared_errors.sum())
    mean_squared_error = sum_squared_error / len(y_test)
    root_mean_squared_error = math.sqrt(mean_squared_error)

    absolute_errors = (y_test - y_pred).abs()
    sum_absolute_error = float(absolute_errors.sum())
    mean_absolute_error = float(absolute_errors.mean())
    root_mean_absolute_error = math.sqrt(mean_absolute_error)

    residuals = y_test - y_pred
    explained_variance = float(residuals.var(ddof=0))
    total_variance = float(y_test.var(ddof=0))
    r_squared = 1.0 - explained_variance / total_variance

    print("Error cuadrático (SSE):", sum_squared_error)
    print("Error cuadrático medio (MSE):", mean_squared_error)
    print("Raíz del error cuadrático medio (RMSE):", root_mean_squared_error)
    print("Error absoluto (SAE):", sum_absolute_error)
    print("Error absoluto medio (MAE):", mean_absolute_error)
    print("Raíz del error absoluto medio (RMAE):", root_mean_absolute_error)
    print("Coeficiente de determinación (R^2):", r_squared)


if __name__ == "__main__":
    main()
