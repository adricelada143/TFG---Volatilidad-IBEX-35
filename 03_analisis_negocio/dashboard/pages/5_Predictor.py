"""Página 5: Predictor — Semáforo de riesgo y señal combinada."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from utils.strategies import (
    run_backtest, train_xgboost_model, get_current_signal,
    get_upcoming_events, walk_forward_validate, compare_har_vs_full,
    ACCION_COLORS, EXPOSURE_PCT, MACRO_EVENT_LABELS,
    style_plotly_chart, load_css,
)

load_css()
st.header("Predictor de Volatilidad")
st.caption("Señal combinada de volatilidad XGBoost + calendario macro")

bt = run_backtest()
df_test, xgb_model, feat_imp, feat_names, train_end = train_xgboost_model()
signal = get_current_signal(bt)

# ── Señal combinada (lógica) ──────────────────────────────────────────────────
es_evento = signal['es_evento']
es_evento_hi = signal['es_evento_hi']
alta_vol = signal['alta_vol']

if alta_vol and es_evento:
    combined = 'rojo'
    combined_text = 'SEÑAL REFORZADA: Alta volatilidad + evento macro'
elif alta_vol or es_evento_hi:
    combined = 'rojo' if signal['semaforo'] == 'rojo' else 'amarillo'
    combined_text = ('Alta volatilidad activa' if alta_vol
                     else 'Evento de alto impacto detectado')
else:
    combined = signal['semaforo']
    combined_text = ''

# ── Semáforo de riesgo (inline styles) ────────────────────────────────────────
semaforo_config = {
    'verde':    {'color': '#059669', 'bg': '#D1FAE5', 'label': 'RIESGO BAJO', 'icon': '🟢', 'glow': 'rgba(5,150,105,0.2)'},
    'amarillo': {'color': '#D97706', 'bg': '#FEF3C7', 'label': 'RIESGO MEDIO', 'icon': '🟡', 'glow': 'rgba(217,119,6,0.2)'},
    'rojo':     {'color': '#DC2626', 'bg': '#FEE2E2', 'label': 'RIESGO ALTO', 'icon': '🔴', 'glow': 'rgba(220,38,38,0.2)'},
}
sem = semaforo_config[combined]

alert_div = (f'<div style="font-size:0.88rem;font-weight:600;color:{sem["color"]};margin-top:8px;">{combined_text}</div>' if combined_text else '')

st.markdown(
    f'<div style="background:linear-gradient(135deg,{sem["bg"]} 0%,#ffffff 100%);border:2px solid {sem["color"]};border-radius:18px;padding:32px 36px;margin:0 0 24px;position:relative;overflow:hidden;box-shadow:0 8px 30px {sem["glow"]};">'
    f'<div style="position:absolute;top:-10px;right:10px;font-size:9rem;opacity:0.06;line-height:1;pointer-events:none;">{sem["icon"]}</div>'
    f'<div style="display:flex;align-items:center;gap:24px;">'
    f'<div style="width:64px;height:64px;border-radius:50%;background:{sem["bg"]};display:flex;align-items:center;justify-content:center;flex-shrink:0;box-shadow:0 4px 12px {sem["glow"]};">'
    f'<div style="width:32px;height:32px;border-radius:50%;background:{sem["color"]};box-shadow:0 0 12px {sem["color"]};"></div></div>'
    f'<div style="flex:1;">'
    f'<div style="font-size:2rem;font-weight:900;color:{sem["color"]};letter-spacing:-0.03em;line-height:1;margin-bottom:6px;">{sem["label"]}</div>'
    f'<div style="font-size:0.95rem;color:#334155;font-weight:500;">{signal["recomendacion"]}</div>'
    f'{alert_div}</div></div>'
    f'<div style="margin-top:20px;padding-top:14px;border-top:1px solid {sem["color"]}20;font-size:0.78rem;color:#64748B;">'
    f'Fecha: <strong>{signal["fecha"].strftime("%d/%m/%Y")}</strong> &nbsp;&middot;&nbsp; '
    f'Percentil: <strong>P{signal["vol_pctile"]:.0f}</strong> &nbsp;&middot;&nbsp; '
    f'Vol. predicha: <strong>{signal["vol_pred"]:.4f}</strong> &nbsp;&middot;&nbsp; '
    f'Vol. real: <strong>{signal["vol_actual"]:.4f}</strong></div></div>',
    unsafe_allow_html=True,
)

# ── KPIs inline HTML ─────────────────────────────────────────────────────────
alta_label = 'ACTIVA' if signal['alta_vol'] else 'INACTIVA'
alta_color = '#DC2626' if signal['alta_vol'] else '#059669'
evt_label = 'SÍ' if es_evento else 'NO'
evt_color = '#DC2626' if es_evento else '#059669'
hi_label = 'SÍ' if es_evento_hi else 'NO'
hi_color = '#DC2626' if es_evento_hi else '#059669'
pct_val = signal['vol_pctile']
pct_color = '#DC2626' if pct_val >= 75 else ('#D97706' if pct_val >= 50 else '#059669')

kpi_cards = [
    ('Señal alta vol.', alta_label, alta_color,
     'Reducir a 50 %' if signal['alta_vol'] else 'Mantener 100 %'),
    ('Evento macro hoy', evt_label, evt_color,
     'Día de publicación' if es_evento else 'Sin publicación'),
    ('Evento alto impacto', hi_label, hi_color,
     'PIB o Paro' if es_evento_hi else 'N/A'),
    ('Percentil histórico', f'P{pct_val:.0f}', pct_color,
     'en distribución de test'),
]

kpi_html = ''
for label, value, color, sub in kpi_cards:
    kpi_html += (
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:20px;'
        f'box-shadow:0 1px 3px rgba(0,0,0,0.06);text-align:center;">'
        f'<div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#64748B;margin-bottom:8px;">{label}</div>'
        f'<div style="font-size:1.45rem;font-weight:800;color:{color};letter-spacing:-0.03em;line-height:1;">{value}</div>'
        f'<div style="font-size:0.72rem;color:#94A3B8;margin-top:4px;">{sub}</div></div>'
    )

st.markdown(
    f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;">{kpi_html}</div>',
    unsafe_allow_html=True,
)

# ── Señal Combinada: tabla visual (inline styles) ────────────────────────────
st.markdown('<div style="display:flex;align-items:center;gap:10px;margin:28px 0 16px;padding-bottom:10px;">'
            '<h3 style="margin:0;font-size:1.1rem;color:#0D1B2A;">Señal Combinada: Volatilidad + Macro</h3></div>',
            unsafe_allow_html=True)

vol_text = ('Reducir' if signal['alta_vol'] else ('Vigilar' if signal['vol_pctile'] >= 50 else 'OK'))
vol_dot_color = ('#DC2626' if signal['alta_vol'] else ('#D97706' if signal['vol_pctile'] >= 50 else '#059669'))
macro_text = ('Alto impacto' if es_evento_hi else ('Evento macro' if es_evento else 'OK'))
macro_dot_color = ('#DC2626' if es_evento_hi else ('#D97706' if es_evento else '#059669'))
comb_dot_color = ('#DC2626' if combined == 'rojo' else ('#D97706' if combined == 'amarillo' else '#059669'))

def _signal_row(source, status, sig_text, dot_color, is_last=False):
    bg = '#F1F5F9' if is_last else '#fff'
    weight = '700' if is_last else '400'
    txt_color = '#0D1B2A' if is_last else '#334155'
    border = '' if is_last else 'border-bottom:1px solid #E2E8F0;'
    dot = (f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
           f'background:{dot_color};box-shadow:0 0 6px {dot_color}80;margin-right:8px;vertical-align:middle;"></span>')
    return (f'<tr><td style="padding:14px 20px;{border}color:{txt_color};font-weight:{weight};">{source}</td>'
            f'<td style="padding:14px 20px;{border}color:{txt_color};">{status}</td>'
            f'<td style="padding:14px 20px;{border}color:{txt_color};font-weight:{weight};">{dot}{sig_text}</td></tr>')

table_html = (
    '<table style="width:100%;border-collapse:separate;border-spacing:0;border-radius:12px;overflow:hidden;border:1px solid #E2E8F0;box-shadow:0 1px 3px rgba(0,0,0,0.06);font-size:0.88rem;">'
    '<thead><tr>'
    '<th style="background:#0D1B2A;color:#fff;padding:14px 20px;text-align:left;font-weight:600;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">Fuente</th>'
    '<th style="background:#0D1B2A;color:#fff;padding:14px 20px;text-align:left;font-weight:600;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">Estado</th>'
    '<th style="background:#0D1B2A;color:#fff;padding:14px 20px;text-align:left;font-weight:600;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;">Señal</th>'
    '</tr></thead><tbody>'
    + _signal_row('XGBoost Volatilidad', f'P{signal["vol_pctile"]:.0f} — {"ALTA" if signal["alta_vol"] else "NORMAL"}', vol_text, vol_dot_color)
    + _signal_row('Calendario Macro', 'Evento detectado' if es_evento else 'Sin evento', macro_text, macro_dot_color)
    + _signal_row('SEÑAL COMBINADA', combined_text if combined_text else 'Normal', sem['label'], comb_dot_color, is_last=True)
    + '</tbody></table>'
)

st.markdown(table_html, unsafe_allow_html=True)

# ── Próximos Eventos Macro ───────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Próximos Eventos Macro (Estimación)</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
            'Fechas estimadas a partir de la frecuencia histórica de publicación. '
            'La recomendación se basa en la dirección del último cambio observado.</p>',
            unsafe_allow_html=True)

cartera_pred = st.number_input(
    "Cartera IBEX 35 (€)",
    value=1_000_000,
    step=100_000,
    min_value=10_000,
    key="cartera_predictor",
)

upcoming = get_upcoming_events()

if upcoming:
    var_icons = {
        'ipc_yoy': '📊', 'pib_yoy': '📈', 'tasa_paro': '👥',
        'ipi_yoy': '🏭', 'euribor_3m': '🏦', 'tipo_dfr': '🇪🇺',
        'ipc_sub_mom': '📉',
    }

    # Calcular exposición para cada evento
    for evt in upcoming:
        pct = EXPOSURE_PCT.get((evt['accion'], evt['tier']), 100)
        evt['exposure_pct'] = pct
        evt['target_eur'] = cartera_pred * pct / 100
        evt['delta_eur'] = evt['target_eur'] - cartera_pred

    # ── Tarjeta resumen consolidada ──────────────────────────────────────────
    min_exp = min(evt['exposure_pct'] for evt in upcoming)
    # Próximo evento clave: el T1/T2 más cercano
    key_events = [e for e in upcoming if e['tier'] <= 2]
    if key_events:
        next_key = key_events[0]
        next_key_text = f"{next_key['label']} — {next_key['next_date'].strftime('%d/%m/%Y')}"
    else:
        next_key_text = "Ninguno (solo T3)"

    if min_exp < 70:
        summary_border = '#DC2626'
        summary_bg = '#FEE2E2'
        summary_text = '#991B1B'
    elif min_exp < 90:
        summary_border = '#D97706'
        summary_bg = '#FEF3C7'
        summary_text = '#92400E'
    else:
        summary_border = '#059669'
        summary_bg = '#D1FAE5'
        summary_text = '#065F46'

    min_target = cartera_pred * min_exp / 100
    min_delta = min_target - cartera_pred

    if min_delta < 0:
        delta_summary_label = f"Vender {abs(min_delta):,.0f} €"
    elif min_delta > 0:
        delta_summary_label = f"Comprar {min_delta:,.0f} €"
    else:
        delta_summary_label = "Sin ajuste"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {summary_bg} 0%, #ffffff 100%);
        border: 2px solid {summary_border};
        border-radius: 16px;
        padding: 28px 32px;
        margin: 20px 0;
        box-shadow: 0 4px 16px {summary_border}20;
    ">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 20px;">
            <div>
                <div style="font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.12em; color: {summary_border}; margin-bottom: 6px;">
                    Exposición mínima recomendada
                </div>
                <div style="font-size: 2.8rem; font-weight: 900; color: {summary_text}; line-height: 1;">
                    {min_exp}%
                </div>
                <div style="font-size: 0.85rem; color: {summary_text}; opacity: 0.8; margin-top: 4px;">
                    {delta_summary_label}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.12em; color: {summary_border}; margin-bottom: 6px;">
                    Próximo evento clave
                </div>
                <div style="font-size: 1.1rem; font-weight: 700; color: {summary_text};">
                    {next_key_text}
                </div>
                <div style="font-size: 0.75rem; color: {summary_text}; opacity: 0.7; margin-top: 4px;">
                    {len(upcoming)} eventos estimados en total
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tarjetas individuales por evento (grid 2 columnas) ───────────────────
    TIER_CARD_STYLE = {
        1: {'header_bg': '#059669', 'header_text': '#fff', 'label': 'T1 — Alta señal'},
        2: {'header_bg': '#D97706', 'header_text': '#fff', 'label': 'T2 — Señal moderada'},
        3: {'header_bg': '#94A3B8', 'header_text': '#fff', 'label': 'T3 — Ruido'},
    }

    cards_html = []
    for evt in upcoming:
        icon = var_icons.get(evt['variable'], '📋')
        ts = TIER_CARD_STYLE[evt['tier']]
        val_str = f"{evt['last_val']:.2f}" if evt['last_val'] is not None else '—'
        hi_badge = ('<span style="background:#DC2626;color:#fff;padding:2px 8px;border-radius:10px;font-size:0.55rem;font-weight:700;margin-left:8px;vertical-align:middle;">ALTO IMPACTO</span>' if evt['high_impact'] else '')

        pct = evt['exposure_pct']
        delta = evt['delta_eur']
        if pct >= 100:
            pct_color = '#059669'
        elif pct >= 70:
            pct_color = '#D97706'
        else:
            pct_color = '#DC2626'

        if delta < 0:
            delta_color = '#DC2626'
            delta_text = f"Vender {abs(delta):,.0f} €"
        elif delta > 0:
            delta_color = '#059669'
            delta_text = f"Comprar {delta:,.0f} €"
        else:
            delta_color = '#64748B'
            delta_text = "Sin ajuste"

        accion_color = ACCION_COLORS.get(evt['accion'], '#64748B')
        bar_w = min(pct / 150 * 100, 100)

        card = (f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.05);">'
                f'<div style="background:{ts["header_bg"]};color:{ts["header_text"]};padding:10px 16px;font-size:0.65rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;">'
                f'{ts["label"]}</div>'
                f'<div style="padding:20px;">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
                f'<span style="font-size:1.5rem;">{icon}</span>'
                f'<span style="font-size:0.95rem;font-weight:700;color:#1E293B;">{evt["label"]}</span>'
                f'{hi_badge}</div>'
                f'<div style="font-size:0.75rem;color:#64748B;margin-bottom:6px;">'
                f'Fecha estimada: <strong>{evt["next_date"].strftime("%d/%m/%Y")}</strong>'
                f'&nbsp;&middot;&nbsp; Freq: cada {evt["freq_days"]}d</div>'
                f'<div style="font-size:0.75rem;color:#64748B;margin-bottom:14px;">'
                f'Último valor: <strong>{val_str} {evt["trend_icon"]}</strong></div>'
                f'<div style="display:flex;align-items:baseline;gap:12px;margin-bottom:8px;">'
                f'<div style="font-size:2rem;font-weight:900;color:{pct_color};line-height:1;">{pct}%</div>'
                f'<div style="font-size:0.75rem;color:{pct_color};font-weight:600;">exposición</div></div>'
                f'<div style="height:5px;background:#F1F5F9;border-radius:3px;overflow:hidden;margin-bottom:10px;">'
                f'<div style="height:100%;width:{bar_w}%;background:{pct_color};border-radius:3px;"></div></div>'
                f'<div style="font-size:0.88rem;font-weight:700;color:{delta_color};margin-bottom:10px;">{delta_text}</div>'
                f'<div style="font-size:0.72rem;color:#64748B;line-height:1.4;border-top:1px solid #F1F5F9;padding-top:10px;">'
                f'<span style="color:{accion_color};font-weight:700;">{evt["accion"]}</span>'
                f'&nbsp;&mdash;&nbsp; {evt["desc"]}</div></div></div>')
        cards_html.append(card)

    # Render grid 2 columnas
    grid_items = ''.join(cards_html)
    st.markdown(
        f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin:16px 0;">{grid_items}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="method-note">
        <p>
            <strong>Nota:</strong> Las fechas son estimaciones basadas en la frecuencia
            mediana histórica de publicación. <strong>T1</strong> = variable con impacto
            estadísticamente significativo (p < 0.05), <strong>T2</strong> = impacto moderado,
            <strong>T3</strong> = sin señal accionable (ruido estadístico). En producción se
            conectaría a un calendario oficial (INE, BCE, Eurostat).
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No se pudieron estimar próximos eventos con los datos disponibles.")

# ── Evolución volatilidad predicha vs real ────────────────────────────────────
st.markdown('<div class="section-header"><h3>Evolución: Volatilidad Predicha vs. Real</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(
    x=df_test.index, y=df_test['vol_21d'],
    name='Volatilidad real (21d)',
    line=dict(color='#0D1B2A', width=1.5),
))
fig_vol.add_trace(go.Scatter(
    x=df_test.index, y=df_test['vol_pred'],
    name='Volatilidad predicha (XGBoost)',
    line=dict(color='#2563EB', width=1.5, dash='dash'),
))
fig_vol.add_trace(go.Scatter(
    x=df_test.index, y=df_test['vol_p75'],
    name='Umbral P75 (rolling 63d)',
    line=dict(color='#DC2626', width=1, dash='dot'),
    fill='tonexty', fillcolor='rgba(220, 38, 38, 0.05)',
))

alta_vol_mask = df_test['alta_vol'] == 1
fig_vol.add_trace(go.Scatter(
    x=df_test.index[alta_vol_mask],
    y=df_test.loc[alta_vol_mask, 'vol_pred'],
    mode='markers',
    name='Señal ALTA VOL',
    marker=dict(color='#DC2626', size=4, opacity=0.35),
))

fig_vol.update_layout(
    xaxis_title="Fecha", yaxis_title="Volatilidad (21d)",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)
style_plotly_chart(fig_vol, height=420)
st.plotly_chart(fig_vol, use_container_width=True)

# ── Feature Importance ────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Variables del Modelo (XGBoost)</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

top_n = st.slider("Top N variables", 5, len(feat_imp), 8)
top_feat = feat_imp.head(top_n)

readable_labels = {
    'vol_lag1': 'Vol. t-1 (1 día)',
    'vol_lag5': 'Vol. media 5d',
    'vol_lag21': 'Vol. media 21d',
    'vix': 'VIX (CBOE)',
    'bono_es_10y': 'Bono España 10Y',
    'bono_de_10y': 'Bono Alemania 10Y',
    'eur_usd': 'EUR/USD',
    'brent': 'Brent (petróleo)',
    'euribor_3m': 'Euríbor 3M',
    'tipo_dfr': 'Tipo DFR (BCE)',
    'ipc_yoy': 'IPC interanual',
    'ipc_sub_mom': 'IPC subyacente',
    'pib_yoy': 'PIB interanual',
    'tasa_paro': 'Tasa de paro',
    'ipi_yoy': 'IPI interanual',
}

fig_fi = go.Figure()
labels = [readable_labels.get(f, f) for f in top_feat.index[::-1]]
values = top_feat.values[::-1]
colors = ['#D97706' if 'vol_lag' in f else '#059669'
          for f in top_feat.index[::-1]]

fig_fi.add_trace(go.Bar(
    x=values, y=labels,
    orientation='h',
    marker_color=colors,
    text=[f"{v:.3f}" for v in values],
    textposition='outside',
))
fig_fi.update_layout(
    xaxis_title="Importancia (gain)",
    annotations=[dict(
        text="Naranja = HAR (autorregresivas)  |  Verde = Macro / Mercado",
        x=0.99, y=0.01, xref="paper", yref="paper",
        showarrow=False, font=dict(size=10, color="#94A3B8"),
    )],
)
style_plotly_chart(fig_fi, height=max(300, top_n * 38))
st.plotly_chart(fig_fi, use_container_width=True)

# ── Comparación HAR-only vs HAR+Macro ─────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Comparación: Modelo HAR-only vs HAR + Macro</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
    'Evaluación del valor añadido de las variables macroeconómicas y de mercado '
    'al modelo base HAR (3 features autorregresivas). Test de Diebold-Mariano '
    'bilateral sobre los residuos al cuadrado.</p>',
    unsafe_allow_html=True,
)

_cmp = compare_har_vs_full()
_har = _cmp['har_metrics']
_full = _cmp['full_metrics']

_cmp_c1, _cmp_c2 = st.columns(2)

with _cmp_c1:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #FFF7ED, #fff); border:2px solid #D97706;
                border-radius:14px; padding:22px; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:#D97706; margin-bottom:12px;">
            Modelo HAR-only ({_cmp['n_har_feats']} features)</div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px;">
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">RMSE</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_har['rmse']:.4f}</div>
            </div>
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">MAE</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_har['mae']:.4f}</div>
            </div>
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">R&sup2;</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_har['r2']:.4f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with _cmp_c2:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, #ECFDF5, #fff); border:2px solid #059669;
                border-radius:14px; padding:22px; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:#059669; margin-bottom:12px;">
            Modelo HAR + Macro ({_cmp['n_full_feats']} features)</div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:10px;">
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">RMSE</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_full['rmse']:.4f}</div>
            </div>
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">MAE</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_full['mae']:.4f}</div>
            </div>
            <div>
                <div style="font-size:0.6rem; color:#64748B; text-transform:uppercase;">R&sup2;</div>
                <div style="font-size:1.3rem; font-weight:800; color:#0D1B2A;">{_full['r2']:.4f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# DM test result card
_dm_sig = _cmp['dm_pvalue'] < 0.05
_dm_color = '#DC2626' if _dm_sig else '#059669'
_dm_conclusion = ('Diferencia significativa (p < 0.05)' if _dm_sig
                  else 'Sin diferencia significativa (p > 0.05)')

st.markdown(f"""
<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px;
            padding:22px 28px; margin:16px 0; text-align:center;">
    <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                letter-spacing:0.1em; color:#64748B; margin-bottom:10px;">
        Test de Diebold-Mariano (bilateral)</div>
    <div style="display:flex; justify-content:center; gap:40px; align-items:baseline;">
        <div>
            <span style="font-size:0.75rem; color:#64748B;">Estad&iacute;stico:</span>
            <span style="font-size:1.2rem; font-weight:800; color:#0D1B2A; margin-left:6px;">
                {_cmp['dm_statistic']:.3f}</span>
        </div>
        <div>
            <span style="font-size:0.75rem; color:#64748B;">p-valor:</span>
            <span style="font-size:1.2rem; font-weight:800; color:{_dm_color}; margin-left:6px;">
                {_cmp['dm_pvalue']:.4f}</span>
        </div>
        <div>
            <span style="font-size:0.88rem; font-weight:700; color:{_dm_color};">
                {_dm_conclusion}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="method-note">
    <p>
        <strong>Interpretaci&oacute;n (OE3):</strong> Las variables macroecon&oacute;micas y de mercado
        <strong>no mejoran significativamente la predicci&oacute;n puntual</strong> de volatilidad
        (test de Diebold-Mariano, p &gt; 0.05). Ambos modelos logran m&eacute;tricas pr&aacute;cticamente
        id&eacute;nticas. Sin embargo, el valor de las variables macro reside en el
        <strong>calendario de eventos</strong> &mdash; los d&iacute;as de publicaci&oacute;n presentan
        un +11.6% de volatilidad anormal explotable. Ver P&aacute;gina 4 (Asesor de Carteras)
        para la aplicaci&oacute;n pr&aacute;ctica de esta se&ntilde;al.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Validación Walk-Forward ───────────────────────────────────────────────────
