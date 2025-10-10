# Modelo predictivo de aforo para SmartFit

Este módulo incluye un pipeline en Python para estimar cuántas personas ingresarán a una
sucursal de SmartFit en ventanas de 4 horas a partir de datos históricos horarios. El flujo
de trabajo está pensado para que puedas reemplazar el CSV de ejemplo con tus propios datos
y entrenar un modelo de machine learning rápidamente.

## Estructura

```
smartfit_model/
├── data/
│   └── smartfit_hourly_visits_sample.csv  # Datos ficticios de ejemplo
├── smartfit_predictive_model.py           # Script principal de entrenamiento
└── requirements.txt                       # Dependencias necesarias
```

## Preparación del entorno

1. (Opcional) Crea y activa un entorno virtual.
2. Instala las dependencias:
   ```bash
   pip install -r smartfit_model/requirements.txt
   ```

## Entrenamiento

Ejecuta el script proporcionando la ruta a tu archivo CSV. En el repositorio se incluye un
ejemplo con datos simulados:

```bash
python smartfit_model/smartfit_predictive_model.py \
    --data smartfit_model/data/smartfit_hourly_visits_sample.csv \
    --model-out smartfit_model/models/smartfit_model.joblib \
    --transformer-out smartfit_model/models/smartfit_transformer.joblib \
    --cv-folds 3
```

El script mostrará las métricas de validación cruzada y guardará los artefactos entrenados
en la carpeta `smartfit_model/models/`.

## Adaptar a tus datos

- Asegúrate de que tu CSV contenga la columna `timestamp` y `visitors_count`.
- Puedes añadir columnas adicionales (por ejemplo, aforo máximo, temperatura interior,
  eventos locales, etc.). El pipeline detecta automáticamente las columnas numéricas y
  categóricas.
- Si tus datos ya están agregados en intervalos de 4 horas, puedes omitir la parte de
  resampleo ajustando la función `aggregate_to_four_hours` o reemplazándola por una que se
  adapte a tu estructura.

## Próximos pasos sugeridos

- Implementar un proceso de evaluación en un conjunto de prueba separado.
- Desplegar el modelo como servicio REST o programar un job de batch.
- Automatizar la actualización del modelo con nuevos datos cada semana.
