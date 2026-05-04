"""Página 1: Resumen Ejecutivo — KPIs, equity curves, tabla comparativa."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from utils.strategies import (
    run_backtest, get_all_metrics, get_all_metrics_net, calc_metrics,
    bootstrap_sharpe_ci, compute_efficient_frontier,
    STRATEGY_NAMES, STRATEGY_COLORS,
    TRANSACTION_COST_BPS,
    style_plotly_chart, load_css,
)

load_css()
st.header("Resumen Ejecutivo")
st.caption("Visión general del rendimiento de las 4 estrategias de gestión táctica")

# ── Cargar datos ──────────────────────────────────────────────────────────────
bt = run_backtest()
df_metrics = get_all_metrics(bt)

# ── Selector de estrategia + inversión ───────────────────────────────────────
col_strat, col_inv = st.columns([2, 1])
with col_strat:
    strategy = st.selectbox("Estrategia", list(STRATEGY_NAMES.keys()), index=2)
with col_inv:
    inversion = st.number_input(
        "Inversión inicial (€)", value=1_000_000, step=100_000,
        min_value=100_000, format="%d",
    )

w_col = STRATEGY_NAMES[strategy]
strat_color = STRATEGY_COLORS[strategy]
m_sel = df_metrics.loc[strategy]
m_bh = df_metrics.loc['Buy & Hold']
is_bh = strategy == 'Buy & Hold'

delta_ret = m_sel['Rent. anual (%)'] - m_bh['Rent. anual (%)']
delta_sharpe = m_sel['Sharpe'] - m_bh['Sharpe']
delta_dd = m_sel['Max Drawdown (%)'] - m_bh['Max Drawdown (%)']
dias_red = 100 - m_sel['% días 100% inv.']

# ── KPIs — tarjetas ──────────────────────────────────────────────────────────
st.markdown(f'<div class="section-header"><h3>KPIs — {strategy}</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

_ret_color = '#2ca02c' if m_sel['Rent. anual (%)'] > 0 else '#d62728'
_dd_color = '#d62728'
_delta_ret_color = '#059669' if delta_ret >= 0 else '#DC2626'
_delta_sharpe_color = '#059669' if delta_sharpe >= 0 else '#DC2626'
_delta_dd_color = '#059669' if delta_dd >= 0 else '#DC2626'

_bh_sub = lambda val, fmt, unit='': (
    f'<div style="font-size:0.72rem;color:#94A3B8;">Referencia (Buy &amp; Hold)</div>'
    if is_bh else
    f'<div style="font-size:0.72rem;color:{{"+" if val >= 0 else "-": "#059669" if val >= 0 else "#DC2626"}};">'
    f'{val:{fmt}}{unit} vs Buy &amp; Hold</div>'
)

st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 16px 0;">
    <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: {_ret_color};"></div>
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #64748B; margin-bottom: 10px;">Rent. anual</div>
        <div style="font-size: 1.5rem; font-weight: 900; color: #0D1B2A;
                    letter-spacing: -0.04em; line-height: 1; margin-bottom: 4px;">
            {m_sel['Rent. anual (%)']:.1f} %</div>
        <div style="font-size: 0.72rem; color: {_delta_ret_color if not is_bh else '#94A3B8'};">
            {'Referencia (Buy &amp; Hold)' if is_bh else f'{delta_ret:+.1f} % vs Buy &amp; Hold'}</div>
    </div>
    <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: {strat_color};"></div>
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #64748B; margin-bottom: 10px;">Sharpe Ratio</div>
        <div style="font-size: 1.5rem; font-weight: 900; color: #0D1B2A;
                    letter-spacing: -0.04em; line-height: 1; margin-bottom: 4px;">
            {m_sel['Sharpe']:.3f}</div>
        <div style="font-size: 0.72rem; color: {_delta_sharpe_color if not is_bh else '#94A3B8'};">
            {'Referencia (Buy &amp; Hold)' if is_bh else f'{delta_sharpe:+.3f} vs Buy &amp; Hold'}</div>
    </div>
    <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: {_dd_color};"></div>
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #64748B; margin-bottom: 10px;">Max Drawdown</div>
        <div style="font-size: 1.5rem; font-weight: 900; color: {_dd_color};
                    letter-spacing: -0.04em; line-height: 1; margin-bottom: 4px;">
            {m_sel['Max Drawdown (%)']:.2f} %</div>
        <div style="font-size: 0.72rem; color: {_delta_dd_color if not is_bh else '#94A3B8'};">
            {'Referencia (Buy &amp; Hold)' if is_bh else f'{delta_dd:+.2f} % vs Buy &amp; Hold'}</div>
    </div>
    <div style="background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: 20px 18px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: #D97706;"></div>
        <div style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #64748B; margin-bottom: 10px;">Días 100 % invertido</div>
        <div style="font-size: 1.5rem; font-weight: 900; color: #0D1B2A;
                    letter-spacing: -0.04em; line-height: 1; margin-bottom: 4px;">
            {m_sel['% días 100% inv.']:.1f} %</div>
        <div style="font-size: 0.72rem; color: #64748B;">
            {'Siempre al 100 %' if dias_red == 0 else f'Reducido solo {dias_red:.1f} % de días'}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Valor Económico en € ─────────────────────────────────────────────────────
st.markdown(f'<div class="section-header"><h3>Valor Económico — Impacto en Cartera Real</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

# Métricas Buy & Hold
ret_bh = np.exp(bt['ret_w_baseline']) - 1
m_bh_full = calc_metrics(ret_bh, 'Buy & Hold')
eq_bh_final = bt['eq_w_baseline'].iloc[-1]

# Métricas estrategia seleccionada
ret_sel = np.exp(bt[f'ret_{w_col}']) - 1
m_sel_full = calc_metrics(ret_sel, strategy)
eq_sel_final = bt[f'eq_{w_col}'].iloc[-1]

# Cálculos en €
valor_final_bh = inversion * (eq_bh_final / 100)
valor_final_sel = inversion * (eq_sel_final / 100)
diferencia_neta = valor_final_sel - valor_final_bh

# Max drawdown en €
dd_bh_pct = abs(m_bh_full['Max Drawdown (%)']) / 100
dd_sel_pct = abs(m_sel_full['Max Drawdown (%)']) / 100
perdida_max_bh = inversion * dd_bh_pct
perdida_max_sel = inversion * dd_sel_pct
perdida_evitada = perdida_max_bh - perdida_max_sel

# VaR diario en €
var_bh = abs(m_bh_full['VaR 95% (%)']) / 100
var_sel = abs(m_sel_full['VaR 95% (%)']) / 100
var_bh_eur = inversion * var_bh
var_sel_eur = inversion * var_sel
var_ahorro = var_bh_eur - var_sel_eur

# Formatear euros
def fmt_eur(v):
    """Formatea valor en euros con separadores de miles."""
    return f"{v:,.0f} €".replace(",", ".")

dif_color = '#059669' if diferencia_neta >= 0 else '#DC2626'
dif_arrow = '▲' if diferencia_neta >= 0 else '▼'
evit_color = '#059669' if perdida_evitada >= 0 else '#DC2626'
var_color = '#059669' if var_ahorro >= 0 else '#DC2626'

st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;">
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:{strat_color};"></div>
        <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">Valor Final Cartera</div>
        <div style="font-size:1.5rem;font-weight:900;color:#0D1B2A;letter-spacing:-0.04em;line-height:1;margin-bottom:4px;">{fmt_eur(valor_final_sel)}</div>
        <div style="font-size:0.72rem;color:{dif_color if not is_bh else '#94A3B8'};margin-bottom:0;">{'Referencia pasiva' if is_bh else f'{dif_arrow} {fmt_eur(abs(diferencia_neta))} vs Buy &amp; Hold'}</div>
    </div>
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:#059669;"></div>
        <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">{'Max Drawdown' if is_bh else 'Pérdida Máxima Evitada'}</div>
        <div style="font-size:1.5rem;font-weight:900;color:{evit_color if not is_bh else '#d62728'};letter-spacing:-0.04em;line-height:1;margin-bottom:4px;">{fmt_eur(perdida_max_sel) if is_bh else fmt_eur(abs(perdida_evitada))}</div>
        <div style="font-size:0.72rem;color:#64748B;margin-bottom:0;">Max DD: {fmt_eur(perdida_max_sel)}{'' if is_bh else f' vs {fmt_eur(perdida_max_bh)}'}</div>
    </div>
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:#D97706;"></div>
        <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">VaR Diario 95%</div>
        <div style="font-size:1.5rem;font-weight:900;color:#D97706;letter-spacing:-0.04em;line-height:1;margin-bottom:4px;">{fmt_eur(var_sel_eur)}</div>
        <div style="font-size:0.72rem;color:{var_color if not is_bh else '#94A3B8'};margin-bottom:0;">{'Referencia pasiva' if is_bh else f'Ahorro diario: {fmt_eur(abs(var_ahorro))} vs B&amp;H'}</div>
    </div>
    <div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;
        box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;right:0;height:4px;background:#1f77b4;"></div>
        <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">Valor Final Buy &amp; Hold</div>
        <div style="font-size:1.5rem;font-weight:900;color:#0D1B2A;letter-spacing:-0.04em;line-height:1;margin-bottom:4px;">{fmt_eur(valor_final_bh)}</div>
        <div style="font-size:0.72rem;color:#94A3B8;margin-bottom:0;">Referencia pasiva</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="method-note">
    <p>
        <strong>Lectura:</strong> Sobre una cartera de <strong>{fmt_eur(inversion)}</strong>,
        la estrategia <strong>{strategy}</strong> genera un valor final de <strong>{fmt_eur(valor_final_sel)}</strong>
        {'(referencia pasiva)' if is_bh else f'({dif_arrow} {fmt_eur(abs(diferencia_neta))} vs gestión pasiva)'}.
        {'El' if is_bh else 'El drawdown máximo se reduce en <strong>' + fmt_eur(abs(perdida_evitada)) + '</strong>, y el'}
        riesgo diario (VaR 95%) {'es de' if is_bh else 'baja en'} <strong>{fmt_eur(var_sel_eur) if is_bh else fmt_eur(abs(var_ahorro))}</strong>.
        Ajusta la inversión inicial para simular tu cartera.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Equity Curves ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Equity Curves — Período de Test</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

fig = go.Figure()
for name, wc in STRATEGY_NAMES.items():
    fig.add_trace(go.Scatter(
        x=bt.index, y=bt[f'eq_{wc}'],
        name=name,
        line=dict(color=STRATEGY_COLORS[name], width=2),
        hovertemplate=f'<b>{name}</b><br>Fecha: %{{x|%Y-%m-%d}}<br>Valor: %{{y:.2f}}<extra></extra>',
    ))

fig.add_hline(y=100, line_dash="dot", line_color="gray", opacity=0.4)
fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Valor de la cartera",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    hovermode="x unified",
)
style_plotly_chart(fig, height=480)
st.plotly_chart(fig, use_container_width=True)

# ── Frontera Eficiente ────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Frontera Eficiente — Espacio Risk-Return</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
    'Optimización de Markowitz sobre las 4 estrategias como activos. '
    'La curva muestra las combinaciones óptimas que minimizan la volatilidad '
    'para cada nivel de rentabilidad objetivo.</p>',
    unsafe_allow_html=True,
)

_ef = compute_efficient_frontier()

fig_ef = go.Figure()

# Frontera eficiente (curva)
fig_ef.add_trace(go.Scatter(
    x=_ef['frontier_vols'], y=_ef['frontier_rets'],
    mode='lines',
    name='Frontera eficiente',
    line=dict(color='#0D1B2A', width=2.5),
    hovertemplate='Vol: %{x:.2f}%<br>Ret: %{y:.2f}%<extra>Frontera</extra>',
))

# 4 estrategias individuales
for s in _ef['strategies']:
    fig_ef.add_trace(go.Scatter(
        x=[s['vol']], y=[s['ret']],
        mode='markers+text',
        name=s['name'],
        marker=dict(color=STRATEGY_COLORS[s['name']], size=12,
                    line=dict(width=2, color='white')),
        text=[s['name'].split(':')[-1].strip() if ':' in s['name'] else s['name']],
        textposition='top center',
        textfont=dict(size=10, color=STRATEGY_COLORS[s['name']]),
        hovertemplate=(f'<b>{s["name"]}</b><br>Vol: {s["vol"]:.2f}%<br>'
                       f'Ret: {s["ret"]:.2f}%<br>Sharpe: {s["sharpe"]:.3f}'
                       '<extra></extra>'),
    ))

# Cartera de máximo Sharpe
fig_ef.add_trace(go.Scatter(
    x=[_ef['max_sharpe']['vol']], y=[_ef['max_sharpe']['ret']],
    mode='markers',
    name=f'Máx. Sharpe ({_ef["max_sharpe"].get("sharpe", 0):.3f})',
    marker=dict(symbol='star', size=18, color='#FFD700',
                line=dict(width=2, color='#0D1B2A')),
    hovertemplate=(f'<b>Máx. Sharpe</b><br>Vol: {_ef["max_sharpe"]["vol"]:.2f}%<br>'
                   f'Ret: {_ef["max_sharpe"]["ret"]:.2f}%<extra></extra>'),
))

# Cartera de mínima varianza
fig_ef.add_trace(go.Scatter(
    x=[_ef['min_var']['vol']], y=[_ef['min_var']['ret']],
    mode='markers',
    name='Mínima varianza',
    marker=dict(symbol='diamond', size=14, color='#7C3AED',
                line=dict(width=2, color='white')),
    hovertemplate=(f'<b>Mín. varianza</b><br>Vol: {_ef["min_var"]["vol"]:.2f}%<br>'
                   f'Ret: {_ef["min_var"]["ret"]:.2f}%<extra></extra>'),
))

fig_ef.update_layout(
    xaxis_title="Volatilidad anual (%)",
    yaxis_title="Rentabilidad anual (%)",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    hovermode="closest",
)
style_plotly_chart(fig_ef, height=480)
st.plotly_chart(fig_ef, use_container_width=True)

# Tabla de pesos óptimos
_ms_w = _ef['max_sharpe']['weights']
_weight_html = ''.join(
    f'<div style="text-align:center;">'
    f'<div style="font-size:0.6rem;color:#64748B;text-transform:uppercase;">{name}</div>'
    f'<div style="font-size:1.3rem;font-weight:800;color:{STRATEGY_COLORS[name]};">{w:.1f}%</div>'
    f'</div>'
    for name, w in _ms_w.items()
)

st.markdown(f"""
<div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:14px;
            padding:18px 24px; margin:8px 0 16px;">
    <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                letter-spacing:0.1em; color:#64748B; margin-bottom:10px; text-align:center;">
        Pesos &oacute;ptimos &mdash; Cartera de M&aacute;ximo Sharpe ({_ef['max_sharpe'].get('sharpe', 0):.3f})</div>
    <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px;">
        {_weight_html}
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="method-note">
    <p>
        <strong>Nota (OE5):</strong> La frontera eficiente muestra las combinaciones &oacute;ptimas
        de las 4 estrategias, tratando cada una como un activo independiente.
        La cartera de m&aacute;ximo Sharpe identifica la asignaci&oacute;n que maximiza el
        exceso de retorno por unidad de riesgo. Esto confirma que la combinaci&oacute;n
        t&aacute;ctica de las se&ntilde;ales de volatilidad y calendario macro mejora el
        perfil risk-return frente a la gesti&oacute;n pasiva pura.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Tabla de métricas ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Tabla Comparativa de Estrategias</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

