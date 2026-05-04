"""
Lógica de estrategias de cartera, backtesting y cálculo de métricas.
Extraído del notebook 01_estrategia_carteras.ipynb.
"""
import numpy as np
import pandas as pd
import streamlit as st
from scipy.stats import mannwhitneyu, norm
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

from utils.data_loader import detect_macro_events, get_macro_model_features

SEED = 42


def load_css():
    """Inyecta el CSS global del dashboard. Llamar al inicio de cada página."""
    import os
    css_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'style.css')
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

STRATEGY_NAMES = {
    'Buy & Hold': 'w_baseline',
    'A: Volatilidad': 'w_vol',
    'B: Calendario Macro': 'w_macro',
    'C: Combinada': 'w_comb',
}

STRATEGY_COLORS = {
    'Buy & Hold': '#1f77b4',
    'A: Volatilidad': '#ff7f0e',
    'B: Calendario Macro': '#2ca02c',
    'C: Combinada': '#d62728',
}

MACRO_EVENT_LABELS = {
    'ipc_yoy': 'IPC interanual',
    'pib_yoy': 'PIB interanual',
    'tasa_paro': 'Tasa de paro',
    'ipi_yoy': 'IPI interanual',
    'euribor_3m': 'Euríbor 3M',
    'tipo_dfr': 'Tipo DFR (BCE)',
    'ipc_sub_mom': 'IPC subyacente',
}

# ── Plotly: tema profesional consistente ──────────────────────────────────────
_FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif"


def style_plotly_chart(fig, height=None):
    """Aplica estilo institucional consistente a un gráfico Plotly."""
    updates = dict(
        font=dict(family=_FONT, color="#2C3E50", size=13),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=50, b=40, l=60, r=20),
        hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#E5E9F0"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E5E9F0",
            borderwidth=1,
            font=dict(size=11),
        ),
    )
    if height:
        updates['height'] = height
    fig.update_layout(**updates)
    fig.update_xaxes(
        gridcolor="rgba(0,0,0,0.04)",
        zerolinecolor="rgba(0,0,0,0.08)",
        title_font=dict(size=12, color="#5D6D7E"),
        tickfont=dict(size=11, color="#5D6D7E"),
    )
    fig.update_yaxes(
        gridcolor="rgba(0,0,0,0.04)",
        zerolinecolor="rgba(0,0,0,0.08)",
        title_font=dict(size=12, color="#5D6D7E"),
        tickfont=dict(size=11, color="#5D6D7E"),
    )
    return fig


@st.cache_data(ttl=3600)
def train_xgboost_model():
    """Entrena el modelo XGBoost HAR+macro y devuelve predicciones en test."""
    ibex, _, _ = detect_macro_events()
    macro_model, MACRO_MODEL_COLS = get_macro_model_features()

    # Features HAR
    ibex = ibex.copy()
    ibex['vol_lag1'] = ibex['vol_21d'].shift(1)
    ibex['vol_lag5'] = ibex['vol_21d'].rolling(5).mean().shift(1)
    ibex['vol_lag21'] = ibex['vol_21d'].rolling(21).mean().shift(1)

    HAR_FEATS = ['vol_lag1', 'vol_lag5', 'vol_lag21']
    ALL_FEATS = HAR_FEATS + MACRO_MODEL_COLS
    TARGET = 'vol_21d'

    df_model = ibex.join(macro_model).dropna(
        subset=[TARGET] + ALL_FEATS
    ).sort_index()

    # Split 80/20
    n = len(df_model)
    cut = int(n * 0.80)
    df_train = df_model.iloc[:cut]
    df_test = df_model.iloc[cut:]

    X_train = df_train[ALL_FEATS].values
    y_train = df_train[TARGET].values
    X_test = df_test[ALL_FEATS].values

    xgb = XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        random_state=SEED, n_jobs=-1,
    )
    xgb.fit(X_train, y_train)

    df_test = df_test.copy()
    df_test['vol_pred'] = xgb.predict(X_test)
    df_test['vol_p75'] = df_test['vol_pred'].rolling(63, min_periods=21).quantile(0.75)
    df_test['alta_vol'] = (df_test['vol_pred'] > df_test['vol_p75']).fillna(0).astype(int)

    # Feature importance
    feat_imp = pd.Series(xgb.feature_importances_, index=ALL_FEATS).sort_values(ascending=False)

    return df_test, xgb, feat_imp, ALL_FEATS, df_train.index[-1]


@st.cache_data(ttl=3600)
def run_backtest():
    """Ejecuta el backtesting de las 4 estrategias. Devuelve DataFrame bt y métricas."""
    df_test, _, _, _, _ = train_xgboost_model()

    bt = df_test[['log_ret', 'vol_21d', 'vol_pred', 'alta_vol',
                   'es_evento', 'es_evento_o_previo',
                   'es_evento_alto_impacto', 'es_evento_hi_o_previo',
                   'precio']].copy()

    # Copiar columnas de evento por variable
    ibex, MACRO_EVENT_COLS, _ = detect_macro_events()
    for col in MACRO_EVENT_COLS:
        if f'evento_{col}' in ibex.columns:
            bt[f'evento_{col}'] = ibex[f'evento_{col}'].reindex(bt.index).fillna(0).astype(int)
        if f'val_{col}' in ibex.columns:
            bt[f'val_{col}'] = ibex[f'val_{col}'].reindex(bt.index)

    # Pesos
    bt['w_baseline'] = 1.0
    bt['w_vol'] = np.where(bt['alta_vol'] == 1, 0.5, 1.0)
    bt['w_macro'] = np.where(bt['es_evento_o_previo'] == 1, 0.5, 1.0)
    bt['w_comb'] = np.where(
        (bt['alta_vol'] == 1) | (bt['es_evento_hi_o_previo'] == 1),
        0.5, 1.0
    )

    # Retornos y equity curves
    for name, w_col in STRATEGY_NAMES.items():
        bt[f'ret_{w_col}'] = bt['log_ret'] * bt[w_col]
        bt[f'eq_{w_col}'] = 100 * np.exp(bt[f'ret_{w_col}'].cumsum())

    return bt


