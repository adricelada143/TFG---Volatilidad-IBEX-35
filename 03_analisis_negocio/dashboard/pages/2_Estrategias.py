"""Página 2: Estrategias de Inversión — Comparativa interactiva."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from utils.strategies import (
    run_backtest, get_all_metrics, calc_metrics,
    STRATEGY_NAMES, STRATEGY_COLORS, style_plotly_chart, load_css,
)

load_css()
st.header("Estrategias de Inversión")
st.caption("Comparativa interactiva de las 4 estrategias de gestión táctica")

bt = run_backtest()

# ── Controles ─────────────────────────────────────────────────────────────────
col_ctrl1, col_ctrl2 = st.columns([2, 1])

with col_ctrl1:
    selected = st.multiselect(
        "Estrategias a comparar",
        list(STRATEGY_NAMES.keys()),
        default=list(STRATEGY_NAMES.keys()),
    )

with col_ctrl2:
    date_range = st.date_input(
        "Rango temporal",
        value=(bt.index[0].date(), bt.index[-1].date()),
        min_value=bt.index[0].date(),
        max_value=bt.index[-1].date(),
    )

# Filtrar por rango temporal
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    bt_filtered = bt.loc[start:end]
else:
    bt_filtered = bt

if len(selected) == 0:
    st.warning("Selecciona al menos una estrategia.")
    st.stop()

# ── Simulador What-If ────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Simulador What-If</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
            'Ajusta la exposición en días de señal y observa cómo cambian las métricas en tiempo real. '
            'El valor por defecto (50 %) reproduce el backtest original.</p>',
            unsafe_allow_html=True)

exposure_pct = st.slider(
    "Exposición en días de señal (%)", 0, 100, 50, 5,
    help="0 % = salir completamente del mercado en días de señal. "
         "100 % = ignorar la señal (equivale a Buy & Hold).",
)
factor = exposure_pct / 100  # 0.0 a 1.0

# Recomputar pesos sobre bt_filtered sin tocar el backtest cacheado
bt_whatif = bt_filtered.copy()
bt_whatif['w_vol'] = np.where(bt_filtered['alta_vol'] == 1, factor, 1.0)
bt_whatif['w_macro'] = np.where(bt_filtered['es_evento_o_previo'] == 1, factor, 1.0)
bt_whatif['w_comb'] = np.where(
    (bt_filtered['alta_vol'] == 1) | (bt_filtered['es_evento_hi_o_previo'] == 1),
    factor, 1.0,
)
bt_whatif['w_baseline'] = 1.0  # Buy & Hold siempre 100 %

# Recomputar retornos y equity curves con los nuevos pesos
for name, w_col in STRATEGY_NAMES.items():
    bt_whatif[f'ret_{w_col}'] = bt_whatif['log_ret'] * bt_whatif[w_col]
    bt_whatif[f'eq_{w_col}'] = 100 * np.exp(bt_whatif[f'ret_{w_col}'].cumsum())

# ── Métricas dinámicas según periodo ──────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Métricas del período seleccionado</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

metric_cards = []
for name in selected:
    w_col = STRATEGY_NAMES[name]
    simple_ret = np.exp(bt_whatif[f'ret_{w_col}']) - 1
    m = calc_metrics(simple_ret, name)
    col = STRATEGY_COLORS[name]
    rent = m['Rent. anual (%)']
    sharpe = m['Sharpe']
    dd = m['Max Drawdown (%)']
    vol = m['Vol. anual (%)']
    rent_color = '#059669' if rent >= 0 else '#DC2626'
    card = (
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:{col};"></div>'
        f'<div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">{name}</div>'
        f'<div style="font-size:1.7rem;font-weight:900;color:{rent_color};letter-spacing:-0.04em;line-height:1;margin-bottom:4px;">{rent:+.2f}%</div>'
        f'<div style="font-size:0.72rem;color:#94A3B8;margin-bottom:14px;">Rent. anual</div>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;border-top:1px solid #F1F5F9;padding-top:12px;">'
        f'<div style="text-align:center;padding:0 2px;"><div style="font-size:0.55rem;font-weight:700;text-transform:uppercase;color:#94A3B8;margin-bottom:3px;white-space:nowrap;">Sharpe</div>'
        f'<div style="font-size:0.82rem;font-weight:800;color:#0D1B2A;white-space:nowrap;">{sharpe:.3f}</div></div>'
        f'<div style="text-align:center;padding:0 2px;border-left:1px solid #F1F5F9;border-right:1px solid #F1F5F9;">'
        f'<div style="font-size:0.55rem;font-weight:700;text-transform:uppercase;color:#94A3B8;margin-bottom:3px;white-space:nowrap;">Max DD</div>'
        f'<div style="font-size:0.82rem;font-weight:800;color:#DC2626;white-space:nowrap;">{dd:.2f}%</div></div>'
        f'<div style="text-align:center;padding:0 2px;"><div style="font-size:0.55rem;font-weight:700;text-transform:uppercase;color:#94A3B8;margin-bottom:3px;white-space:nowrap;">Vol.</div>'
        f'<div style="font-size:0.82rem;font-weight:800;color:#0D1B2A;white-space:nowrap;">{vol:.2f}%</div></div>'
        f'</div></div>'
    )
    metric_cards.append(card)

n_cols = len(selected)
grid_cols = f'repeat({n_cols}, 1fr)'
st.markdown(
    f'<div style="display:grid;grid-template-columns:{grid_cols};gap:14px;margin:16px 0;">'
    + ''.join(metric_cards)
    + '</div>',
    unsafe_allow_html=True,
)

# ── Equity curves filtradas ───────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Equity Curves</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

fig_eq = go.Figure()
for name in selected:
    w_col = STRATEGY_NAMES[name]
    rets = bt_whatif[f'ret_{w_col}']
    eq = 100 * np.exp(rets.cumsum())
    fig_eq.add_trace(go.Scatter(
        x=bt_whatif.index, y=eq,
        name=name, line=dict(color=STRATEGY_COLORS[name], width=2),
    ))

fig_eq.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.4)
fig_eq.update_layout(
    xaxis_title="Fecha", yaxis_title="Valor (base 100)",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)
style_plotly_chart(fig_eq, height=450)
st.plotly_chart(fig_eq, use_container_width=True)

# ── Pesos a lo largo del tiempo ───────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Exposición al mercado a lo largo del tiempo</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(f'<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
            f'Muestra cuándo cada estrategia reduce la exposición al {exposure_pct} %</p>',
            unsafe_allow_html=True)

fig_w = make_subplots(
    rows=len(selected), cols=1, shared_xaxes=True,
    subplot_titles=selected, vertical_spacing=0.05,
)

for i, name in enumerate(selected, 1):
    w_col = STRATEGY_NAMES[name]
    fig_w.add_trace(go.Scatter(
        x=bt_whatif.index,
        y=bt_whatif[w_col] * 100,
        fill='tozeroy',
        name=name,
        line=dict(color=STRATEGY_COLORS[name], width=1),
    ), row=i, col=1)
    fig_w.update_yaxes(
        range=[0, 110], ticksuffix=" %",
        title_text="Exposición", row=i, col=1,
    )

fig_w.update_layout(showlegend=False, hovermode="x unified")
style_plotly_chart(fig_w, height=200 * len(selected))
st.plotly_chart(fig_w, use_container_width=True)

# ── Scatter: Retorno vs Riesgo ────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Retorno vs. Riesgo</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

metrics_list = []
for name in selected:
    w_col = STRATEGY_NAMES[name]
    simple_ret = np.exp(bt_whatif[f'ret_{w_col}']) - 1
    m = calc_metrics(simple_ret, name)
    metrics_list.append(m)

df_m = pd.DataFrame(metrics_list)

fig_scatter = go.Figure()
for _, row in df_m.iterrows():
    name = row['Estrategia']
    fig_scatter.add_trace(go.Scatter(
        x=[row['Vol. anual (%)']],
        y=[row['Rent. anual (%)']],
        mode='markers+text',
        text=[name],
        textposition='top center',
        marker=dict(size=15, color=STRATEGY_COLORS[name]),
        name=name,
        hovertemplate=(
            f"<b>{name}</b><br>"
            f"Rent.: {row['Rent. anual (%)']:.2f} %<br>"
            f"Vol.: {row['Vol. anual (%)']:.2f} %<br>"
            f"Sharpe: {row['Sharpe']:.3f}<extra></extra>"
        ),
    ))

fig_scatter.update_layout(
    xaxis_title="Volatilidad anual (%)",
    yaxis_title="Rentabilidad anual (%)",
    showlegend=False,
)
style_plotly_chart(fig_scatter, height=450)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── Conclusión ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Conclusión:</strong> La <strong>Estrategia B (Calendario Macro)</strong>
        ofrece el mejor equilibrio rentabilidad-riesgo: obtiene un ratio de Sharpe
        superior al Buy &amp; Hold reduciendo la exposición únicamente en días de
        publicación macroeconómica, lo que mitiga los picos de volatilidad sin
        sacrificar retorno de forma significativa. La Estrategia C (Combinada)
        refuerza la protección en los escenarios más adversos, a costa de una
        ligera reducción adicional de rentabilidad. Para un gestor de carteras,
        la implicación práctica es clara: incorporar el calendario macro como
        filtro táctico de exposición es una mejora dominante frente a la gestión
        pasiva, con coste de implementación nulo (información pública).
    </p>
</div>
""", unsafe_allow_html=True)
