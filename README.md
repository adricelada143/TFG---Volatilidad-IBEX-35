# Gestión Táctica de Carteras IBEX 35
## Impacto de las variables macroeconómicas en la volatilidad del IBEX 35

**Autor:** Adrián Celada Calderón  
**Titulación:** Business Analytics  
**Universidad:** Universidad Francisco de Vitoria  
**Año:** 2025-26

---

## 📊 Descripción del Proyecto

Este TFG analiza el impacto de las variables macroeconómicas en la volatilidad del IBEX 35 mediante tres enfoques complementarios:

1. **Ingeniería del Dato**: Procesamiento de datos financieros y macroeconómicos
2. **Análisis del Dato**: Modelos de volatilidad y event study de publicaciones macro
3. **Análisis de Negocio**: Dashboard interactivo con estrategias de gestión táctica de carteras

---

## 🚀 Cómo ejecutar el Dashboard

### Requisitos Previos
- Python 3.10+
- pip o conda

### Instalación

1. **Clonar el repositorio**
```bash
git clone git@github.com:adricelada143/TFG---Volatilidad-IBEX-35.git
cd "proyecto"
```

2. **Crear un entorno virtual (recomendado)**
```bash
# Con venv
python -m venv venv
source venv/bin/activate  # En macOS/Linux
# o en Windows:
# venv\Scripts\activate

# O con conda
conda create -n tfg-ibex python=3.11
conda activate tfg-ibex
```

3. **Instalar dependencias**
```bash
cd 03_analisis_negocio/dashboard
pip install -r requirements.txt
```

### Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 📁 Estructura del Proyecto

```
proyecto/
├── 01_ingenieria_dato/          # Procesamiento y ETL de datos
│   ├── 01_ETL_empresas.ipynb           # Carga y limpieza de datos financieros
│   ├── 02_ETL_macro.ipynb              # Procesamiento de datos macroeconómicos
│   ├── 03_validacion.ipynb             # Validación de integridad
│   └── 04_EDA.ipynb                    # Análisis exploratorio
│
├── 02_analisis_dato/            # Modelos analíticos
│   ├── 01_modelos_volatilidad.ipynb    # Modelos HAR, GARCH, XGBoost
│   └── 02_event_study_macro.ipynb      # Event study: impacto publicaciones macro
│
├── 03_analisis_negocio/         # Dashboard y aplicación final
│   ├── dashboard/
│   │   ├── app.py                      # Página principal (Streamlit)
│   │   ├── requirements.txt            # Dependencias
│   │   ├── assets/
│   │   │   └── style.css               # Estilos custom
│   │   ├── pages/
│   │   │   ├── 1_Resumen_Ejecutivo.py
│   │   │   ├── 2_Estrategias.py
│   │   │   ├── 3_Riesgo.py
│   │   │   ├── 4_Asesor_De_Carteras.py
│   │   │   ├── 5_Predictor.py
│   │   │   └── 6_Plan_De_Accion.py
│   │   └── utils/
│   │       ├── data_loader.py          # Carga de datos
│   │       └── strategies.py           # Lógica de estrategias
│   └── analisis_negocio.md             # Análisis ejecutivo
│
├── data/
│   ├── db/                      # Base de datos SQLite
│   │   └── tfg.db              # Datos procesados (no incluido en git por tamaño)
│   └── processed/              # Datos en CSV
│
└── outputs/                     # Resultados, figuras y tablas
```

---

## 📊 Páginas del Dashboard

1. **Resumen Ejecutivo** — KPIs principales y hallazgos clave
2. **Estrategias** — Estrategias de trading basadas en volatilidad
3. **Riesgo** — Análisis de riesgo y Value-at-Risk
4. **Asesor de Carteras** — Recomendaciones de composición de cartera
5. **Predictor** — Predicciones de volatilidad futura
6. **Plan de Acción** — Recomendaciones operacionales

---

## 📚 Datos Utilizados

- **Datos Financieros**: Precios y rendimientos del IBEX 35 (empresas componentes)
- **Datos Macroeconómicos**: IPC, PIB, Paro, Euríbor, tipos del BCE (Refinitiv/Reuters)
- **Período**: 2020-2024 (datos diarios y mensuales)

**Nota**: Los datos originales brutos no están incluidos en el repositorio por razones de tamaño y confidencialidad (están versionados en una base de datos SQLite).

---

## 🔧 Funcionalidades Principales

### Dashboard Interactivo
- Gráficos dinámicos con Plotly
- Filtros por fechas y activos
- Exportación de análisis

### Modelos Incluidos
- **HAR (Heterogeneous Auto-Regressive)**: Volatilidad a múltiples escalas
- **XGBoost**: Machine learning para predicción
- **Event Study**: Impacto de publicaciones macro
- **Value-at-Risk (VaR)**: Estimación de riesgo

### Estrategias
- Market neutral (long/short)
- Dynamic hedging
- Volatility-targeting
- Rotation basada en macro

---

## 📖 Cómo usar el Dashboard

### Primera Visita
1. Abre la app en `http://localhost:8501`
2. Consulta el **Resumen Ejecutivo** para entender los hallazgos principales
3. Navega por las otras pestañas según tu interés

### Exploración de Datos
- Filtra por fechas en la barra lateral
- Selecciona activos específicos del IBEX 35
- Ajusta parámetros de volatilidad (ventana, método)

### Generación de Reportes
- Descarga gráficos directamente desde Streamlit (botón 📷 arriba a la derecha)
- Exporta datos filtrados en formato CSV

---

## ⚠️ Requisitos del Sistema

- **RAM**: 4 GB mínimo (8 GB recomendado)
- **Disco**: 500 MB disponibles
- **Conexión**: No requiere internet una vez instalado

---

## 🔐 Privacidad y Datos

- Todos los datos están almacenados localmente en `data/db/tfg.db`
- No se transmite información a servidores externos
- Los datos macroeconómicos son públicos (fuentes: Refinitiv, Banco de España, BCE)

---

## 📝 Solución de Problemas

### "ModuleNotFoundError" al ejecutar
```bash
# Asegúrate de estar en el entorno virtual correcto
pip install -r requirements.txt
```

### App lenta o se queda congelada
- El primer arranque carga caché de datos (normal)
- Reduce el rango de fechas si aplicas filtros muy grandes
- Cierra otras aplicaciones si tienes problemas de RAM

### Puerto 8501 en uso
```bash
streamlit run app.py --server.port 8502
```

---

## 📞 Contacto

**Autor:** Adrián Celada Calderón  
**Email:** [tu email si es necesario]  
**GitHub:** [tu perfil]

---

## 📄 Licencia

Este proyecto es una Tesis Final de Grado (TFG) de la Universidad Francisco de Vitoria.

---

**Última actualización:** Mayo de 2026