def calc_metrics(returns, name, ann_factor=252):
    """Calcula métricas de rendimiento a partir de retornos simples diarios."""
    ret_mean = returns.mean() * ann_factor
    ret_std = returns.std() * np.sqrt(ann_factor)
    sharpe = ret_mean / ret_std if ret_std > 0 else 0

    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    dd = (equity - peak) / peak
    mdd = dd.min()
    calmar = ret_mean / abs(mdd) if mdd != 0 else 0

    # VaR y CVaR
    var_95 = returns.quantile(0.05)
    cvar_95 = returns[returns <= var_95].mean()

    return {
        'Estrategia': name,
        'Rent. anual (%)': ret_mean * 100,
        'Vol. anual (%)': ret_std * 100,
        'Sharpe': sharpe,
        'Max Drawdown (%)': mdd * 100,
        'Calmar': calmar,
        'VaR 95% (%)': var_95 * 100,
        'CVaR 95% (%)': cvar_95 * 100,
    }


def get_all_metrics(bt):
    """Devuelve DataFrame con métricas de todas las estrategias."""
    metrics = []
    for name, w_col in STRATEGY_NAMES.items():
        simple_ret = np.exp(bt[f'ret_{w_col}']) - 1
        m = calc_metrics(simple_ret, name)
        m['% días 100% inv.'] = (bt[w_col] == 1.0).mean() * 100
        metrics.append(m)
    return pd.DataFrame(metrics).set_index('Estrategia')


def calc_drawdown(bt, w_col):
    """Calcula serie de drawdown para una estrategia."""
    simple_ret = np.exp(bt[f'ret_{w_col}']) - 1
    equity = (1 + simple_ret).cumprod()
    dd = (equity - equity.cummax()) / equity.cummax() * 100
    return dd


def calc_rolling_sharpe(bt, w_col, window=63):
    """Calcula Sharpe ratio rolling."""
    rets = np.exp(bt[f'ret_{w_col}']) - 1
    rolling_mean = rets.rolling(window).mean() * 252
    rolling_std = rets.rolling(window).std() * np.sqrt(252)
    return rolling_mean / rolling_std


def get_best_worst_days(bt, w_col, n=10):
    """Devuelve los n mejores y peores días."""
    rets = (np.exp(bt[f'ret_{w_col}']) - 1) * 100
    worst = rets.nsmallest(n).reset_index()
    worst.columns = ['Fecha', 'Retorno (%)']
    best = rets.nlargest(n).reset_index()
    best.columns = ['Fecha', 'Retorno (%)']
    return best, worst


def get_current_signal(bt):
    """Devuelve el estado actual de las señales para el predictor."""
    last = bt.iloc[-1]
    vol_pred = last['vol_pred']
    vol_actual = last['vol_21d']
    alta_vol = int(last['alta_vol'])
    es_evento = int(last.get('es_evento', 0))
    es_evento_hi = int(last.get('es_evento_alto_impacto', 0))

    # Percentil de vol predicha en histórico
    vol_pctile = (bt['vol_pred'] <= vol_pred).mean() * 100

    # Semáforo
    if vol_pctile >= 75:
        semaforo = 'rojo'
        recomendacion = 'REDUCIR exposición al 50%'
    elif vol_pctile >= 50:
        semaforo = 'amarillo'
        recomendacion = 'VIGILAR — mantener con cautela'
    else:
        semaforo = 'verde'
        recomendacion = 'MANTENER exposición completa'

    return {
        'fecha': bt.index[-1],
        'vol_pred': vol_pred,
        'vol_actual': vol_actual,
        'alta_vol': alta_vol,
        'es_evento': es_evento,
        'es_evento_hi': es_evento_hi,
        'vol_pctile': vol_pctile,
        'semaforo': semaforo,
        'recomendacion': recomendacion,
    }


# ── Asesor de Carteras ───────────────────────────────────────────────────────

ASESOR_VARIABLES = {
    'PIB': 'pib_yoy',
    'Tasa de Paro': 'tasa_paro',
    'IPC': 'ipc_yoy',
    'Tipo BCE': 'tipo_dfr',
    'IPI': 'ipi_yoy',
    'Euríbor': 'euribor_3m',
    'IPC Subyacente': 'ipc_sub_mom',
}

MACRO_RECOMMENDATIONS = {
    'pib_yoy': {
        'sube': {'accion': 'AUMENTAR', 'tier': 1,
                 'desc': 'PIB al alza — señal histórica fuerte alcista'},
        'baja': {'accion': 'REDUCIR', 'tier': 1,
                 'desc': 'PIB a la baja — señal histórica fuerte bajista'},
    },
    'tasa_paro': {
        'sube': {'accion': 'CAUTELA', 'tier': 2,
                 'desc': 'Paro al alza — riesgo moderado, vigilar exposición'},
        'baja': {'accion': 'AUMENTAR', 'tier': 1,
                 'desc': 'Paro a la baja — señal histórica fuerte alcista'},
    },
    'tipo_dfr': {
        'sube': {'accion': 'REDUCIR', 'tier': 1,
                 'desc': 'BCE sube tipo — señal histórica fuerte bajista'},
        'baja': {'accion': 'MANTENER', 'tier': 2,
                 'desc': 'BCE baja tipo — alta vol intradía, mantener con cobertura'},
    },
    'ipc_yoy': {
        'sube': {'accion': 'MANTENER', 'tier': 2,
                 'desc': 'IPC al alza — leve sesgo alcista, mantener posición'},
        'baja': {'accion': 'MANTENER', 'tier': 2,
                 'desc': 'IPC a la baja — impacto neutral'},
    },
    'ipi_yoy': {
        'sube': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'IPI — sin señal accionable (ruido)'},
        'baja': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'IPI — sin señal accionable (ruido)'},
    },
    'euribor_3m': {
        'sube': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'Euríbor — sin señal accionable (ruido)'},
        'baja': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'Euríbor — sin señal accionable (ruido)'},
    },
    'ipc_sub_mom': {
        'sube': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'IPC subyacente — sin señal accionable (ruido)'},
        'baja': {'accion': 'MANTENER', 'tier': 3,
                 'desc': 'IPC subyacente — sin señal accionable (ruido)'},
    },
}