st.markdown("### Validación Walk-Forward (Expanding Window)")

wf_results = walk_forward_validate(n_splits=5)

if wf_results:
    import pandas as _pd_wf

    df_wf = _pd_wf.DataFrame(wf_results)

    mean_rmse = df_wf['rmse'].mean()
    std_rmse = df_wf['rmse'].std()
    mean_r2 = df_wf['r2'].mean()
    std_r2 = df_wf['r2'].std()

    # Summary cards
    wf_c1, wf_c2, wf_c3 = st.columns(3)
    with wf_c1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F8FAFC, #EFF6FF);
                    border: 1px solid #BFDBFE; border-radius: 12px; padding: 18px;
                    text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase;
                        letter-spacing: 0.1em; color: #64748B;">RMSE medio</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #1E40AF;">
                {mean_rmse:.4f}</div>
            <div style="font-size: 0.75rem; color: #64748B;">
                &sigma; = {std_rmse:.4f}</div>
        </div>
        """, unsafe_allow_html=True)
    with wf_c2:
        r2_color = "#059669" if mean_r2 > 0.5 else "#D97706" if mean_r2 > 0.3 else "#DC2626"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F8FAFC, #ECFDF5);
                    border: 1px solid #A7F3D0; border-radius: 12px; padding: 18px;
                    text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase;
                        letter-spacing: 0.1em; color: #64748B;">R&sup2; medio</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: {r2_color};">
                {mean_r2:.3f}</div>
            <div style="font-size: 0.75rem; color: #64748B;">
                &sigma; = {std_r2:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    with wf_c3:
        stability = "Alta" if std_rmse / mean_rmse < 0.15 else "Media" if std_rmse / mean_rmse < 0.30 else "Baja"
        stab_color = "#059669" if stability == "Alta" else "#D97706" if stability == "Media" else "#DC2626"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #F8FAFC, #FFF7ED);
                    border: 1px solid #FED7AA; border-radius: 12px; padding: 18px;
                    text-align: center;">
            <div style="font-size: 0.7rem; text-transform: uppercase;
                        letter-spacing: 0.1em; color: #64748B;">Estabilidad</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: {stab_color};">
                {stability}</div>
            <div style="font-size: 0.75rem; color: #64748B;">
                CV(RMSE) = {std_rmse / mean_rmse:.1%}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    # Fold detail table
    df_display = df_wf.rename(columns={
        'fold': 'Fold',
        'train_period': 'Período train',
        'test_period': 'Período test',
        'n_train': 'N train',
        'n_test': 'N test',
        'rmse': 'RMSE',
        'r2': 'R²',
    })
    st.dataframe(
        df_display.style.format({'RMSE': '{:.4f}', 'R²': '{:.3f}'}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("""
    <div class="method-note">
        <p>
            <strong>Interpretación:</strong> La validación walk-forward simula un entorno
            de producción real: el modelo se entrena solo con datos pasados y se evalúa en
            el período inmediatamente siguiente. Una baja variabilidad del RMSE entre folds
            (CV &lt; 15%) indica que el modelo generaliza de forma estable a lo largo del
            tiempo, sin depender de un split concreto.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No se pudieron generar folds suficientes para la validación walk-forward.")

