"""
Carga de datos desde tfg.db y construcción del índice IBEX 35 sintético.
"""
import os
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st

# ── Rutas ─────────────────────────────────────────────────────────────────────
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
DB_PATH = os.path.join(REPO_ROOT, 'data', 'db', 'tfg.db')

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"No se encuentra la base de datos SQLite en {DB_PATH}. "
        "Asegúrate de que el archivo data/db/tfg.db está en el repositorio."
    )


@st.cache_data(ttl=3600)
def load_raw_data():
    """Carga dataset_maestro y ref_empresas desde SQLite."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql('SELECT * FROM dataset_maestro', conn, parse_dates=['fecha'])
        ref = pd.read_sql('SELECT * FROM ref_empresas', conn)
    df = df.sort_values(['ticker', 'fecha']).reset_index(drop=True)
    return df, ref


@st.cache_data(ttl=3600)
def build_ibex_index():
    """Construye el índice IBEX 35 sintético (equiponderado, base 100)."""
    df_raw, _ = load_raw_data()

    ibex = df_raw.groupby('fecha').agg(
        log_ret=('log_ret', 'mean'),
        vol_21d=('vol_hist_21d', 'mean'),
    ).sort_index()

    ibex['precio'] = 100 * np.exp(ibex['log_ret'].fillna(0).cumsum())
    return ibex


@st.cache_data(ttl=3600)
def detect_macro_events():
    """Detecta días de evento macro y alto impacto. Devuelve ibex con columnas de eventos."""
    df_raw, _ = load_raw_data()
    ibex = build_ibex_index()

    MACRO_EVENT_COLS = ['ipc_yoy', 'pib_yoy', 'tasa_paro', 'ipi_yoy',
                        'euribor_3m', 'tipo_dfr', 'ipc_sub_mom']
    HIGH_IMPACT_COLS = ['pib_yoy', 'tasa_paro']

    macro = (df_raw.drop_duplicates('fecha')
             .sort_values('fecha')
             .set_index('fecha')[MACRO_EVENT_COLS]
             .ffill())

    cambios = macro.diff().fillna(0)

    ibex['es_evento'] = (cambios.abs().sum(axis=1) > 0).astype(int).reindex(ibex.index).fillna(0).astype(int)

    cambios_hi = cambios[HIGH_IMPACT_COLS]
    ibex['es_evento_alto_impacto'] = (cambios_hi.abs().sum(axis=1) > 0).astype(int).reindex(ibex.index).fillna(0).astype(int)

    ibex['es_evento_o_previo'] = ibex['es_evento'] | ibex['es_evento'].shift(-1).fillna(0).astype(int)
    ibex['es_evento_hi_o_previo'] = ibex['es_evento_alto_impacto'] | ibex['es_evento_alto_impacto'].shift(-1).fillna(0).astype(int)

    # Detalle por variable (para calendario)
    for col in MACRO_EVENT_COLS:
        ibex[f'evento_{col}'] = (cambios[col].abs() > 0).astype(int).reindex(ibex.index).fillna(0).astype(int)

    # Valores macro actuales
    macro_vals = macro.reindex(ibex.index).ffill()
    for col in MACRO_EVENT_COLS:
        ibex[f'val_{col}'] = macro_vals[col]

    return ibex, MACRO_EVENT_COLS, HIGH_IMPACT_COLS


@st.cache_data(ttl=3600)
def get_macro_model_features():
    """Devuelve las features macro para el modelo XGBoost."""
    df_raw, _ = load_raw_data()

    MACRO_MODEL_COLS = [
        'vix', 'bono_es_10y', 'bono_de_10y', 'eur_usd', 'brent',
        'euribor_3m', 'tipo_dfr', 'ipc_yoy', 'ipc_sub_mom',
        'pib_yoy', 'tasa_paro', 'ipi_yoy',
    ]

    macro_model = (df_raw.drop_duplicates('fecha')
                   .sort_values('fecha')
                   .set_index('fecha')[MACRO_MODEL_COLS]
                   .ffill())

    return macro_model, MACRO_MODEL_COLS
