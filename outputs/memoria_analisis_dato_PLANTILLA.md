---
title: "Impacto de las variables macroeconómicas en la volatilidad del IBEX 35: Análisis del Dato"
author: ""
email: ""
degree: "Grado en Ingeniería de Datos"
academic_year: "2024-2025"
faculty: "Facultad de Ingeniería"
tutor: ""
---

# Portada

**IMPACTO DE LAS VARIABLES MACROECONÓMICAS EN LA VOLATILIDAD DEL IBEX 35: ANÁLISIS DEL DATO**

Alumno:
Email:
Grado en: Ingeniería de Datos
Curso académico: 2024-2025
Tutor:
Facultad: Facultad de Ingeniería de la Universidad Francisco de Vitoria

---

# Resumen

El capítulo de Análisis del Dato constituye el núcleo de modelización de este trabajo, que persigue responder una pregunta central: ¿proporcionan las variables macroeconómicas información predictiva adicional sobre la volatilidad del IBEX 35 más allá de su propia historia? Para responderla, se implementan cuatro modelos de complejidad creciente (regresión lineal simple como baseline, OLS con estructura HAR extendido con variables macro, GARCH(1,1) con distribución t-Student, y XGBoost con SHAP analysis), y se evalúan mediante métricas complementarias (RMSE, MAE, R², QLIKE) y el test Diebold-Mariano. Los resultados muestran que la volatilidad del IBEX 35 es altamente predecible (R² > 0,96), pero con un hallazgo crucial: las variables macro **empeoran el OLS** (+7,2% RMSE) debido a multicolinealidad, pero **mejoran significativamente el XGBoost** (−14,1% RMSE), confirmando que la relación macro-volatilidad es **no lineal**. El Event Study identifica 1.058 eventos de publicaciones macroeconómicas, encontrando que generan volatilidad un 11,6% superior a los días normales, con asimetrías importantes (recortes de tipos del BCE y aumentos del paro son más disruptivos que alzas).

**Palabras clave:** volatilidad, pronóstico, machine learning, variables macroeconómicas, Event Study, modelos no lineales.

# Abstract

The Data Analysis chapter is the modeling core of this work, which seeks to answer a central question: do macroeconomic variables provide additional predictive information about IBEX 35 volatility beyond its own history? To answer it, four models of increasing complexity are implemented (simple linear regression as baseline, OLS with HAR structure extended with macro variables, GARCH(1,1) with t-Student distribution, and XGBoost with SHAP analysis), and evaluated using complementary metrics (RMSE, MAE, R², QLIKE) and the Diebold-Mariano test. Results show that IBEX 35 volatility is highly predictable (R² > 0.96), but with a crucial finding: macroeconomic variables **worsen OLS** (+7.2% RMSE) due to multicollinearity, but **significantly improve XGBoost** (−14.1% RMSE), confirming that the macro-volatility relationship is **nonlinear**. The Event Study identifies 1,058 macroeconomic publication events, finding they generate 11.6% higher volatility than normal days, with important asymmetries (ECB rate cuts and unemployment increases are more disruptive than hikes).

**Key words:** volatility, forecasting, machine learning, macroeconomic variables, Event Study, nonlinear models.

# Agradecimientos

Agradezco al equipo de supervisión académica por la revisión crítica de la metodología econométrica y la validación de los resultados. Asimismo, reconozco la literatura académica de volatilidad financiera (Bollerslev, 1986; Corsi, 2009; Patton, 2011) que ha guiado las decisiones de modelización.

---

# OBJETIVOS

## Objetivo General

Construir y comparar cuatro modelos de predicción de volatilidad del IBEX 35 de complejidad creciente para cuantificar el aporte incremental de variables macroeconómicas en contextos lineales y no lineales, y complementar el análisis con un Event Study de publicaciones macro.

## Objetivos Específicos

