# MAPEO: SECCIONES MEMORIA → CELDAS GITHUB

**Repositorio:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35

**Notebooks Ingeniería del Dato:**
- `01_ingenieria_dato/01_ETL_empresas.ipynb`
- `01_ingenieria_dato/02_ETL_macro.ipynb`
- `01_ingenieria_dato/03_validacion.ipynb`
- `01_ingenieria_dato/04_EDA.ipynb`

---

## SECCIÓN 3: Origen de los datos

### 3.1. Reuters Eikon — Precios de empresas

**Implementación:**
- Lectura de fichero de referencia con 35 empresas IBEX 35
- Detección automática de cabeceras (problema metadatos Reuters)
- Función `leer_empresa()` con parseo de fechas y tipos numéricos

**Celdas GitHub:**
- 📍 **Lectura fichero referencia:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-4
- 📍 **Función leer_empresa():** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-6
- 📍 **Procesamiento bucle 35 empresas:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-8
- 📍 **Consolidación dataset:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-10

### 3.2-3.6. Fuentes macroeconómicas (Reuters, Investing, INE, BCE)

**Implementación:**
- 4 funciones de parsing especializadas (reuters, investing, ine, bce)
- Manejo de formatos heterogéneos (fechas, decimales, matrices)
- 5 tablas SQLite organizadas por frecuencia

**Celdas GitHub:**
- 📍 **Funciones parsing especializadas:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-4
- 📍 **Bloque 1 - Actividad económica:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-5
- 📍 **Bloque 2 - Condiciones monetarias:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-7
- 📍 **Bloque 3 - Precios e inflación:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-9
- 📍 **Bloque 4 - Riesgo global:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-11
- 📍 **Consolidación en 5 tablas SQLite:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-14

---

## SECCIÓN 4: Extracción y transformación de datos

### 4.1. ETL de precios de empresas

**Implementación:**
- Procesamiento secuencial de 35 archivos Reuters
- Cálculo de log-retornos: `r_t = ln(P_t / P_{t-1})`
- Volatilidad histórica 21d: `σ = √252 × std(r_{-20..0})`

**Celdas GitHub:**
- 📍 **Procesamiento 35 empresas en bucle:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-8
- 📍 **Cálculo variables derivadas (log_ret, vol_hist_21d):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-12

**Casos extremos de cobertura temporal:**
- 📍 **Análisis de heterogeneidad por empresa:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-10

### 4.2. ETL de variables macroeconómicas

**Implementación:**
- Parsing diferenciado por fuente (Reuters, Investing, INE, BCE)
- Organización en 4 bloques temáticos (actividad, monetarias, inflación, riesgo)
- Consolidación en 5 tablas SQLite

**Celdas GitHub:**
- 📍 **Funciones de parsing por formato:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-4
- 📍 **Consolidación en tablas macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-14

---

## SECCIÓN 5: Limpieza y alineación temporal

### 5.1. Tratamiento de nulos en precios

**Implementación:**
- Detección de 8 nulos en columna close (4 empresas)
- Interpolación lineal: estima puntos medios entre días adyacentes
- Recalcula log_ret y vol_hist_21d post-imputación

**Celdas GitHub:**
- 📍 **Identificación de nulos:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-15
- 📍 **Interpolación lineal:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-17

### 5.2-5.3. Nulos estructurales y frecuencias múltiples

**Implementación:**
- Forward-fill en macro (propaga último valor conocido)
- Alineación temporal al calendario bursátil (5.323 fechas)
- merge_asof para evitar data leakage

**Celdas GitHub:**
- 📍 **Análisis de nulos estructurales:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/03_validacion.ipynb#cell-10
- 📍 **Alineación temporal (forward-fill + merge_asof):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/03_validacion.ipynb#cell-8

### 5.5. Cobertura del dataset maestro

**Implementación:**
- Análisis de 31 variables (cobertura 16.8% a 99.8%)
- Identificación de limitaciones (PMI, VIBEX, spread)
- Resultado: dataset maestro 157.455 × 31

**Celdas GitHub:**
- 📍 **Tabla de cobertura por variable:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/03_validacion.ipynb#cell-10
- 📍 **Heatmap de cobertura temporal:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-10

---

## SECCIÓN 6: Análisis exploratorio de datos (EDA)

### 6.1. Estadísticos descriptivos

**Implementación:**
- Media, std, asimetría, curtosis de log-retornos (157.420 obs)
- Volatilidad media IBEX 35: 0.2926 (29.26% anualizada)
- Curtosis extremadamente elevada: 19,00 (vs 3 normal)
- Asimetría por empresa: 20 negativa, 15 positiva

**Celdas GitHub:**
- 📍 **Tabla de estadísticos por empresa:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-16
- 📍 **Evolución temporal volatilidad IBEX 35:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-18

### 6.2. Tests de estacionariedad (ADF)

**Implementación:**
- Augmented Dickey-Fuller test (autolag='AIC', α=0.05)
- Precios NO estacionarios, log-retornos SÍ estacionarios
- Volatilidad SÍ estacionaria

**Celdas GitHub:**
- 📍 **Test ADF en todas las series:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-24

### 6.3. Distribución de retornos y test de normalidad (Jarque-Bera)