INVESTOR_PROFILES = {
    'Conservador': {
        'strategy': 'C: Combinada',
        'desc': 'Prioriza protección de capital. Reduce exposición en alta volatilidad y eventos macro.',
        'icon': '🛡️',
        'color': '#2563EB',
    },
    'Moderado': {
        'strategy': 'B: Calendario Macro',
        'desc': 'Equilibrio rentabilidad/riesgo. Solo reduce exposición en publicaciones macro.',
        'icon': '⚖️',
        'color': '#D97706',
    },
    'Agresivo': {
        'strategy': 'Buy & Hold',
        'desc': 'Maximiza exposición. Acepta toda la volatilidad a cambio de mayor retorno potencial.',
        'icon': '🚀',
        'color': '#DC2626',
    },
}

ACCION_COLORS = {
    'AUMENTAR': '#2ca02c',
    'MANTENER': '#1f77b4',
    'CAUTELA': '#ff7f0e',
    'REDUCIR': '#d62728',
}

# ── Mapeo de exposición: (acción, tier) → % de exposición objetivo ────────
EXPOSURE_PCT = {
    ('AUMENTAR', 1): 120,   # Sobreponderar — señal fuerte alcista
    ('AUMENTAR', 2): 110,   # Leve sobreponderar
    ('MANTENER', 2): 100,   # Sin cambio
    ('MANTENER', 3): 100,   # Sin señal → no mover
    ('CAUTELA',  2): 80,    # Leve infraponderación
    ('REDUCIR',  2): 70,    # Reducir moderadamente
    ('REDUCIR',  1): 50,    # Reducir a la mitad — señal fuerte bajista
}


def calc_exposure(variable, direction, portfolio_eur):
    """Calcula la exposición objetivo en % y € para una variable macro.

    Args:
        variable: clave de variable macro (ej: 'pib_yoy')
        direction: 'sube' o 'baja'
        portfolio_eur: valor actual de la cartera IBEX en €

    Returns:
        dict con accion, tier, desc, exposure_pct, target_eur, delta_eur
    """
    rec_table = MACRO_RECOMMENDATIONS.get(variable, {})
    if direction in ('sube', 'baja') and direction in rec_table:
        rec = rec_table[direction]
    else:
        rec = {'accion': 'MANTENER', 'tier': 3,
               'desc': 'Selecciona la dirección esperada para una recomendación específica'}

    accion = rec['accion']
    tier = rec['tier']
    exposure_pct = EXPOSURE_PCT.get((accion, tier), 100)
    target_eur = portfolio_eur * exposure_pct / 100
    delta_eur = target_eur - portfolio_eur

    return {
        'accion': accion,
        'tier': tier,
        'desc': rec['desc'],
        'exposure_pct': exposure_pct,
        'target_eur': target_eur,
        'delta_eur': delta_eur,
    }


def analyze_macro_event(variable, direction=None):
    """Analiza el impacto histórico de un evento macro sobre el IBEX 35.
    Usa el dataset completo (no solo test) para máxima evidencia."""
    ibex, MACRO_EVENT_COLS, _ = detect_macro_events()

    ecol = f'evento_{variable}'
    vcol = f'val_{variable}'
    if ecol not in ibex.columns:
        return None

    ibex = ibex.copy()

    # Forward returns (acumulados desde t+1)
    cum = ibex['log_ret'].cumsum()
    ibex['fwd_1d'] = cum.shift(-1) - cum
    ibex['fwd_5d'] = cum.shift(-5) - cum
    ibex['fwd_21d'] = cum.shift(-21) - cum

    # Eventos de esta variable
    events = ibex[ibex[ecol] == 1].copy()
    if len(events) == 0:
        return None

    # Dirección del cambio
    val_diff = ibex[vcol].diff()
    events['val_change'] = val_diff.reindex(events.index)
    events['direccion'] = np.where(
        events['val_change'] > 0, 'sube',
        np.where(events['val_change'] < 0, 'baja', 'sin_cambio'),
    )

    # Filtrar por dirección si se indica
    if direction in ('sube', 'baja'):
        subset = events[events['direccion'] == direction]
    else:
        subset = events

    n_events = len(subset)
    if n_events == 0:
        return None

    # Retornos forward del subconjunto
    ret_1d = subset['fwd_1d'].dropna()
    ret_5d = subset['fwd_5d'].dropna()
    ret_21d = subset['fwd_21d'].dropna()

    # Días normales (sin evento de esta variable)
    normal = ibex[ibex[ecol] == 0]
    normal_1d = normal['fwd_1d'].dropna()
    normal_21d = normal['fwd_21d'].dropna()

    # Volatilidad del día del evento vs. normal
    vol_evento = subset['log_ret'].abs().mean()
    vol_normal = normal['log_ret'].abs().mean()

    try:
        _, p_vol = mannwhitneyu(
            subset['log_ret'].abs().dropna(),
            normal['log_ret'].abs().dropna(),
            alternative='greater',
        )
    except Exception:
        p_vol = 1.0

    # Recomendación según tabla empírica
    rec_table = MACRO_RECOMMENDATIONS.get(variable, {})
    if direction in ('sube', 'baja') and direction in rec_table:
        rec = rec_table[direction]
    else:
        rec = {'accion': 'MANTENER', 'tier': 3,
               'desc': 'Selecciona la dirección esperada para una recomendación específica'}

    first_year = ibex.index[0].year

    return {
        'variable': variable,
        'direction': direction,
        'n_events': n_events,
        'n_up': int((events['direccion'] == 'sube').sum()),
        'n_down': int((events['direccion'] == 'baja').sum()),
        'recommendation': rec,
        'ret_1d_mean': ret_1d.mean() * 100 if len(ret_1d) > 0 else 0,
        'ret_5d_mean': ret_5d.mean() * 100 if len(ret_5d) > 0 else 0,
        'ret_21d_mean': ret_21d.mean() * 100 if len(ret_21d) > 0 else 0,
        'ret_1d_std': ret_1d.std() * 100 if len(ret_1d) > 0 else 0,
        'ret_5d_std': ret_5d.std() * 100 if len(ret_5d) > 0 else 0,
        'ret_21d_std': ret_21d.std() * 100 if len(ret_21d) > 0 else 0,
        'vol_evento': vol_evento * 100,
        'vol_normal': vol_normal * 100,
        'vol_ratio': vol_evento / vol_normal if vol_normal > 0 else 1.0,
        'p_vol': p_vol,
        'ret_1d_series': ret_1d * 100,
        'ret_21d_series': ret_21d * 100,
        'normal_1d_series': normal_1d * 100,
        'normal_21d_series': normal_21d * 100,
        'first_year': first_year,
    }