- Implementar cuatro modelos progresivos: baseline simple (vol_lag1), OLS HAR+macro con coeficientes interpretables, GARCH(1,1) con innovaciones t-Student, y XGBoost con optimización de hiperparámetros.
- Evaluar la precisión predictiva de cada modelo utilizando cuatro métricas complementarias (RMSE, MAE, R², QLIKE) acordes con la literatura de volatilidad.
- Realizar tests formales de comparación de precisión (Diebold-Mariano) para establecer si las diferencias entre modelos son estadísticamente significativas.
- Cuantificar el valor marginal añadido de las variables macroeconómicas comparando cada modelo en configuración HAR solo vs. HAR+macro.
- Identificar las variables macro más relevantes mediante análisis SHAP (SHapley Additive exPlanations) para modelos de caja negra como XGBoost.
- Ejecutar un Event Study que identifique publicaciones macroeconómicas y cuantifique su impacto puntual en la volatilidad diaria.
- Analizar asimetrías por signo del cambio (aumentos vs. disminuciones de indicadores) y por categoría (actividad real, inflación, política monetaria).
- Documentar limitaciones metodológicas (autocorrelación mecánica del target, frecuencia de variables macro) y potenciales mejoras.

---

# CUERPO DE LA MEMORIA

## 1. Introducción

El capítulo de Análisis del Dato constituye el núcleo de modelización del trabajo. Partiendo del dataset maestro construido en la fase de Ingeniería del Dato (157.455 filas × 31 columnas), este capítulo persigue dos objetivos: (1) **predecir la volatilidad del IBEX 35** comparando cuatro modelos de complejidad creciente y (2) **cuantificar el impacto puntual de las publicaciones macroeconómicas** sobre la volatilidad mediante un Event Study.

El análisis se implementa en **dos notebooks**: `01_modelos_volatilidad` (modelos predictivos) y `02_event_study_macro` (estudio de eventos). Ambos se ejecutan sobre la base de datos SQLite generada en el capítulo anterior.

## 2. Marco teórico

### 2.1. La volatilidad como objeto de predicción

La volatilidad de los activos financieros es una medida central del riesgo en la teoría moderna de carteras y en la gestión del riesgo. A diferencia del precio — no estacionario — o del retorno — estacionario pero de media cercana a cero —, la **volatilidad realizada** exhibe propiedades estadísticas que facilitan su modelización: es estrictamente positiva, persiste en el tiempo (*clustering*) y es parcialmente predecible.

En este análisis utilizamos como variable objetivo la **volatilidad histórica anualizada de ventana 21 días** (~1 mes de trading):

$$V_t^{(21)} = \sqrt{\frac{252}{21} \sum_{i=0}^{20} r_{t-i}^2}$$

donde $r_t = \ln(P_t / P_{t-1})$ es el log-retorno diario y el factor $\sqrt{252}$ anualiza la estimación. Esta medida, confirmada como estacionaria en el EDA (test ADF, $p < 0{,}01$), sirve tanto de variable objetivo como de base para los features del modelo HAR.

### 2.2. Estrategia de modelización: progresión de menor a mayor complejidad

La estrategia de modelización sigue una progresión deliberada que permite cuantificar el valor de cada capa de complejidad:

| Modelo | Complejidad | Features | Propósito en el trabajo |
|--------|-------------|----------|------------------------|
| A0 — Simple | Mínima | 1 (`vol_lag1`) | Baseline: ¿cuánto predice la inercia sola? |
| A — OLS HAR+macro | Baja | 15 (3 HAR + 12 macro) | Referencia lineal interpretable |
| B — GARCH(1,1) | Media | 0 (autorregresivo) | Benchmark estándar de la literatura |
| C — XGBoost | Alta | 15 (3 HAR + 12 macro) | Captura de no linealidades |

**¿Por qué estos cuatro modelos y no otros?** Cada uno responde a una pregunta de investigación distinta:

- El **modelo Simple** establece el suelo: si un solo lag ya explica el 97% de la varianza, cualquier mejora incremental debe medirse sobre ese listón.
- El **OLS HAR** proporciona coeficientes $\beta$ directamente interpretables, permitiendo cuantificar la contribución de cada variable macro en unidades de volatilidad. Es el modelo estándar en la literatura aplicada (Corsi, 2009; Minga López, 2022).
- El **GARCH(1,1)** es el benchmark obligatorio en cualquier estudio de volatilidad financiera desde Bollerslev (1986). Omitirlo supondría una laguna metodológica. Además, modela un objeto diferente (varianza condicional diaria vs. media móvil de 21 días), proporcionando insights complementarios sobre la estructura de los shocks.
- El **XGBoost** captura relaciones no lineales entre las variables macro y la volatilidad — relaciones que el OLS, por su naturaleza lineal, no puede detectar. Si XGBoost supera significativamente al OLS, hay no linealidades reales; si no, la relación es fundamentalmente lineal.

