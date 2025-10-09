# Proyecto 12: Mantenimiento predictivo en línea de producción

## Objetivo general
Reducir paros no planeados y los costos asociados al mantenimiento mediante la predicción anticipada de fallas en equipos críticos (bombas, motores, rodillos, hornos, CNC, etc.).

## Enfoques del problema
- **Clasificación binaria**: predecir si ocurrirá una falla en las próximas \( W \) horas para activar órdenes de trabajo preventivas.
- **Supervivencia / Tiempo-a-falla (RUL)**: estimar el tiempo restante de vida del equipo y optimizar calendarios de mantenimiento.
- **Detección de anomalías**: aprender el comportamiento normal cuando hay pocas etiquetas de fallas y alertar desviaciones significativas.

## Datos mínimos necesarios
- **Sensores**: `timestamp`, `id_equipo`, temperatura, vibración (RMS/FFT), corriente, voltaje, presión, caudal, rpm.
- **Eventos**: fallas, mantenimientos correctivo/preventivo (tipo, duración, costo).
- **Contexto**: turno, producto, carga de trabajo, ambiente.
- **Catálogo**: información del equipo, ubicación, criticidad.
- **Granularidad**: datos agregados y sincronizados a 1 minuto; horizonte típico \( W \) entre 24 y 168 horas.

## Ingeniería de características
- **Rollups temporales**: media, desviación estándar, mínimos/máximos, percentiles (pXX) en ventanas de {5, 15, 60, 360} minutos.
- **Tendencias**: pendientes mediante regresiones móviles, deltas, z-scores, EWMA.
- **Espectro de vibración**: picos en bandas 1x, 2x, 3x rpm; curtosis, factor de cresta.
- **Variables eléctricas**: factor de potencia, THD.
- **Carga/Producción**: piezas por hora, porcentaje de utilización, cambios de receta.
- **Historial de mantenimiento**: tiempo desde el último servicio, tipo de servicio.
- **Calendario y ambiente**: turno, día de semana, temperatura ambiental.

## Etiquetado para clasificadores
- Etiquetar con 1 toda muestra en el intervalo \([t_{falla}-W, t_{falla})\).
- Etiquetar con 0 las muestras fuera de la ventana anterior.
- Excluir un buffer posterior a la falla (12–24 h) para evitar contaminación de datos.

## Modelos recomendados
- **Clasificación**: XGBoost, LightGBM, Random Forest.
- **Supervivencia**: Cox Proportional Hazards, Random Survival Forest, LGBM-Cox.
- **Secuenciales**: LSTM o 1D-CNN con ventanas deslizantes para historiales largos.
- **Anomalías**: Isolation Forest, One-Class SVM, Autoencoders.

## Validación y métricas
- Validación con particiones temporales (TimeSeriesSplit).
- **Clasificación**: PR-AUC, Recall@k, F1, métricas ponderadas por costo.
- **Supervivencia**: C-index, sMAPE del RUL por horizonte.
- **Anomalías**: equilibrio entre detecciones tempranas y falsos positivos por día.

## Optimización de umbral y costos
- Definir costo de falso positivo (CFP) y falso negativo (CFN).
- Ajustar el umbral para minimizar \( CFP \cdot FP + CFN \cdot FN \).
- Reportar ROI: horas de paro evitadas, MTBF incrementado, MTTR reducido, ahorro anual.

## Pipeline sugerido
1. Ingesta y sincronización de sensores; remuestreo a 1 min.
2. Limpieza: imputación de huecos cortos, eliminación de outliers imposibles.
3. Generación de *feature store* con ventanas y transformadas FFT (vibración).
4. Etiquetado según ventana \( W \).
5. Separación temporal en train/valid/test con escalado dentro de `Pipeline`.
6. Entrenamiento de modelo (p. ej. LightGBM) con búsqueda de hiperparámetros.
7. Calibración de probabilidades (Platt o isotónica) y análisis de SHAP.
8. Despliegue: job periódico que calcula nuevas características, puntúa y emite alertas.
9. Monitoreo: drift de datos, PR-AUC mensual, tasa de alertas por semana.

## Esquema de tablas de datos
- `sensores_raw(id_equipo, ts, temp, vibr, corriente, volt, rpm, ...)`
- `eventos(id_equipo, ts_inicio, ts_fin, tipo_evento, causa, costo)`
- `features_min(id_equipo, ts, temp_mean_15m, vibr_rms_5m, fft_1x, slope_temp_1h, ...)`
- `labels(id_equipo, ts, y_binaria, rul_horas)`
- `predicciones(id_equipo, ts, score, alerta_bool, umbral, version_modelo)`
- `alertas(id_alerta, id_equipo, ts, score, motivo_top_features, estatus)`

## Baseline de comparación
- Regla heurística: alerta si `temp` > p95 o `vibr_rms` aumenta más de 3σ.
- El modelo debe superar al baseline en PR-AUC y costo total.

## Entregables sugeridos
- Notebook reproducible (EDA, features, modelo, métricas).
- Dashboard (Streamlit/Gradio) con scoring en tiempo real por equipo.
- Reporte ejecutivo (2–3 páginas) con objetivo, datos, features relevantes, PR-AUC y ROI estimado.
- Guía operativa con criterios de intervención y procedimientos.

## Mini-roadmap (8 pasos)
1. Seleccionar 1–3 equipos críticos.
2. Recolectar 3–6 meses de sensores e historial de fallas.
3. Definir horizonte \( W \) (ej. 72 h).
4. Generar features y etiquetas.
5. Entrenar LightGBM (clasificación) y ajustar umbral por costos.
6. Validar con TimeSeriesSplit y medir PR-AUC.
7. Implementar API/servicio de scoring y alertas.
8. Medir MTBF, paros evitados y ahorro en un piloto de 1 mes.
