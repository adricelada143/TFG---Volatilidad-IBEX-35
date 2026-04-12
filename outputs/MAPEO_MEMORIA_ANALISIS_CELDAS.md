# MAPEO: SECCIONES MEMORIA → CELDAS GITHUB (ANÁLISIS DEL DATO)

**Repositorio:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35

**Notebooks Análisis del Dato:**
- `02_analisis_dato/01_modelos_volatilidad.ipynb`
- `02_analisis_dato/02_event_study_macro.ipynb`

---

## SECCIÓN 2: Marco teórico

### 2.1. La volatilidad como objeto de predicción

**Implementación:**
- Definición de $V_t^{(21)}$ como target (volatilidad histórica 21d)
- Propiedades: estacionaria, persistente, predecible
- Colapso de 35 empresas a serie IBEX agregada

**Celdas GitHub:**
- 📍 **Cargar dataset maestro y colapsar a serie IBEX:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-5
- 📍 **Decisiones de diseño (por qué esta estructura):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-4

### 2.2. Estrategia de modelización: progresión de menor a mayor complejidad

**Implementación:**
- 4 modelos progresivos (Simple, OLS, GARCH, XGBoost)
- Tabla comparativa: complejidad vs features vs propósito

**Celdas GitHub:**
- 📍 **Tabla de modelos (A0, A, B, C) con justificación:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-4
- 📍 **Importaciones de librerías (statsmodels, sklearn, xgboost, arch):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-1

### 2.3. Modelo A — OLS con estructura HAR (Corsi, 2009)

**Implementación:**
- Ecuación: $\hat{V}_t = \beta_0 + \beta_1 V_{t-1} + \beta_5 \bar{V}^{(5)}_{t-1} + \beta_{21} \bar{V}^{(21)}_{t-1} + \gamma' X_{t-1} + \varepsilon_t$
- 15 features: 3 HAR + 12 macro
- Interpretabilidad de coeficientes

**Celdas GitHub:**
- 📍 **Explicación teórica de OLS HAR y variables macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-12
- 📍 **Función de métricas (RMSE, MAE, R², QLIKE):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-13
- 📍 **Entrenamiento OLS y generación Figura 16:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-15

### 2.4. Modelo B — GARCH(1,1) (Bollerslev, 1986)

**Implementación:**
- Ecuación: $\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$
- Distribución t-Student ($\nu$) para colas pesadas
- Parámetros: $\omega=0.0402, \alpha=0.1001, \beta=0.8722, \nu=6.35$

**Celdas GitHub:**
- 📍 **Teoría de GARCH y justificación de uso:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-19
- 📍 **Ajuste GARCH(1,1) con distribución t-Student:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-20
- 📍 **Pronóstico 1-step-ahead en test set:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-22

### 2.5. Modelo C — XGBoost (Chen & Guestrin, 2016)

**Implementación:**
- Gradient boosting con regularización
- Captura no linealidades
- SHAP values para interpretabilidad
- Robusto a multicolinealidad

**Celdas GitHub:**
- 📍 **Introducción a XGBoost y ventajas:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-27
- 📍 **Validación cruzada temporal (TimeSeriesSplit 5-fold):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-28
- 📍 **SHAP analysis y Feature Importance (Figura 18):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-30

### 2.6. Métricas de evaluación

**Implementación:**
- RMSE, MAE, R², QLIKE
- Test de Diebold-Mariano (1995)
- Diagnósticos de residuos (Jarque-Bera, QQ-plot, ACF/Ljung-Box)

**Celdas GitHub:**
- 📍 **Función compute_metrics() implementada:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-13
- 📍 **Test Diebold-Mariano en tabla de comparación:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-35

---

## SECCIÓN 3: Feature engineering e ingeniería de variables

### 3.1. Colapso del formato panel a serie IBEX agregada

**Implementación:**
- 35 empresas × 4.500 días → agregado diario único
- Media de log_ret y vol_hist_21d
- Resultado: 3.455 obs × 15 cols

**Celdas GitHub:**
- 📍 **Colapso panel a serie IBEX (media de 35 empresas):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-5

### 3.2. Construcción de features HAR

**Implementación:**
- `vol_lag1` = V_{t-1} (escala diaria)
- `vol_lag5` = media móvil 5d (escala semanal)
- `vol_lag21` = media móvil 21d (escala mensual)
- Cálculo con shift(1) para evitar data leakage

**Celdas GitHub:**
- 📍 **Features HAR con shift(1):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-5

### 3.3. Variables macroeconómicas como features