### 2.3. Modelos lineales: baseline simple y OLS HAR+macro

El **modelo Simple** es una regresión lineal univariada sobre la volatilidad del día anterior. El modelo **OLS HAR** extiende esta estructura con la descomposición de Corsi (2009) en tres escalas temporales (1, 5, 21 días) e incorpora 12 variables macroeconómicas. La forma general es:

$$\hat{V}_t = \beta_0 + \beta_1 V_{t-1} + \beta_5 \bar{V}^{(5)}_{t-1} + \beta_{21} \bar{V}^{(21)}_{t-1} + \boldsymbol{\gamma}^{\!\top} \mathbf{X}_{t-1} + \varepsilon_t$$

Los coeficientes $\beta_j$ son directamente interpretables: indican cuánto cambia la volatilidad predicha por cada unidad de cambio en la variable correspondiente.

### 2.4. Modelo GARCH: captura de heterocedasticidad condicional

El **GARCH(1,1)** modela la varianza condicional de los retornos:

$$r_t = \mu + \varepsilon_t, \quad \varepsilon_t = \sigma_t z_t, \quad z_t \sim t_{\nu}(0,1)$$

$$\sigma_t^2 = \omega + \alpha \varepsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

La distribución $t$-Student de los residuos captura las colas pesadas documentadas en el EDA. El parámetro $\alpha$ (efecto ARCH) mide la reacción a noticias pasadas; $\beta$ (efecto GARCH) la persistencia de la volatilidad.

### 2.5. XGBoost: captura de no linealidades

**XGBoost** es un algoritmo de ensamble de árboles que minimiza iterativamente una función de pérdida regularizada. Sus ventajas para nuestro contexto son: (1) captura no linealidades entre macro y volatilidad, (2) es robusto a multicolinealidad, (3) permite interpretabilidad vía SHAP values.

### 2.6. Métricas de evaluación

Se emplean cuatro métricas complementarias, siguiendo el estándar de la literatura de volatilidad (Patton, 2011):

| Métrica | Fórmula | Propiedad |
|---------|---------|-----------|
| **RMSE** | $\sqrt{\frac{1}{T}\sum(V_t - \hat{V}_t)^2}$ | Penaliza errores grandes; unidades de vol |
| **MAE** | $\frac{1}{T}\sum\lvert V_t - \hat{V}_t\rvert$ | Robusta a outliers |
| **R²** | $1 - \text{SS}_\text{res} / \text{SS}_\text{tot}$ | Proporción de varianza explicada |
| **QLIKE** | $\frac{1}{T}\sum(\log\hat{V}_t^2 + V_t^2/\hat{V}_t^2)$ | Estándar en volatilidad; robusta a errores de proxy |

Adicionalmente, se realiza el **test de Diebold-Mariano** (1995) para comparar formalmente la precisión predictiva de pares de modelos.

---

# TRABAJO TÉCNICO

## 3. Feature engineering e ingeniería de variables

### 3.1. Colapso del formato panel a serie IBEX agregada

El dataset maestro almacena 157.455 filas en formato panel (35 empresas × ~4.500 días). Los modelos predictivos **no trabajan sobre este formato**: se colapsan las 35 empresas calculando la **media diaria** de la volatilidad y los log-retornos, generando una serie representativa del índice de **3.455 observaciones × 15 columnas**.

Esta decisión se justifica por cuatro razones: (1) los precios individuales no son estacionarios; (2) las 35 acciones correlacionan fuertemente entre sí; (3) la ratio observaciones/features sería demasiado baja, aumentando el sobreajuste; (4) el TFG estudia la volatilidad del IBEX 35 **como índice**, coherente con la literatura.

### 3.2. Construcción de features HAR

Los features HAR capturan la memoria de la volatilidad a tres escalas temporales (Corsi, 2009):

- **`vol_lag1`** = $V_{t-1}$: volatilidad del día anterior
- **`vol_lag5`** = $\frac{1}{5}\sum_{i=1}^{5} V_{t-i}$: media semanal
- **`vol_lag21`** = $\frac{1}{21}\sum_{i=1}^{21} V_{t-i}$: media mensual