# ── Nota metodológica ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="method-note">
        <p>
            <strong>Metodología:</strong> Modelo XGBoost-HAR con 15 features
            (3 autorregresivas + 12 macro/mercado). Split temporal 80/20,
            entrenamiento hasta {train_end.strftime('%d/%m/%Y')}.
            Umbral de alta volatilidad: percentil 75 rolling (63 días).
            Validación cruzada walk-forward con ventana expansiva (5 folds).
            Datos hasta <strong>{signal['fecha'].strftime('%d/%m/%Y')}</strong>.
            En producción se conectaría a feeds de datos en tiempo real.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Conclusión: aportación diferencial ───────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Conclusión — Aportación diferencial del TFG:</strong> La
        <strong>señal combinada (XGBoost + calendario macro)</strong> es la
        contribución original de este trabajo. Mientras que los modelos de
        volatilidad clásicos (GARCH, HAR) se limitan a la predicción puntual,
        esta herramienta transforma la predicción en una señal accionable
        (semáforo de riesgo) que el gestor puede integrar directamente en su
        proceso de decisión. La fusión de dos fuentes independientes de
        información &mdash;predicción cuantitativa de ML y calendario de eventos
        macroeconómicos&mdash; incrementa la convicción: cuando ambas señales
        coinciden (alta volatilidad + evento macro), la evidencia histórica muestra
        los peores escenarios de cola. En un entorno productivo, el sistema se
        alimentaría de feeds de datos en tiempo real, permitiendo al gestor
        reaccionar de forma anticipada y sistemática.
    </p>
</div>
""", unsafe_allow_html=True)