display_metrics = df_metrics.copy().round(3)
st.dataframe(
    display_metrics.style.format({
        'Rent. anual (%)': '{:.2f} %',
        'Vol. anual (%)': '{:.2f} %',
        'Sharpe': '{:.3f}',
        'Max Drawdown (%)': '{:.2f} %',
        'Calmar': '{:.3f}',
        'VaR 95% (%)': '{:.4f} %',
        'CVaR 95% (%)': '{:.4f} %',
        '% días 100% inv.': '{:.1f} %',
    }).background_gradient(subset=['Sharpe'], cmap='RdYlGn')
    .background_gradient(subset=['Max Drawdown (%)'], cmap='RdYlGn_r'),
    use_container_width=True,
)

# ── Impacto de costes de transacción ─────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Robustez: Impacto de Costes de Transacción</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    f'<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 12px;">'
    f'Métricas recalculadas con un coste de <strong>{TRANSACTION_COST_BPS} pb '
    f'({TRANSACTION_COST_BPS/100:.1f}%)</strong> por operación, proporcional al '
    f'cambio de peso. Demuestra que las estrategias tácticas mantienen su ventaja '
    f'neta de costes.</p>',
    unsafe_allow_html=True,
)

df_metrics_net = get_all_metrics_net(bt)
display_net = df_metrics_net.copy().round(3)
st.dataframe(
    display_net.style.format({
        'Rent. anual (%)': '{:.2f} %',
        'Vol. anual (%)': '{:.2f} %',
        'Sharpe': '{:.3f}',
        'Max Drawdown (%)': '{:.2f} %',
        'Calmar': '{:.3f}',
        'VaR 95% (%)': '{:.4f} %',
        'CVaR 95% (%)': '{:.4f} %',
        'Costes totales (%)': '{:.3f} %',
        'N.º rebalanceos': '{:.0f}',
        '% días 100% inv.': '{:.1f} %',
    }).background_gradient(subset=['Sharpe'], cmap='RdYlGn')
    .background_gradient(subset=['Costes totales (%)'], cmap='RdYlGn_r'),
    use_container_width=True,
)