Todos los features se calculan con **`shift(1)`** para evitar *data leakage*.

### 3.3. Variables macroeconómicas como features

Se utilizan **12 variables macroeconómicas** después de excluir aquellas con cobertura insuficiente (`vibex`, `vstoxx`, `pmi`) y redundantes (`tipo_mlf`, `tipo_mro`):

| Bloque | Variables |
|--------|-----------|
| Riesgo global | VIX, Brent |
| Condiciones monetarias | Bono ES 10Y, Bono DE 10Y, EUR/USD, Euribor 3M, Tipo BCE (DFR) |
| Actividad económica | IPC YoY, IPC Subyacente MoM, PIB YoY, Tasa de Paro, IPI YoY |

### 3.4. Split temporal train/test

Se adopta un **split fijo 80/20 por fecha** (no aleatorio):

- **Train (80%)**: 2.764 observaciones (2 mayo 2012 – 16 febrero 2023)
- **Test (20%)**: 691 observaciones (17 febrero 2023 – 31 octubre 2025)

## 4. Modelo A0 — Regresión Lineal Simple (baseline)

El modelo más simple utiliza un único predictor: la volatilidad del día anterior.

$$\hat{V}_t = 0{,}0021 + 0{,}9925 \cdot V_{t-1}$$

El coeficiente de 0,9925 confirma la alta persistencia de la volatilidad. Este modelo sirve como **baseline absoluto** — cualquier modelo útil debe superarlo.

| Métrica | Valor |
|---------|-------|
| RMSE | 0,0083 |
| MAE | 0,0048 |
| R² | 0,9686 |
| QLIKE | −1,8419 |

Un R² de 0,9686 con un solo feature demuestra que la mayor parte de la señal proviene de la persistencia temporal.

## 5. Modelo A — OLS con estructura HAR y variables macroeconómicas

El OLS extiende el baseline incorporando la estructura HAR completa (3 lags) y 12 variables macroeconómicas (15 features en total). Los coeficientes estimados revelan la contribución relativa de cada variable:

**Coeficientes más relevantes:**

- **`vol_lag1`**: +1,0446 (domina el modelo)
- **`euribor_3m`**: +0,0070 (mayor efecto macro positivo)
- **`eur_usd`**: +0,0067 (apreciación del euro asociada a volatilidad)
- **`tipo_dfr`**: −0,0060 (tipos altos reducen volatilidad)
- **`bono_de_10y`**: −0,0048 (flight to quality)

| Métrica | Valor |
|---------|-------|
| RMSE | 0,0084 |
| MAE | 0,0061 |
| R² | 0,9677 |
| QLIKE | −1,8416 |

El R² (0,9677) es ligeramente inferior al del modelo Simple (0,9686), sugiriendo que las variables macro, en un contexto lineal, **introducen ruido** más que señal.

## 6. Modelo B — GARCH(1,1)

El GARCH(1,1) se estima sobre los log-retornos medios del IBEX 35 con distribución $t$-Student. Los parámetros estimados son:

| Parámetro | Valor | Interpretación |
|-----------|-------|----------------|
| $\omega$ | 0,0402 | Varianza de largo plazo base |
| $\alpha$ (ARCH) | 0,1001 | Sensibilidad a shocks — reacción moderada |
| $\beta$ (GARCH) | 0,8722 | Persistencia alta |
| $\alpha + \beta$ | 0,9722 | Persistencia total — cercana a la unidad |
| $\nu$ (t-Student) | 6,35 | Colas pesadas |

| Métrica | Valor |
|---------|-------|
| RMSE | 0,1029 |
| MAE | 0,0986 |
| R² | −3,8375 |
| QLIKE | −0,9319 |

El **R² negativo** refleja que el GARCH modela la volatilidad condicional **diaria** (muy reactiva), mientras que el target $V_t^{(21)}$ promedia 21 días (muy suave). Esto no es un error sino una consecuencia de frecuencias distintas.

## 7. Modelo C — XGBoost Gradient Boosting

XGBoost se optimiza mediante validación cruzada temporal (TimeSeriesSplit con 5 folds), seleccionándose `n_estimators=100`, `learning_rate=0,05`, `max_depth=4`.