**Implementación:**
- 12 variables macro en 3 bloques (riesgo, monetarias, actividad)
- Forward-filled para información disponible en tiempo real
- Datos desde SQLite (ingeniería del dato previa)

**Celdas GitHub:**
- 📍 **Carga de 12 variables macro de SQLite:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-5

### 3.4. Split temporal train/test

**Implementación:**
- Split 80/20 por fecha (no aleatorio)
- Train: 2.764 obs (2 mayo 2012 – 16 febrero 2023), vol media 0.2943
- Test: 691 obs (17 febrero 2023 – 31 octubre 2025), vol media 0.2449

**Celdas GitHub:**
- 📍 **Split temporal 80/20 y Figura 15:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-6

---

## SECCIÓN 4: Modelo A0 — Regresión Lineal Simple (baseline)

**Implementación:**
- Ecuación: $\hat{V}_t = 0.0021 + 0.9925 \cdot V_{t-1}$
- Baseline absoluto: R²=0.9686
- Demuestra que persistencia explica 97% de la varianza

**Celdas GitHub:**
- 📍 **Modelo Simple (vol_lag1 solo):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-8
- 📍 **Figura 16b: Resultados Simple:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-8
- 📍 **Figura 16d: Diagnóstico residuos Simple:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-10

---

## SECCIÓN 5: Modelo A — OLS con estructura HAR y variables macroeconómicas

**Implementación:**
- 15 features: 3 HAR + 12 macro
- Coeficientes estimados:
  - vol_lag1: +1.0446 (domina)
  - euribor_3m: +0.0070 (mayor efecto macro)
  - eur_usd: +0.0067
  - tipo_dfr: -0.0060
- Métricas: RMSE=0.0084, R²=0.9677

**Celdas GitHub:**
- 📍 **Teoría de OLS HAR+macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-12
- 📍 **Figura 16: Coeficientes y resultados OLS:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-15
- 📍 **Figura 16c: Diagnóstico residuos OLS (JB, QQ, ACF, error):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-17

---

## SECCIÓN 6: Modelo B — GARCH(1,1)

**Implementación:**
- Parámetros: ω=0.0402, α=0.1001, β=0.8722, ν=6.35
- Persistencia total: α+β=0.9722
- Volatilidad LP implícita: 19.09% (vs media observada 19.81%)
- Métricas: RMSE=0.1029, R²=-3.8375 (esperado por diferencia de frecuencia)

**Celdas GitHub:**
- 📍 **Teoría GARCH (ecuación, interpretación parámetros):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-19
- 📍 **Ajuste GARCH sobre log-retornos medios:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-20
- 📍 **Pronóstico GARCH 1-step-ahead (Figura 17):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-22
- 📍 **Figura 17b: Diagnóstico residuos GARCH:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-25

---

## SECCIÓN 7: Modelo C — XGBoost Gradient Boosting

### 7.1. Validación cruzada temporal

**Implementación:**
- TimeSeriesSplit(n_splits=5) preservando orden temporal
- Optimización de n_estimators: 100, 200, 300, 500, 700
- Selección: n_estimators=100 (CV-RMSE=0.0348 ± 0.0406)
- Hiperparámetros: learning_rate=0.05, max_depth=4, subsample=0.8

**Celdas GitHub:**
- 📍 **CV temporal y selección de n_estimators:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-28

### 7.2. Rendimiento en test

**Implementación:**
- RMSE=0.0082 (MENOR de todos)
- R²=0.9691 (MAYOR de todos)
- MAE=0.0052
- QLIKE=-1.8419

**Celdas GitHub:**
- 📍 **Entrenamiento final y pronóstico XGBoost:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-30

### 7.3. Importancia de variables y análisis SHAP

**Implementación:**
- Top 5 SHAP values:
  1. vol_lag1: 0.0547
  2. vol_lag5: 0.0080
  3. vix: 0.0026 (principal variable macro)
  4. vol_lag21: 0.0011
  5. bono_es_10y: 0.0003

**Celdas GitHub:**
- 📍 **Figura 18: Feature Importance y SHAP summary plot:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-30
- 📍 **Figura 18b: Diagnóstico residuos XGBoost:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-32

---

## SECCIÓN 8: Comparación de modelos

### 8.1. Resumen de métricas

**Implementación:**
- Tabla comparativa 4 modelos
- Simple ≈ OLS ≈ XGBoost (R² 0.9677–0.9691)
- GARCH significativamente peor (RMSE 0.1029, R²=-3.8375)

**Celdas GitHub:**
- 📍 **Tabla de métricas (Simple, OLS, GARCH, XGBoost):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-35

### 8.2. Test de Diebold-Mariano