def get_event_history(variable, n=15):
    """Devuelve las últimas n publicaciones de una variable macro con la reacción del IBEX."""
    ibex, _, _ = detect_macro_events()

    ecol = f'evento_{variable}'
    vcol = f'val_{variable}'
    if ecol not in ibex.columns:
        return pd.DataFrame()

    # Forward returns
    cum = ibex['log_ret'].cumsum()
    fwd_5d = cum.shift(-5) - cum
    fwd_21d = cum.shift(-21) - cum

    events = ibex[ibex[ecol] == 1].copy()
    events = events.tail(n)
    if len(events) == 0:
        return pd.DataFrame()

    val_diff = ibex[vcol].diff()

    result = pd.DataFrame({
        'Fecha': events.index.strftime('%d/%m/%Y'),
        'Valor': events[vcol].values,
        'Cambio': val_diff.reindex(events.index).values,
        'Dirección': np.where(
            val_diff.reindex(events.index) > 0, '↑ Sube',
            np.where(val_diff.reindex(events.index) < 0, '↓ Baja', '—')),
        'Ret. día (%)': (events['log_ret'] * 100).values,
        'Ret. 5d (%)': (fwd_5d.reindex(events.index) * 100).values,
        'Ret. 21d (%)': (fwd_21d.reindex(events.index) * 100).values,
    })

    return result.iloc[::-1].reset_index(drop=True)


def get_upcoming_events():
    """Estima las próximas publicaciones macro a partir del patrón histórico.

    Para cada variable macro:
    - Extrae las fechas históricas de publicación (evento_{col} == 1)
    - Calcula la frecuencia mediana entre publicaciones
    - Estima la próxima fecha como última_publicación + frecuencia_mediana
    - Obtiene el último valor y la dirección del cambio
    - Asigna tier e importancia desde MACRO_RECOMMENDATIONS
    """
    ibex, MACRO_EVENT_COLS, HIGH_IMPACT_COLS = detect_macro_events()

    upcoming = []
    for col in MACRO_EVENT_COLS:
        ecol = f'evento_{col}'
        vcol = f'val_{col}'
        if ecol not in ibex.columns:
            continue

        # Fechas de eventos históricos
        event_dates = ibex.index[ibex[ecol] == 1]
        if len(event_dates) < 2:
            continue

        # Frecuencia mediana entre publicaciones (en días)
        deltas = pd.Series(event_dates).diff().dropna().dt.days
        freq_median = int(deltas.median())

        # Última publicación y estimación de la próxima
        last_date = event_dates[-1]
        next_date = last_date + pd.Timedelta(days=freq_median)

        # Último valor y dirección (comparar valores en las 2 últimas fechas de evento)
        last_val = ibex.loc[last_date, vcol] if vcol in ibex.columns else None
        if vcol in ibex.columns and len(event_dates) >= 2:
            curr_val = ibex.loc[event_dates[-1], vcol]
            prev_val = ibex.loc[event_dates[-2], vcol]
            if pd.notna(curr_val) and pd.notna(prev_val) and curr_val > prev_val:
                direction = 'sube'
                trend_icon = '↑'
            elif pd.notna(curr_val) and pd.notna(prev_val) and curr_val < prev_val:
                direction = 'baja'
                trend_icon = '↓'
            else:
                direction = 'sin_cambio'
                trend_icon = '—'
        else:
            direction = 'sin_cambio'
            trend_icon = '—'

        # Tier y recomendación
        rec_table = MACRO_RECOMMENDATIONS.get(col, {})
        if direction in rec_table:
            rec = rec_table[direction]
        else:
            rec = {'accion': 'MANTENER', 'tier': 3, 'desc': 'Sin señal accionable'}

        label = MACRO_EVENT_LABELS.get(col, col)

        upcoming.append({
            'variable': col,
            'label': label,
            'last_date': last_date,
            'next_date': next_date,
            'freq_days': freq_median,
            'last_val': last_val,
            'trend_icon': trend_icon,
            'direction': direction,
            'tier': rec['tier'],
            'accion': rec['accion'],
            'desc': rec['desc'],
            'high_impact': col in HIGH_IMPACT_COLS,
        })

    # Ordenar por fecha próxima
    upcoming.sort(key=lambda x: x['next_date'])
    return upcoming


# ── Rigor estadístico y validación ──────────────────────────────────────────

TRANSACTION_COST_BPS = 20  # 20 puntos básicos (0.20%) por operación


def get_net_returns(bt, w_col, cost_bps=TRANSACTION_COST_BPS):
    """Retornos log netos de costes de transacción para una estrategia.

    El coste se aplica proporcionalmente al cambio absoluto de peso cada día.
    Ejemplo: pasar de w=1.0 a w=0.5 incurre en |0.5| × 20 bps = 10 bps.
    """
    gross_log_ret = bt[f'ret_{w_col}']
    weight_change = bt[w_col].diff().abs().fillna(0)
    cost = weight_change * cost_bps / 10000
    return gross_log_ret - cost