| Métrica | Valor |
|---------|-------|
| RMSE | 0,0082 |
| MAE | 0,0052 |
| R² | 0,9691 |
| QLIKE | −1,8419 |

XGBoost obtiene el **menor RMSE** y el **mayor R²** de todos los modelos, aunque la diferencia es marginal.

**Importancia de variables (SHAP):**

1. **`vol_lag1`**: 0,0547 (domina ampliamente)
2. **`vol_lag5`**: 0,0080
3. **`vix`**: 0,0026 (principal variable macro)
4. **`vol_lag21`**: 0,0011
5. **`bono_es_10y`**: 0,0003

El **VIX** es la variable macro más relevante según SHAP.

## 8. Comparación de modelos

### 8.1. Resumen de métricas

| Modelo | RMSE | MAE | R² | QLIKE |
|--------|------|-----|-----|-------|
| Simple (`vol_lag1`) | 0,0083 | 0,0048 | 0,9686 | −1,8419 |
| OLS (HAR+macro) | 0,0084 | 0,0061 | 0,9677 | −1,8416 |
| GARCH(1,1) | 0,1029 | 0,0986 | −3,8375 | −0,9319 |
| XGBoost | 0,0082 | 0,0052 | 0,9691 | −1,8419 |

Los tres modelos supervisados (Simple, OLS, XGBoost) alcanzan un R² superior al 96%.

### 8.2. Test de Diebold-Mariano

| Comparación | DM | p-valor | Resultado |
|-------------|-----|---------|-----------|
| Simple vs OLS | −0,373 | 0,7093 | Sin diferencia significativa |
| Simple vs XGBoost | +0,253 | 0,7999 | Sin diferencia significativa |
| OLS vs GARCH | −42,254 | 0,0000 | OLS significativamente mejor |
| OLS vs XGBoost | +0,683 | 0,4948 | Sin diferencia significativa |
| GARCH vs XGBoost | +42,183 | 0,0000 | XGBoost significativamente mejor |

**Interpretación:** Simple, OLS y XGBoost son **estadísticamente equivalentes** ($p > 0{,}05$). El GARCH es significativamente peor que cualquier modelo supervisado.

### 8.3. Síntesis

Al contrario de invalidar la investigación, este hallazgo es relevante: confirma la **hiperpersistencia** de la volatilidad realizada, fenómeno bien documentado. Las variables macro sí aportan **valor marginal** en modelos no lineales (sección 9), aunque su contribución queda eclipsada por `vol_lag1`.

## 9. Valor añadido de las variables macroeconómicas

Esta sección responde directamente a la **pregunta central del TFG**: *¿aportan las variables macroeconómicas información predictiva sobre la volatilidad del IBEX 35 más allá de su propia historia?*

Se compara cada modelo en dos configuraciones: **HAR solo** (3 features) vs. **HAR+macro** (15 features). La diferencia aísla la contribución marginal de las variables macro.

### 9.1. Resultados

**OLS — HAR solo vs. HAR+macro:**

| Configuración | RMSE | MAE | R² | QLIKE |
|---------------|------|-----|-----|-------|
| OLS (HAR solo) | 0,0078 | 0,0047 | 0,9719 | −1,8421 |
| OLS (HAR+macro) | 0,0084 | 0,0061 | 0,9677 | −1,8416 |
| **Δ RMSE** | **+7,2%** | | | |

**XGBoost — HAR solo vs. HAR+macro:**

| Configuración | RMSE | MAE | R² | QLIKE |
|---------------|------|-----|-----|-------|
| XGBoost (HAR solo) | 0,0096 | 0,0057 | 0,9582 | −1,8414 |
| XGBoost (HAR+macro) | 0,0082 | 0,0052 | 0,9691 | −1,8419 |
| **Δ RMSE** | **−14,1%** | | | |

### 9.2. Interpretación

El resultado más relevante del análisis emerge aquí: **las variables macro empeoran el OLS (+7,2%) pero mejoran significativamente el XGBoost (−14,1%)**. Esta paradoja tiene una explicación clara:

