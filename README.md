# Calculadora de Métodos Numéricos (GUI)

Aplicación interactiva desarrollada en Python con una interfaz moderna usando **CustomTkinter**.

## ¿Solo necesito el `.py`?
No. Para ejecutarlo correctamente necesitas:

- `app.py` (interfaz gráfica).
- `numerical_methods.py` (lógica matemática que usa la interfaz).
- Las dependencias de `requirements.txt` (`customtkinter`, `numpy`, `sympy`).

Si tienes solo `app.py`, fallará al importar `numerical_methods` y las librerías externas.

## Módulos incluidos

1. **Método de la Secante**
   - Entrada de función `f(x)` con sintaxis matemática (ejemplo: `x^2 + sin(x)`).
   - Valores iniciales `x0`, `x1` y tolerancia.
   - Salida de raíz aproximada y tabla de iteraciones.

2. **Método de Gauss-Seidel**
   - Tamaño dinámico del sistema `n x n`.
   - Captura de matriz de coeficientes `A`, vector `b`, tolerancia y máximo de iteraciones.
   - Salida de solución aproximada e historial iterativo.

3. **Interpolación de Lagrange**
   - Cantidad dinámica de puntos `(x, y)`.
   - Obtención del polinomio interpolante simbólico.
   - Evaluación del polinomio en un valor específico de `x`.

## Cómo correr el proyecto

### 1) Requisitos
- Python 3.10+ (recomendado).

### 2) Instalar dependencias

#### Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows (PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3) Ejecutar la app
```bash
python app.py
```

## Estructura

- `app.py`: interfaz gráfica y flujo de interacción.
- `numerical_methods.py`: lógica matemática modular.
- `requirements.txt`: dependencias del proyecto.
