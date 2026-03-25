# TFG — Impacto de las variables macroeconómicas en la volatilidad del IBEX 35

**Autor:** Adrián Celada Calderón
**Grado:** Business Analytics — Universidad Francisco de Vitoria (UFV), Madrid
**Curso:** 2025-26

---

## Descripción

Este repositorio contiene el código y los análisis del TFG, cuyo objetivo es estudiar cómo las variables macroeconómicas influyen en la volatilidad del IBEX 35 e integrar dicha relación en un modelo de optimización de carteras.

---

## Estructura del proyecto

```
proyecto/
├── 01_ingenieria_dato/          # ETL y EDA
│   ├── 01_ETL_empresas.ipynb    # Extracción y limpieza de las 35 empresas IBEX 35
│   ├── 02_ETL_macro.ipynb       # ETL de variables macroeconómicas (4 bloques)
│   ├── 03_validacion.ipynb      # Dataset maestro y control de calidad
│   └── 04_EDA.ipynb             # Análisis exploratorio completo
│
├── 02_analisis_dato/            # Modelos predictivos de volatilidad
│
├── 03_analisis_negocio/         # Optimización de carteras
│
├── data/
│   ├── db/                      # Base de datos SQLite (no versionada, >50MB)
│   └── processed/               # CSVs de variables macro (pequeños)
│
└── outputs/
    └── figuras/                 # Gráficos generados por los notebooks
```

---

## Datos

| Fuente | Variables |
|---|---|
| Reuters Eikon | Precios diarios OHLCV de 35 empresas (2005–2025) |
| Reuters Eikon | PIB, PMI, Tasa de Paro, IPC España |
| INE | IPI, IPC Subyacente |
| BCE / ECB Data Portal | Euribor 3M, Euribor 6M |
| BCE (epdata.es) | Tipos oficiales DFR, MLF, MRO |
| Investing.com | Bono ES/DE 10Y, Spread, VIX, VIBEX, VSTOXX, Brent |
| Reuters | Gas Natural TTF, EUR/USD |

> Los archivos de datos grandes (`tfg.db`, `dataset_maestro.csv`, `precios_empresas.csv`) no están versionados por tamaño. Se generan ejecutando los notebooks en orden.

---

## Instalación

```bash
pip install pandas numpy sqlalchemy matplotlib seaborn scipy statsmodels openpyxl
```

---

## Ejecución

Ejecutar los notebooks en orden dentro de `01_ingenieria_dato/`:

1. `01_ETL_empresas.ipynb`
2. `02_ETL_macro.ipynb`
3. `03_validacion.ipynb`
4. `04_EDA.ipynb`