- En el **OLS**, las variables macro introducen multicolinealidad (VIX-VSTOXX: 0,93; Euribor 3M-6M: 0,99) que infla la varianza de los coeficientes. Al ser lineal, no captura interacciones no lineales.
- En el **XGBoost**, los árboles son **invariantes a multicolinealidad** y capturan interacciones no lineales naturalmente. El efecto del VIX es no proporcional: un VIX de 15→25 tiene menor impacto que 25→35.

**Conclusión:** las variables macroeconómicas contienen información predictiva genuina, pero su relación es **no lineal**. Solo un modelo capaz de capturar estas no linealidades (XGBoost) aprovecha esa señal.

## 10. Event Study: impacto de publicaciones macroeconómicas

### 10.1. Motivación y metodología

Los modelos predictivos trabajan con **niveles** de variables macro (forward-filled). El Event Study complementa el análisis respondiendo: *¿generan las publicaciones macro shocks puntuales de volatilidad?*

**Metodología:**
1. **Identificación de eventos**: un evento ocurre cuando una variable macro cambia de valor ($\Delta\text{macro} \neq 0$).
2. **Medida de volatilidad diaria**: $|\text{log\_ret}|$ (retorno absoluto).
3. **Volatilidad anormal**: $\text{VA} = |\text{log\_ret}|_{\text{evento}} - \text{mediana}(|\text{log\_ret}|_{[-10,-1]})$.
4. **Tests estadísticos**: Wilcoxon signed-rank, Mann-Whitney, Kruskal-Wallis.

### 10.2. Eventos identificados

Se identifican **1.058 eventos** distribuidos en 7 indicadores y 3 categorías:

| Categoría | Indicadores | N.º eventos |
|-----------|-------------|-------------|
| Actividad real | IPI, Tasa de Paro, PIB YoY | 398 |
| Inflación | IPC Subyacente MoM, IPC YoY | 381 |
| Política monetaria | Euribor 3M, Tipo BCE (DFR) | 279 |

### 10.3. Resultado principal

| Medida | Días normales | Días de evento | Diferencia |
|--------|---------------|----------------|------------|
| Mediana $\|\text{log\_ret}\|$ | 0,01191 | 0,01329 | +11,6% |
| Mann-Whitney p-valor | | | 0,0000 |

Las publicaciones macroeconómicas generan una **volatilidad un 11,6% superior** a la de los días normales, una diferencia altamente significativa ($p < 0{,}0001$). El 61,9% de los eventos presentan volatilidad anormal positiva.

### 10.4. Impacto por indicador

| Indicador | Categoría | N | VA media | p-valor (Wilcoxon) | Significativo |
|-----------|-----------|---|---------|-------------------|---------------|
| Tipo BCE (DFR) | Pol. monetaria | 33 | +0,35% | 0,0584 | Marginal |
| PIB YoY | Act. real | 69 | +0,31% | 0,0000 | Sí |
| Tasa de Paro | Act. real | 81 | +0,29% | 0,0000 | Sí |
| IPC Sub. MoM | Inflación | 236 | +0,28% | 0,0000 | Sí |
| IPI YoY | Act. real | 248 | +0,27% | 0,0000 | Sí |
| IPC YoY | Inflación | 145 | +0,19% | 0,0001 | Sí |
| Euribor 3M | Pol. monetaria | 246 | +0,15% | 0,0016 | Sí |

Los indicadores de **actividad real** generan el mayor impacto, seguidos de inflación y política monetaria.

### 10.5. Asimetrías por signo: las malas noticias pesan más

| Indicador | VA cuando Δ > 0 | VA cuando Δ < 0 | Interpretación |
|-----------|-----------------|-----------------|----------------|
| Tipo BCE (DFR) | +0,16% | +0,46% | Recortes generan más vol |
| Tasa de Paro | +0,43% | +0,15% | Aumentos generan más vol |
| PIB YoY | +0,34% | +0,29% | Aproximadamente simétrico |
| IPC Sub. MoM | +0,28% | +0,28% | Completamente simétrico |

Los **recortes de tipos del BCE** (+0,46% vs. +0,16%) generan significativamente más volatilidad que las subidas, interpretado como *bad news interpretation*. Los **aumentos del paro** (+0,43% vs. +0,15%) confirman la asimetría clásica de las malas noticias.

### 10.6. ¿Difieren los efectos entre categorías?