**Implementación:**
- Simple vs OLS: DM=-0.373, p=0.7093 (sin diferencia)
- Simple vs XGBoost: DM=+0.253, p=0.7999 (sin diferencia)
- OLS vs GARCH: DM=-42.254, p=0.0000 (OLS mejor)
- OLS vs XGBoost: DM=+0.683, p=0.4948 (sin diferencia)
- GARCH vs XGBoost: DM=+42.183, p=0.0000 (XGBoost mejor)

**Celdas GitHub:**
- 📍 **Figura 19: Test Diebold-Mariano completo:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-35

### 8.3. ¿Invalida esto la investigación?

**Implementación:**
- Confirma hiperpersistencia de volatilidad (Mandelbrot, 1963)
- Variables macro aportan valor marginal en modelos no lineales
- GARCH significativamente peor valida que HAR > GARCH

**Celdas GitHub:**
- 📍 **Justificación de por qué Simple≈OLS≈XGBoost:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-34

---

## SECCIÓN 9: Valor añadido de las variables macroeconómicas

### 9.1. Resultados

**Implementación:**
- **OLS (HAR solo vs HAR+macro):**
  - HAR solo: RMSE=0.0078, R²=0.9719
  - HAR+macro: RMSE=0.0084, R²=0.9677
  - Δ RMSE: +7.2% (EMPEORA)

- **XGBoost (HAR solo vs HAR+macro):**
  - HAR solo: RMSE=0.0096, R²=0.9582
  - HAR+macro: RMSE=0.0082, R²=0.9691
  - Δ RMSE: -14.1% (MEJORA)

**Celdas GitHub:**
- 📍 **Comparación OLS: HAR solo vs HAR+macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-37
- 📍 **Comparación XGBoost: HAR solo vs HAR+macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-37
- 📍 **Figura 20: Valor añadido de macro visualizado:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-37

### 9.2. Interpretación

**Implementación:**
- OLS: multicolinealidad introduce ruido (-7,2% RMSE)
- XGBoost: captura interacciones no lineales (+14.1% mejora RMSE)
- Ejemplo: efecto del VIX es asimétrico (15→25 vs 25→35)
- **Conclusión: relación macro-volatilidad es NO LINEAL**

**Celdas GitHub:**
- 📍 **Explicación teórica del hallazgo paradójico:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-36

---

## SECCIÓN 10: Event Study — Impacto de publicaciones macroeconómicas

### 10.1. Motivación y metodología

**Implementación:**
- Pregunta: ¿generan las publicaciones macro shocks puntuales?
- Medida: |log_ret| como volatilidad diaria
- Metodología: vol evento vs mediana de 10 días previos
- Tests: Wilcoxon, Mann-Whitney, Kruskal-Wallis

**Celdas GitHub:**
- 📍 **Motivación del Event Study (notebook 02):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-0
- 📍 **Carga de datos y metodología:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-4

### 10.2. Eventos identificados

**Implementación:**
- Total: 1.058 eventos
- Distribución:
  - Producción industrial: 248
  - Euribor 3M: 246
  - IPC subyacente: 236
  - IPC interanual: 145
  - Tasa de paro: 81
  - PIB: 69
  - Tipo BCE: 33

**Celdas GitHub:**
- 📍 **Detección de eventos (cambios en variables macro):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-6

### 10.3. Resultado principal: +11,6% volatilidad en días de evento

**Implementación:**
- Mediana vol evento: 0.01329
- Mediana vol normal: 0.01191
- Diferencia: +11.6%
- Mann-Whitney p-valor: 0.0000

**Celdas GitHub:**
- 📍 **Figura 20: Panorama general (Mann-Whitney +11,6% sig):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-10

### 10.4. Impacto por indicador

**Implementación:**
- Top impacto: Tipo BCE (+0.35%), PIB (+0.31%), Paro (+0.29%)
- Actividad real > Inflación > Política monetaria
- Todos significativos excepto Tipo BCE (marginal p=0.0584)

**Celdas GitHub:**
- 📍 **Tabla resumen con tests Wilcoxon por indicador:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-12
- 📍 **Figura 21: Análisis detallado por indicador:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-13

### 10.5. Asimetrías por signo: malas noticias pesan más

**Implementación:**
- Tipo BCE: Recortes (+0.46%) > Subidas (+0.16%)
- Tasa de Paro: Aumentos (+0.43%) > Bajadas (+0.15%)
- PIB/IPC: Aproximadamente simétrico

**Celdas GitHub:**
- 📍 **Análisis de efecto por signo del cambio:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-12
- 📍 **Figura 22: Zoom BCE + IPC con asimetría visible:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-15