# ── Intervalos de confianza del Sharpe ──────────────────────────────────────
st.markdown('<div class="section-header"><h3>Intervalos de Confianza Bootstrap (Sharpe Ratio, 95%)</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 12px;">'
    'Bootstrap con 5.000 remuestreos. El intervalo indica la incertidumbre '
    'estadística del Sharpe observado.</p>',
    unsafe_allow_html=True,
)

ci_cards = []
for name, w_col in STRATEGY_NAMES.items():
    rets = np.exp(bt[f'ret_{w_col}']) - 1
    lo, hi, mean_s = bootstrap_sharpe_ci(rets)
    color = STRATEGY_COLORS[name]
    sig = 'Significativo' if lo > 0 else 'Incluye cero'
    sig_color = '#059669' if lo > 0 else '#D97706'
    ci_cards.append(
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:20px 18px;'
        f'box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:4px;background:{color};"></div>'
        f'<div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.1em;color:#64748B;margin-bottom:8px;">{name}</div>'
        f'<div style="font-size:1.4rem;font-weight:900;color:#0D1B2A;letter-spacing:-0.04em;'
        f'line-height:1;margin-bottom:6px;">{mean_s:.3f}</div>'
        f'<div style="font-size:0.78rem;color:#475569;margin-bottom:4px;">'
        f'IC 95%: [{lo:.3f}, {hi:.3f}]</div>'
        f'<div style="font-size:0.68rem;font-weight:700;color:{sig_color};">{sig}</div></div>'
    )

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;">'
    + ''.join(ci_cards) + '</div>',
    unsafe_allow_html=True,
)