def get_all_metrics_net(bt, cost_bps=TRANSACTION_COST_BPS):
    """Métricas de todas las estrategias netas de costes de transacción."""
    metrics = []
    for name, w_col in STRATEGY_NAMES.items():
        net_log_ret = get_net_returns(bt, w_col, cost_bps)
        simple_ret = np.exp(net_log_ret) - 1
        m = calc_metrics(simple_ret, name)
        # Costes totales acumulados
        weight_changes = bt[w_col].diff().abs().fillna(0)
        total_cost_pct = (weight_changes * cost_bps / 10000).sum() * 100
        n_trades = int((weight_changes > 0).sum())
        m['Costes totales (%)'] = total_cost_pct
        m['N.º rebalanceos'] = n_trades
        m['% días 100% inv.'] = (bt[w_col] == 1.0).mean() * 100
        metrics.append(m)
    return pd.DataFrame(metrics).set_index('Estrategia')


def bootstrap_sharpe_ci(returns, n_boot=5000, ci=0.95):
    """Intervalo de confianza bootstrap para el Sharpe ratio.

    Remuestrea con reemplazo n_boot veces y devuelve (lo, hi, media).
    """
    rng = np.random.RandomState(SEED)
    n = len(returns)
    sharpes = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.randint(0, n, size=n)
        sample = returns.iloc[idx]
        mu = sample.mean() * 252
        sigma = sample.std() * np.sqrt(252)
        sharpes[i] = mu / sigma if sigma > 0 else 0
    alpha = (1 - ci) / 2
    lo = float(np.percentile(sharpes, alpha * 100))
    hi = float(np.percentile(sharpes, (1 - alpha) * 100))
    return lo, hi, float(np.mean(sharpes))


def get_bonferroni_results():
    """Calcula p-values con corrección de Bonferroni para todas las variables macro.

    Aplica la corrección multiplicando cada p-valor bruto por el número total
    de tests realizados (7 variables × 2 direcciones = hasta 14 tests).
    """
    raw_results = []
    for var_label, variable in ASESOR_VARIABLES.items():
        for direction in ['sube', 'baja']:
            analysis = analyze_macro_event(variable, direction)
            if analysis is not None:
                raw_results.append({
                    'variable': variable,
                    'label': var_label,
                    'direction': direction,
                    'p_raw': analysis['p_vol'],
                    'n_events': analysis['n_events'],
                    'vol_ratio': analysis['vol_ratio'],
                    'tier': analysis['recommendation']['tier'],
                    'accion': analysis['recommendation']['accion'],
                })

    n_tests = len(raw_results)
    for r in raw_results:
        r['p_bonferroni'] = min(r['p_raw'] * n_tests, 1.0)
        r['sig_raw'] = r['p_raw'] < 0.05
        r['sig_corrected'] = r['p_bonferroni'] < 0.05
        r['n_tests'] = n_tests

    return raw_results