**Implementación:**
- Test Jarque-Bera (H₀: distribución normal)
- Rechaza normalidad en TODAS las variables financieras (p < 0,0001)
- JB estadísticos: log_ret=1.678.375, vol_hist=25.346, vix=23.312

**Celdas GitHub:**
- 📍 **Test Jarque-Bera + gráficos:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-36
- 📍 **Comparación antes/después log-retornos:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-12
- 📍 **Distribución vs normal teórica:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-36

### 6.4. Memoria larga de la volatilidad (ACF/PACF)

**Implementación:**
- ACF/PACF de 60 retardos
- ACF significativa en todos los lags hasta 60 (persistencia)
- Picos PACF en lags 1, 5, 21 (escalas diaria, semanal, mensual)

**Celdas GitHub:**
- 📍 **ACF/PACF con 60 lags:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-26

### 6.5. Detección y tratamiento de outliers

**Implementación:**
- IQR: método robusto, identifica 8.169 outliers vol_hist (5,20%)
- Z-score: método paramétrico, identifica 2.801 outliers (1,78%)
- Decisión: MANTENER outliers (señal económica real, periodos crisis)

**Celdas GitHub:**
- 📍 **Detección IQR + Z-score:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-34

### 6.6. Volatilidad por empresa y sector (Kruskal-Wallis)

**Implementación:**
- Test de Kruskal-Wallis entre 11 sectores GICS
- H = 7.259,89 (p ≈ 0): diferencias significativas
- Post-hoc Mann-Whitney + corrección Bonferroni: 47/55 pares significativos
- Sectores: Real Estate (35,4%) > Materials (34,2%) > Financials (30,7%)

**Celdas GitHub:**
- 📍 **Cálculo volatilidad por sector:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-20
- 📍 **Test Kruskal-Wallis + Mann-Whitney:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-40

### 6.7. Relación con variables macro (correlaciones y CCF)

**Implementación:**
- Correlaciones de Pearson: VIBEX (+0,824), VIX (+0,754), VSTOXX (+0,728)
- Correlaciones negativas: IPI YoY (−0,442), PIB YoY (−0,429)
- Cross-correlación con 60 lags: VIX lag 0, spread/euribor lag 59+

**Celdas GitHub:**
- 📍 **Evolución temporal 8 variables macro:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-22
- 📍 **Correlaciones Pearson (matriz + heatmap):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-28
- 📍 **Co-evolución volatilidad vs VIX vs Euribor:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-32
- 📍 **Cross-correlación con lags 0-60:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-38

### 6.8. Split temporal train/test

**Implementación:**
- Split 80/20 por fecha (no aleatorio)
- Train: 2.764 obs (2012-05-02 → 2023-02-16)
- Test: 691 obs (2023-02-17 → 2025-10-31)
- Evita data leakage: información histórica solo

**Celdas GitHub:**
- 📍 **Visualización split temporal:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-29

---

## SECCIÓN 7: Decisiones finales y conclusión

**Implementación:**
- Tabla formal de decisión de variables
- MANTENER: 19 variables (vol_hist_21d, log_ret, 12 macro principales)
- REDUNDANTE: tipo_mlf, tipo_mro (colinealidad perfecta con tipo_dfr)
- USO LIMITADO: pmi (cobertura 16,8% desde 2023)

**Celdas GitHub:**
- 📍 **Tabla de decisión variables:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/04_EDA.ipynb#cell-42

---

## SECCIÓN 8: Base de datos final

**Implementación:**
- SQLite con 8 tablas (precios, ref, 5 macro, maestro)
- 325.000+ registros totales
- Backups en CSV y Parquet
- Diseño en estrella: trazabilidad + eficiencia

**Celdas GitHub:**
- 📍 **Carga precios en SQLite:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-19
- 📍 **Carga macro en SQLite:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-18
- 📍 **Dataset maestro (consolidación final):** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/03_validacion.ipynb#cell-12
- 📍 **Verificación final de todas las tablas:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/02_ETL_macro.ipynb#cell-20

---

## CÓMO USAR ESTE MAPEO EN WORD

1. **Abre el documento Word:** `Memoria_Ingenieria_del_Dato_v2.docx`

2. **Para cada sección**, inserta un hipervínculo:
   - Selecciona el texto (ej: "la función `leer_empresa()`")
   - Menú → Insertar → Hipervínculo (Ctrl+K)
   - Pega la URL de la celda GitHub correspondiente
   - Ejemplo: `https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/01_ingenieria_dato/01_ETL_empresas.ipynb#cell-6`

3. **Estructura de URLs GitHub:**
   ```
   https://github.com/adricelada143/TFG---Volatilidad-IBEX-35/blob/main/{notebook_path}#{cell_reference}
   ```
   - `{notebook_path}`: ruta del notebook (ej: `01_ingenieria_dato/01_ETL_empresas.ipynb`)
   - `{cell_reference}`: referencia de la celda (ej: `cell-6` para celda 6)

4. **Commit final en GitHub:**
   ```bash
   git add outputs/Memoria_Ingenieria_del_Dato_v2.docx
   git commit -m "docs: Add GitHub cell hyperlinks to Ingeniería del Dato memoria"
   git push
   ```

---

**Documento generado:** 12 de abril de 2026
**Repositorio:** https://github.com/adricelada143/TFG---Volatilidad-IBEX-35
