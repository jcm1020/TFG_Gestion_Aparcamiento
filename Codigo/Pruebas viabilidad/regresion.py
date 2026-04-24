# Estudio de outliers en un problema ficticio con regresion
# En nuestro proyecto los outliers seran los objetos reconocidos no alineados en una linea de una red
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def analizar_regresion(x, y, umbral_z=2):
    # Convertimos a DataFrame
    data = pd.DataFrame({"x": x, "y": y})
    
    # 1. Entrenamiento de la regresión lineal
    modelo = LinearRegression()
    modelo.fit(data[["x"]], data["y"])
    
    pendiente = modelo.coef_[0]
    intercepto = modelo.intercept_
    print("Pendiente (a):", pendiente)
    print("Intercepto (b):", intercepto)
    
    # Predicciones de la recta
    y_pred = modelo.predict(data[["x"]])
    
    # 2. Cálculo de residuos (distancia a la recta)
    residuos = data["y"] - y_pred
    
    # 3. Z-score sobre los residuos
    media_res = residuos.mean() # Calculo de la media
    std_res = residuos.std() # Calculo de la desviacion tipica
    z_scores_res = (residuos - media_res) / std_res
    
    # Outliers según z-score de los residuos
    outliers = np.abs(z_scores_res) > umbral_z   # bool por punto
    
    # Devolvemos todo lo que necesita la función de dibujo
    return data, y_pred, outliers, modelo



def dibujar_regresion(data, y_pred, outliers, modelo):
    x = data["x"].values
    y = data["y"].values
    
    # Clasificación de puntos para colorear
    arriba = (y > y_pred) & (~outliers)
    abajo  = (y < y_pred) & (~outliers)
    
    plt.figure(figsize=(8, 5))
    
    # Puntos normales por encima de la recta
    plt.scatter(x[arriba], y[arriba],
                color="green", label="Normal arriba")
    
    # Puntos normales por debajo de la recta
    plt.scatter(x[abajo], y[abajo], color="blue", label="Normal abajo")
    
    # Outliers (según residuos)
    plt.scatter(x[outliers], y[outliers], color="red", label="Outliers", edgecolor="black", s=90)
    
    # Línea de regresión
    x_linea = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
    y_linea = modelo.predict(x_linea)
    plt.plot(x_linea, y_linea, color="orange", label="Línea de regresión")
    
    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("Regresión lineal con outliers (residuos) y puntos arriba/abajo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def imprimir_resumen(data, y_pred, outliers, modelo):
    """Imprime un resumen bonito de los resultados"""
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE LA REGRESIÓN LINEAL")
    print("="*60)
    
    # 1. Parámetros del modelo
    print(f"📈 Pendiente (a): {modelo.coef_[0]:.3f}")
    print(f"📍 Intercepto (b): {modelo.intercept_:.3f}")
    print(f"📋 Ecuación: y = {modelo.coef_[0]:.3f}x + {modelo.intercept_:.3f}")
    
    # 2. Métricas de ajuste
    r2 = modelo.score(data[["x"]], data["y"])
    residuos = data["y"] - y_pred
    mse = np.mean(residuos**2)
    
    print(f"\n📊 MÉTRICAS DE AJUSTE:")
    print(f"   R²: {r2:.3f}  |  MSE: {mse:.3f}")
    
    # 3. TABLA ALINEADA CON ESPACIOS (funciona en cualquier terminal)
    print("\n📋 CLASIFICACIÓN DEL MODELO:")
    print(" ┌─────────┬────────┬──────────────────────────────────────┐")
    print(" │  R²     │  MSE   │ Interpretación                       │")
    print(" ├─────────┼────────┼──────────────────────────────────────┤")
    print(" │ >0.90   │  Baja  │ Excelente ajuste                     │")
    print(" │0.70-0.90│ Media  │ Buen ajuste                          │")
    print(" │ <0.70   │  Alta  │ ⚠️ Revisar outliers o modelo         │")
    print(" └─────────┴────────┴──────────────┴───────────────────────┘")
    
    # Clasificar tu modelo actual
    if r2 > 0.90:
        clasif = "✅ Excelente"
    elif r2 >= 0.70:
        clasif = "✅ Buen ajuste"
    else:
        clasif = "⚠️ Revisar modelo"
    
    print(f"\n🎯 TU MODELO: R²={r2:.3f} → {clasif}")
    
    # 4. Outliers detectados
    n_outliers = np.sum(outliers)
    print(f"\n🔍 OUTLIERS DETECTADOS:")
    print(f"   Total puntos: {len(data)}")
    print(f"   Outliers: {n_outliers}")
    print(f"   % Outliers: {100*n_outliers/len(data):.1f}%")
    
    if n_outliers > 0:
        print(f"   📍 Posiciones: {np.where(outliers)[0] + 1}")
    
    # 5. Resumen de residuos
    print(f"\n📏 RESIDUOS:")
    print(f"   Media: 0.000 ✅")
    print(f"   Std:   {residuos.std():.3f}")
    print(f"   Máx:   {np.max(np.abs(residuos)):.3f}")
    
    print("\n" + "="*60)



    
if __name__ == "__main__":
    
    # Datos de prueba
    np.random.seed(0)
    x = np.arange(1, 91)             # 1, 2, ..., 20
    y = 2 * x + (np.random.randn(90) * 2)  # relación lineal con ruido

    # Metemos un par de outliers manualmente
    y[3] = 50
    y[15] = -10
    # R² (Coeficiente de determinación) es el porcentaje de variabilidad de y que explica la recta de regresión.
    # R² = 0.85 → "La recta explica el 85% de la variabilidad de y"
    # R² = 0.60 → "La recta explica el 60% de la variabilidad de y"  
    # R² = 0.20 → "La recta solo explica el 20% de la variabilidad de y"
    # Segun datos suministrados se espera esto:
    # Con nuestros 2 outliers grandes (y=50, y=-10), esperamos bajo R² ≈ 0.20-0.30. 
    # Los outliers "estropean bastante" el ajuste.
    # Cuanto mas alto mejor.
    
    # MSE: 23.456 → "Error promedio √155.362 ≈ 12.46 unidades" cuanto mas bajo mejor


    # 1) Analizar
    data, y_pred, outliers, modelo = analizar_regresion(x, y, umbral_z=1.2)
    
    # 2) Informacion para consola
    imprimir_resumen(data, y_pred, outliers, modelo)
    
    # 3) Dibujar
    dibujar_regresion(data, y_pred, outliers, modelo)