### 10.6. ¿Importa la magnitud del cambio?

**Implementación:**
- Análisis de relación |Δmacro| vs vol anormal
- Cambios mayores producen shocks más intensos

**Celdas GitHub:**
- 📍 **Figura 23: 6 scatterplots de magnitud vs vol anormal:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-17

### 10.7. ¿Difieren los efectos entre categorías?

**Implementación:**
- Kruskal-Wallis: H=10.71, p=0.0047
- Actividad real tiene mayor impacto que inflación y política monetaria

**Celdas GitHub:**
- 📍 **Test Kruskal-Wallis entre categorías:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-13

### 10.8. Persistencia del efecto

**Implementación:**
- Vol elevada 1-2 días post-evento en todos indicadores
- Mercado tarda 1-2 días hábiles en procesar información

**Celdas GitHub:**
- 📍 **Análisis de vol_post_1d y vol_post_2d:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-12

---

## SECCIÓN 11: Conclusiones del capítulo

### 11.1. Respuestas a las preguntas de investigación

**Implementación:**
- Q1: ¿Predecible? SÍ, R²>0.96
- Q2: ¿Mejor modelo? XGBoost (RMSE=0.0082), pero sin diferencia estadística
- Q3: ¿Valor macro? SÍ, pero NO LINEAL (+7,2% OLS, -14,1% XGBoost)
- Q4: ¿Shocks? SÍ, +11,6% en días publicación (p<0.0001)

**Celdas GitHub:**
- 📍 **Síntesis de respuestas a 4 preguntas principales:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-40
- 📍 **Event Study: resumen de hallazgos:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/02_event_study_macro.ipynb#cell-19

### 11.2. Limitaciones

**Implementación:**
- Autocorrelación mecánica de vol_hist_21d (20/21 retornos compartidos)
- Frecuencia variables macro (trimestrales → forward-fill)
- Test set tranquilo (2023-2025) vs train con crisis

**Celdas GitHub:**
- 📍 **Discusión de limitaciones al final del análisis:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-38

---

## RESUMEN DE ESTRUCTURA NOTEBOOK

### 01_modelos_volatilidad.ipynb (40 celdas)

| Sección | Celdas | Contenido |
|---------|--------|----------|
| Setup | 0-2 | Título, importaciones |
| Feature Engineering | 3-6 | Decisiones diseño, carga, split |
| Modelo A0 Simple | 7-11 | Baseline, métricas, diagnóstico |
| Modelo A OLS | 12-18 | HAR+macro, coefs, diagnóstico |
| Modelo B GARCH | 19-26 | Parámetros, pronóstico, diagnóstico |
| Modelo C XGBoost | 27-33 | CV, SHAP, diagnóstico |
| Comparación | 34-35 | Test DM, interpretación |
| Valor Macro | 36-37 | HAR vs HAR+macro |
| Conclusiones | 38-40 | Respuestas, limitaciones |

### 02_event_study_macro.ipynb (20 celdas)

| Sección | Celdas | Contenido |
|---------|--------|----------|
| Setup | 0-2 | Motivación, importaciones |
| Datos | 3-4 | Dataset maestro, serie IBEX |
| Eventos | 5-6 | Identificación 1.058 eventos |
| Vol Anormal | 7-8 | Cálculo evento vs benchmark |
| Figura 20 | 9-10 | Panorama +11,6% (Mann-Whitney p=0) |
| Figura 21 | 11-13 | Detalle por indicador, KW p=0.0047 |
| Figura 22 | 14-15 | Zoom BCE + IPC, asimetría |
| Figura 23 | 16-17 | Magnitud |Δmacro| vs vol |
| Conclusiones | 18-20 | Resumen hallazgos, próximos pasos |

---

## CÓMO USAR ESTE MAPEO EN WORD

1. **Abre:** `Memoria_Analisis_del_Dato.docx`

2. **Para cada sección**, inserta un hipervínculo:
   - Selecciona texto relacionado (ej: "función `compute_metrics()`")
   - **Ctrl+K** (o Menú → Insertar → Hipervínculo)
   - Pega la URL de la celda GitHub
   - Aceptar

3. **Ejemplo de URL:**
   ```
   https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/02_analisis_dato/01_modelos_volatilidad.ipynb#cell-15
   ```

4. **Cuando termines, commit:**
   ```bash
   git add outputs/Memoria_Analisis_del_Dato.docx
   git commit -m "docs: Add GitHub hyperlinks to Análisis del Dato memoria"
   git push
   ```

---

**Documento generado:** 12 de abril de 2026
**Repositorio:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35