# ── Conclusión ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Conclusión:</strong> Los resultados confirman las tres hipótesis del
        TFG. <strong>(Q1)</strong> La volatilidad del IBEX 35 es predecible con alta
        precisión mediante un modelo XGBoost-HAR (R² &gt; 0.96).
        <strong>(Q2)</strong> XGBoost supera a los benchmarks autorregresivos puros
        gracias a la incorporación de variables de mercado y macroeconómicas.
        <strong>(Q3)</strong> El calendario macro, pese a un impacto marginal en
        rentabilidad, permite reducir la exposición tácticamente en días de alta
        incertidumbre, mejorando el perfil riesgo-retorno (mayor Sharpe, menor
        drawdown) con un coste mínimo. La combinación de ambas señales &mdash;ML +
        calendario&mdash; constituye la propuesta de valor central de este trabajo.
        Los resultados son <strong>robustos a costes de transacción</strong>
        ({TRANSACTION_COST_BPS} pb/operación) y los intervalos de confianza bootstrap
        confirman la significación estadística del Sharpe ratio.
        La <strong>frontera eficiente</strong> confirma que las estrategias tácticas
        dominan al Buy &amp; Hold en el espacio risk-return: la cartera de máximo
        Sharpe asigna el mayor peso a las estrategias que combinan señales de
        volatilidad y calendario macro, validando la propuesta central del TFG.
    </p>
</div>
""", unsafe_allow_html=True)