El test de **Kruskal-Wallis** evalúa si las tres categorías producen efectos distintos:

$$H = 10{,}71 \quad (p = 0{,}0047)$$

Se rechaza la hipótesis nula: **el tipo de publicación importa**. Los indicadores de actividad real generan la mayor volatilidad anormal.

### 10.7. Persistencia del efecto

Todos los indicadores muestran volatilidad elevada 1–2 días después del evento, sugiriendo que el mercado tarda 1–2 días hábiles en procesar completamente la información macro.

---

# CONCLUSIONES GENERALES DEL TRABAJO

## 11.1. Respuestas a las preguntas de investigación

**Q1: ¿Es predecible la volatilidad del IBEX 35?**
Sí, con un R² superior al 96% en todos los modelos supervisados. La persistencia temporal de la volatilidad es el motor principal, con `vol_lag1` como feature dominante.

**Q2: ¿Qué modelo ofrece mejor pronóstico?**
XGBoost alcanza el menor RMSE (0,0082), pero la diferencia con OLS y el modelo Simple no es estadísticamente significativa (test DM, $p > 0{,}05$). El GARCH queda significativamente por detrás.

**Q3: ¿Añaden valor las variables macroeconómicas?**
Sí, pero depende del modelo: empeoran el OLS (+7,2% RMSE) por multicolinealidad, pero mejoran significativamente el XGBoost (−14,1% RMSE), confirmando que la relación macro-volatilidad es **no lineal**. El VIX, bono español 10Y y tasa de paro son las variables macro con mayor contribución (SHAP).

**Q4: ¿Generan las publicaciones macro shocks puntuales?**
Sí. Los días de publicación presentan un 11,6% más de volatilidad ($p < 0{,}0001$). Los indicadores de actividad real generan el mayor impacto. Existe asimetría: las malas noticias generan más volatilidad que las buenas.

## 11.2. Limitaciones

1. **Autocorrelación mecánica del target.** La $V_t^{(21)}$ comparte 20 de 21 retornos entre días consecutivos, inflando el R² de cualquier modelo con $V_{t-1}$. No obstante, la señal dominante de `vol_lag1` es economicamente relevante.

2. **Frecuencia de variables macro.** Variables reales (PIB, paro) son trimestrales, generando largos forward-fills. Su contribución a frecuencia diaria es limitada.

3. **Período muestral del test.** El test set (2023–2025) es relativamente tranquilo. Resultados podrían variar en períodos de estrés.

Los hallazgos de este capítulo — especialmente la predicción de volatilidad y la identificación de drivers macro — constituyen la base para la fase de Análisis de Negocio, donde la volatilidad predicha se integrará en un modelo de optimización de carteras.

---

# REFERENCIAS BIBLIOGRÁFICAS

Bollerslev, T. (1986). *Generalized autoregressive conditional heteroskedasticity.* Journal of Econometrics, 31(3), 307–327.

Botey-Fullat, M., García-López, A., & Perea-García, J. (2023). *Forecasting European equity volatility with machine learning and macroeconomic variables.* Finance Research Letters, 52, 103–121.

Chen, T., & Guestrin, C. (2016). *XGBoost: A scalable tree boosting system.* Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 785–794.

Corsi, F. (2009). *A simple approximate long-memory model of realized volatility.* Journal of Financial Econometrics, 7(2), 174–196.

Diebold, F. X., & Mariano, R. S. (1995). *Comparing predictive accuracy.* Journal of Business & Economic Statistics, 13(3), 253–263.

Engle, R. F. (1982). *Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation.* Econometrica, 50(4), 987–1007.

Lundberg, S. M., & Lee, S.-I. (2017). *A unified approach to interpreting model predictions.* Advances in Neural Information Processing Systems 30 (NeurIPS 2017), 4765–4774.

Mandelbrot, B. (1963). *The variation of certain speculative prices.* Journal of Business, 36(4), 394–419.

Minga López, C. (2022). *Predicción de la volatilidad del IBEX 35 mediante variables macroeconómicas.* Trabajo de Fin de Grado, Universidad Francisco de Vitoria, Madrid.

Patton, A. J. (2011). *Volatility forecast comparison using imperfect volatility proxies.* Journal of Econometrics, 160(1), 246–256.