def walk_forward_validate(n_splits=5):
    """Validación walk-forward con ventana expansiva.

    Divide el dataset en n_splits folds secuenciales, entrenando con
    datos crecientes y testeando en el fold siguiente. Devuelve RMSE
    y R² por fold.
    """
    ibex, _, _ = detect_macro_events()
    macro_model, MACRO_MODEL_COLS = get_macro_model_features()

    ibex = ibex.copy()
    ibex['vol_lag1'] = ibex['vol_21d'].shift(1)
    ibex['vol_lag5'] = ibex['vol_21d'].rolling(5).mean().shift(1)
    ibex['vol_lag21'] = ibex['vol_21d'].rolling(21).mean().shift(1)

    HAR_FEATS = ['vol_lag1', 'vol_lag5', 'vol_lag21']
    ALL_FEATS = HAR_FEATS + MACRO_MODEL_COLS
    TARGET = 'vol_21d'

    df_model = ibex.join(macro_model).dropna(
        subset=[TARGET] + ALL_FEATS
    ).sort_index()

    n = len(df_model)
    min_train = int(n * 0.4)
    fold_size = (n - min_train) // n_splits

    results = []
    for i in range(n_splits):
        train_end = min_train + i * fold_size
        test_start = train_end
        test_end = min(train_end + fold_size, n)

        if test_start >= n or test_end <= test_start:
            break

        df_train = df_model.iloc[:train_end]
        df_test_fold = df_model.iloc[test_start:test_end]

        if len(df_test_fold) < 10:
            break

        X_tr = df_train[ALL_FEATS].values
        y_tr = df_train[TARGET].values
        X_te = df_test_fold[ALL_FEATS].values
        y_te = df_test_fold[TARGET].values

        model = XGBRegressor(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8,
            random_state=SEED, n_jobs=-1,
        )
        model.fit(X_tr, y_tr)
        y_pred = model.predict(X_te)

        rmse = float(np.sqrt(mean_squared_error(y_te, y_pred)))
        ss_res = float(np.sum((y_te - y_pred) ** 2))
        ss_tot = float(np.sum((y_te - y_te.mean()) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        results.append({
            'fold': i + 1,
            'train_period': (f"{df_train.index[0].strftime('%Y-%m')} → "
                             f"{df_train.index[-1].strftime('%Y-%m')}"),
            'test_period': (f"{df_test_fold.index[0].strftime('%Y-%m')} → "
                            f"{df_test_fold.index[-1].strftime('%Y-%m')}"),
            'n_train': len(df_train),
            'n_test': len(df_test_fold),
            'rmse': rmse,
            'r2': r2,
        })

    return results


def get_stress_test_results(bt):
    """Analiza el rendimiento de las estrategias en períodos de crisis históricos.

    Calcula retorno acumulado y max drawdown por estrategia en cada ventana.
    Solo incluye períodos que caen dentro del rango de datos del backtest.
    """
    crisis_periods = [
        ('Crisis Financiera Global', '2008-01-01', '2009-06-30'),
        ('Crisis Deuda Soberana', '2010-04-01', '2012-07-31'),
        ('Desaceleración China', '2015-06-01', '2016-02-29'),
        ('Vol. Q4 2018', '2018-10-01', '2018-12-31'),
        ('COVID-19', '2020-02-01', '2020-06-30'),
        ('Subida de Tipos 2022', '2022-01-01', '2022-12-31'),
    ]

    results = []
    for label, start, end in crisis_periods:
        mask = (bt.index >= start) & (bt.index <= end)
        period = bt.loc[mask]

        if len(period) < 10:
            continue

        row = {'Período': label, 'Días': len(period)}
        for name, w_col in STRATEGY_NAMES.items():
            simple_ret = np.exp(period[f'ret_{w_col}']) - 1
            cum_ret = float((1 + simple_ret).prod() - 1)
            equity = (1 + simple_ret).cumprod()
            mdd = float((equity / equity.cummax() - 1).min())
            short_name = name.split(':')[-1].strip() if ':' in name else name
            row[f'Ret {short_name} (%)'] = cum_ret * 100
            row[f'MDD {short_name} (%)'] = mdd * 100
        results.append(row)

    return results


# ── Plan de Acción Táctico ──────────────────────────────────────────────────


def compute_composite_risk_score(signal, upcoming_events, window_days=30):
    """Calcula un score de riesgo compuesto (0-100) fusionando volatilidad y eventos.

    Componente volatilidad (0-50): vol_pctile / 2
    Componente eventos (0-50): Tier-1 = 15 pts, Tier-2 = 8 pts, Tier-3 = 2 pts (cap 50)
    """
    vol_component = signal['vol_pctile'] / 2  # 0-50

    today = signal['fecha']
    cutoff = today + pd.Timedelta(days=window_days)
    tier_pts = {1: 15, 2: 8, 3: 2}
    event_component = 0
    tier_counts = {1: 0, 2: 0, 3: 0}
    for evt in upcoming_events:
        if evt['next_date'] <= cutoff:
            event_component += tier_pts.get(evt['tier'], 2)
            tier_counts[evt['tier']] = tier_counts.get(evt['tier'], 0) + 1
    event_component = min(event_component, 50)  # cap 50

    score = vol_component + event_component

    if score < 35:
        risk_level = 'Bajo'
    elif score <= 65:
        risk_level = 'Medio'
    else:
        risk_level = 'Alto'

    # Resumen ejecutivo
    sem_label = 'normal' if signal['semaforo'] == 'verde' else (
        'elevada' if signal['semaforo'] == 'amarillo' else 'alta')
    n_events = sum(tier_counts.values())
    n_hi = tier_counts.get(1, 0)
    hi_text = f" ({n_hi} de alto impacto)" if n_hi > 0 else ""
    summary = (f"Régimen de vol. {sem_label} + {n_events} eventos macro "
               f"en {window_days}d{hi_text}")

    return {
        'score': round(score, 1),
        'vol_component': round(vol_component, 1),
        'event_component': round(event_component, 1),
        'risk_level': risk_level,
        'summary': summary,
        'tier_counts': tier_counts,
    }


def generate_action_calendar(signal, upcoming_events, portfolio_eur,
                             profile, lookahead_days):
    """Genera un calendario de acción día a día para el horizonte indicado.

    Para cada día calcula la exposición recomendada fusionando señal de vol +
    eventos macro + perfil de inversor.
    """
    today = signal['fecha']
    base_exposure = 100
    vol_pctile = signal['vol_pctile']

    # Exposición base por volatilidad
    if vol_pctile >= 75:
        vol_exposure = 50
        vol_signal = 'ALTA'
    elif vol_pctile >= 50:
        vol_exposure = 80
        vol_signal = 'MEDIA'
    else:
        vol_exposure = 100
        vol_signal = 'NORMAL'

    # Construir mapeo fecha → eventos
    event_map = {}
    for evt in upcoming_events:
        d = evt['next_date']
        if d not in event_map:
            event_map[d] = []
        event_map[d].append(evt)

    # Ventana de influencia de eventos por perfil
    if profile == 'Conservador':
        event_window = 1  # ±1 día extra
    else:
        event_window = 0

    # Expandir event_map con ventanas
    expanded_event_map = {}
    for d, evts in event_map.items():
        for offset in range(-event_window, event_window + 1):
            shifted = d + pd.Timedelta(days=offset)
            if shifted not in expanded_event_map:
                expanded_event_map[shifted] = []
            for evt in evts:
                # Evitar duplicados
                if evt not in expanded_event_map[shifted]:
                    expanded_event_map[shifted].append(evt)

    rows = []
    bdays = pd.bdate_range(start=today, periods=lookahead_days + 1)

    for d in bdays:
        day_events = expanded_event_map.get(d, [])

        # Filtrar Tier-3 para perfil Agresivo
        if profile == 'Agresivo':
            day_events = [e for e in day_events if e['tier'] <= 2]

        # Calcular exposición por eventos del día
        event_exposure = 100
        event_names = []
        reasoning_parts = []

        for evt in day_events:
            pct = EXPOSURE_PCT.get((evt['accion'], evt['tier']), 100)
            event_exposure = min(event_exposure, pct)
            event_names.append(evt['label'])
            reasoning_parts.append(
                f"{evt['label']}: {evt['accion']} T{evt['tier']} → {pct}%")

        # Fusionar vol + evento
        exposure = min(vol_exposure, event_exposure)

        # Cadena de razonamiento
        reasoning = []
        if vol_exposure < 100:
            reasoning.append(f"Vol P{vol_pctile:.0f} ({vol_signal}) → {vol_exposure}%")
        reasoning.extend(reasoning_parts)
        if not reasoning:
            reasoning.append("Sin señales activas")

        # Acción
        if exposure >= 100:
            action = 'MANTENER'
        elif exposure >= 80:
            action = 'CAUTELA'
        else:
            action = 'REDUCIR'

        delta_eur = portfolio_eur * (exposure / 100) - portfolio_eur

        rows.append({
            'date': d,
            'events': ', '.join(event_names) if event_names else '—',
            'vol_signal': vol_signal,
            'score': round(100 - exposure, 0),
            'exposure_pct': exposure,
            'action': action,
            'delta_eur': delta_eur,
            'reasoning': ' | '.join(reasoning),
        })

    return pd.DataFrame(rows)


def detect_event_clusters(upcoming_events, cluster_window=5):
    """Detecta agrupaciones de 2+ eventos en ventanas de N días hábiles.

    Calcula exposición combinada multiplicativa:
    e.g. 80% × 50% / 100 = 40%
    """
    if len(upcoming_events) < 2:
        return []

    sorted_events = sorted(upcoming_events, key=lambda e: e['next_date'])
    clusters = []
    used = set()

    for i, evt_a in enumerate(sorted_events):
        if i in used:
            continue
        cluster_events = [evt_a]
        cluster_indices = {i}

        for j, evt_b in enumerate(sorted_events):
            if j <= i or j in used:
                continue
            delta = (evt_b['next_date'] - evt_a['next_date']).days
            if 0 <= delta <= cluster_window:
                cluster_events.append(evt_b)
                cluster_indices.add(j)

        if len(cluster_events) >= 2:
            # Exposición multiplicativa
            combined = 100
            for evt in cluster_events:
                pct = EXPOSURE_PCT.get((evt['accion'], evt['tier']), 100)
                combined = combined * pct / 100
            combined = max(round(combined, 1), 10)  # floor 10%

            clusters.append({
                'start_date': min(e['next_date'] for e in cluster_events),
                'end_date': max(e['next_date'] for e in cluster_events),
                'events': cluster_events,
                'combined_exposure_pct': combined,
                'n_events': len(cluster_events),
            })
            used.update(cluster_indices)

    return clusters


def build_scenario_table(next_event, portfolio_eur):
    """Construye tabla de escenarios (sube/baja/no_action) para un evento.

    Usa analyze_macro_event + calc_exposure existentes.
    """
    variable = next_event['variable']

    # Escenario SUBE
    analysis_up = analyze_macro_event(variable, 'sube')
    exposure_up = calc_exposure(variable, 'sube', portfolio_eur)

    # Escenario BAJA
    analysis_down = analyze_macro_event(variable, 'baja')
    exposure_down = calc_exposure(variable, 'baja', portfolio_eur)

    # Escenario NO ACTION (Buy & Hold → 100%)
    analysis_all = analyze_macro_event(variable, None)

    result = {}

    if analysis_up:
        result['sube'] = {
            'exposure_pct': exposure_up['exposure_pct'],
            'delta_eur': exposure_up['delta_eur'],
            'ret_21d_mean': analysis_up['ret_21d_mean'],
            'ret_1d_mean': analysis_up['ret_1d_mean'],
            'n_events': analysis_up['n_events'],
            'accion': exposure_up['accion'],
            'desc': exposure_up['desc'],
        }
    else:
        result['sube'] = None

    if analysis_down:
        result['baja'] = {
            'exposure_pct': exposure_down['exposure_pct'],
            'delta_eur': exposure_down['delta_eur'],
            'ret_21d_mean': analysis_down['ret_21d_mean'],
            'ret_1d_mean': analysis_down['ret_1d_mean'],
            'n_events': analysis_down['n_events'],
            'accion': exposure_down['accion'],
            'desc': exposure_down['desc'],
        }
    else:
        result['baja'] = None

    if analysis_all:
        # VaR histórico en días de este evento (Buy & Hold)
        ibex, _, _ = detect_macro_events()
        ecol = f'evento_{variable}'
        if ecol in ibex.columns:
            event_rets = ibex.loc[ibex[ecol] == 1, 'log_ret'].dropna()
            var_95 = float(event_rets.quantile(0.05)) * 100 if len(event_rets) > 5 else 0
        else:
            var_95 = 0

        result['no_action'] = {
            'exposure_pct': 100,
            'delta_eur': 0,
            'ret_21d_mean': analysis_all['ret_21d_mean'],
            'ret_1d_mean': analysis_all['ret_1d_mean'],
            'n_events': analysis_all['n_events'],
            'var_95': var_95,
        }
    else:
        result['no_action'] = None

    return result


@st.cache_data(ttl=3600)
def compare_har_vs_full():
    """Compara modelo HAR-only vs HAR+Macro y aplica test de Diebold-Mariano."""
    ibex, _, _ = detect_macro_events()
    macro_model, MACRO_MODEL_COLS = get_macro_model_features()

    ibex = ibex.copy()
    ibex['vol_lag1'] = ibex['vol_21d'].shift(1)
    ibex['vol_lag5'] = ibex['vol_21d'].rolling(5).mean().shift(1)
    ibex['vol_lag21'] = ibex['vol_21d'].rolling(21).mean().shift(1)

    HAR_FEATS = ['vol_lag1', 'vol_lag5', 'vol_lag21']
    ALL_FEATS = HAR_FEATS + MACRO_MODEL_COLS
    TARGET = 'vol_21d'

    df_model = ibex.join(macro_model).dropna(
        subset=[TARGET] + ALL_FEATS
    ).sort_index()

    n = len(df_model)
    cut = int(n * 0.80)
    df_train = df_model.iloc[:cut]
    df_test = df_model.iloc[cut:]

    y_test = df_test[TARGET].values

    # Modelo A: HAR-only
    xgb_har = XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        random_state=SEED, n_jobs=-1,
    )
    xgb_har.fit(df_train[HAR_FEATS].values, df_train[TARGET].values)
    pred_har = xgb_har.predict(df_test[HAR_FEATS].values)

    # Modelo B: HAR+Macro (full)
    xgb_full = XGBRegressor(
        n_estimators=300, max_depth=4, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8,
        random_state=SEED, n_jobs=-1,
    )
    xgb_full.fit(df_train[ALL_FEATS].values, df_train[TARGET].values)
    pred_full = xgb_full.predict(df_test[ALL_FEATS].values)

    # Métricas
    har_metrics = {
        'rmse': float(np.sqrt(mean_squared_error(y_test, pred_har))),
        'mae': float(mean_absolute_error(y_test, pred_har)),
        'r2': float(r2_score(y_test, pred_har)),
    }
    full_metrics = {
        'rmse': float(np.sqrt(mean_squared_error(y_test, pred_full))),
        'mae': float(mean_absolute_error(y_test, pred_full)),
        'r2': float(r2_score(y_test, pred_full)),
    }

    # Test de Diebold-Mariano (bilateral)
    e_har = y_test - pred_har
    e_full = y_test - pred_full
    d_t = e_har ** 2 - e_full ** 2
    n_obs = len(d_t)
    dm_stat = float(d_t.mean() / (d_t.std(ddof=1) / np.sqrt(n_obs)))
    dm_pvalue = float(norm.sf(abs(dm_stat)) * 2)

    return {
        'har_metrics': har_metrics,
        'full_metrics': full_metrics,
        'dm_statistic': dm_stat,
        'dm_pvalue': dm_pvalue,
        'har_residuals': e_har,
        'full_residuals': e_full,
        'n_har_feats': len(HAR_FEATS),
        'n_full_feats': len(ALL_FEATS),
    }


@st.cache_data(ttl=3600)
def compute_efficient_frontier(n_points=50):
    """Calcula la frontera eficiente de Markowitz sobre las 4 estrategias."""
    bt = run_backtest()

    # Retornos simples diarios de cada estrategia
    strat_rets = pd.DataFrame()
    strat_names = []
    for name, w_col in STRATEGY_NAMES.items():
        strat_rets[name] = np.exp(bt[f'ret_{w_col}']) - 1
        strat_names.append(name)

    n_assets = len(strat_names)
    mu = strat_rets.mean().values * 252
    cov = strat_rets.cov().values * 252

    # Puntos individuales de cada estrategia
    strategies = []
    for i, name in enumerate(strat_names):
        ret_ann = mu[i]
        vol_ann = float(np.sqrt(cov[i, i]))
        sharpe = ret_ann / vol_ann if vol_ann > 0 else 0
        strategies.append({
            'name': name,
            'ret': ret_ann * 100,
            'vol': vol_ann * 100,
            'sharpe': sharpe,
        })

    # Funciones auxiliares
    def port_vol(w):
        return float(np.sqrt(w @ cov @ w))

    def port_ret(w):
        return float(w @ mu)

    bounds = tuple((0, 1) for _ in range(n_assets))
    eq_constraint = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}

    # Cartera de mínima varianza
    w0 = np.ones(n_assets) / n_assets
    res_min = minimize(port_vol, w0, method='SLSQP',
                       bounds=bounds, constraints=[eq_constraint])
    min_var = {
        'ret': port_ret(res_min.x) * 100,
        'vol': port_vol(res_min.x) * 100,
        'weights': {strat_names[i]: float(res_min.x[i]) * 100
                    for i in range(n_assets)},
    }

    # Cartera de máximo Sharpe
    def neg_sharpe(w):
        r = w @ mu
        v = np.sqrt(w @ cov @ w)
        return -r / v if v > 0 else 0

    res_sharpe = minimize(neg_sharpe, w0, method='SLSQP',
                          bounds=bounds, constraints=[eq_constraint])
    max_sharpe = {
        'ret': port_ret(res_sharpe.x) * 100,
        'vol': port_vol(res_sharpe.x) * 100,
        'weights': {strat_names[i]: float(res_sharpe.x[i]) * 100
                    for i in range(n_assets)},
        'sharpe': -float(neg_sharpe(res_sharpe.x)),
    }

    # Frontera eficiente
    ret_min = port_ret(res_min.x)
    ret_max = max(mu) * 1.05
    target_rets = np.linspace(ret_min, ret_max, n_points)

    frontier_vols = []
    frontier_rets = []
    for target in target_rets:
        ret_constraint = {'type': 'eq', 'fun': lambda w, t=target: w @ mu - t}
        res = minimize(port_vol, w0, method='SLSQP',
                       bounds=bounds,
                       constraints=[eq_constraint, ret_constraint])
        if res.success:
            frontier_vols.append(port_vol(res.x) * 100)
            frontier_rets.append(target * 100)

    return {
        'frontier_vols': frontier_vols,
        'frontier_rets': frontier_rets,
        'strategies': strategies,
        'min_var': min_var,
        'max_sharpe': max_sharpe,
    }


@st.cache_data(ttl=3600)
def get_landing_kpis():
    """Calcula dinámicamente los KPIs de la landing page."""
    ibex, _, _ = detect_macro_events()

    # 1) Vol. anormal en días de evento (ratio Mann-Whitney)
    evt = ibex[ibex['es_evento'] == 1]['log_ret'].abs().dropna()
    no_evt = ibex[ibex['es_evento'] == 0]['log_ret'].abs().dropna()
    vol_ratio = (evt.mean() / no_evt.mean() - 1) * 100 if no_evt.mean() > 0 else 0

    # 2) RMSE del modelo XGBoost
    df_test, _, _, _, _ = train_xgboost_model()
    rmse = np.sqrt(mean_squared_error(df_test['vol_21d'], df_test['vol_pred']))

    # 3) Estrategia con mejor Sharpe
    bt = run_backtest()
    metrics = get_all_metrics(bt)
    best_strat = metrics['Sharpe'].idxmax()

    return {
        'vol_ratio': vol_ratio,
        'rmse': rmse,
        'best_strategy': best_strat,
        'cost': 0,
    }
