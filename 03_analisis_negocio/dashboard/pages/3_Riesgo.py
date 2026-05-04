"""Página 3: Análisis de Riesgo — Drawdown, VaR/CVaR, rolling Sharpe."""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

from utils.strategies import (
    run_backtest, get_all_metrics, calc_drawdown, calc_rolling_sharpe,
    get_best_worst_days, get_stress_test_results,
    STRATEGY_NAMES, STRATEGY_COLORS,
    INVESTOR_PROFILES, style_plotly_chart, load_css,
)

load_css()
st.header("Análisis de Riesgo")
st.caption("Drawdown, distribución de retornos, VaR/CVaR y rolling Sharpe")

bt = run_backtest()
metrics = get_all_metrics(bt)

# ── Perfil de inversor + Cartera ─────────────────────────────────────────────
col_perfil, col_cartera = st.columns([2, 1])
with col_perfil:
    perfil = st.select_slider(
        "Perfil de inversor",
        options=list(INVESTOR_PROFILES.keys()),
        value="Moderado",
    )
with col_cartera:
    cartera_eur = st.number_input(
        "Cartera IBEX 35 (€)",
        min_value=10_000,
        max_value=100_000_000,
        value=1_000_000,
        step=100_000,
        format="%d",
    )

profile = INVESTOR_PROFILES[perfil]
recommended_strategy = profile['strategy']

# ── Métricas para el banner ──────────────────────────────────────────────────
rec_metrics = metrics.loc[recommended_strategy]
bh_metrics = metrics.loc['Buy & Hold']

rent_anual_pct = rec_metrics['Rent. anual (%)']
mdd_pct = rec_metrics['Max Drawdown (%)']
var_pct = rec_metrics['VaR 95% (%)']
delta_rent_pct = rent_anual_pct - bh_metrics['Rent. anual (%)']

rent_anual_eur = cartera_eur * rent_anual_pct / 100
mdd_eur = cartera_eur * mdd_pct / 100
var_eur = cartera_eur * var_pct / 100
delta_rent_eur = cartera_eur * delta_rent_pct / 100

# ── Banner de recomendación ──────────────────────────────────────────────────
def _fmt_eur(v):
    """Formatea un valor en € con signo y separador de miles."""
    sign = "+" if v > 0 else ""
    return f"{sign}{v:,.0f} €".replace(",", ".")

st.markdown(f"""
<div style="background: linear-gradient(135deg, {profile['color']}11, {profile['color']}22);
            border: 1px solid {profile['color']}44; border-radius: 12px;
            padding: 1.5rem 2rem; margin: 1rem 0 1.5rem 0;">
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem;">
        <span style="font-size: 2rem;">{profile['icon']}</span>
        <div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {profile['color']};">
                Perfil {perfil} → {recommended_strategy}
            </div>
            <div style="font-size: 0.9rem; color: #5D6D7E; margin-top: 2px;">
                {profile['desc']}
            </div>
        </div>
    </div>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem;">
        <div style="background: white; border-radius: 8px; padding: 0.75rem 1rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            <div style="font-size: 0.75rem; color: #5D6D7E; text-transform: uppercase;">
                Rent. anual estimada</div>
            <div style="font-size: 1.1rem; font-weight: 700;
                        color: {'#2ca02c' if rent_anual_pct > 0 else '#d62728'};">
                {_fmt_eur(rent_anual_eur)}</div>
            <div style="font-size: 0.7rem; color: #95A5A6;">{rent_anual_pct:+.2f} %</div>
        </div>
        <div style="background: white; border-radius: 8px; padding: 0.75rem 1rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            <div style="font-size: 0.75rem; color: #5D6D7E; text-transform: uppercase;">
                Max Drawdown</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #d62728;">
                {_fmt_eur(mdd_eur)}</div>
            <div style="font-size: 0.7rem; color: #95A5A6;">{mdd_pct:.2f} %</div>
        </div>
        <div style="background: white; border-radius: 8px; padding: 0.75rem 1rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            <div style="font-size: 0.75rem; color: #5D6D7E; text-transform: uppercase;">
                VaR diario (95%)</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #d62728;">
                {_fmt_eur(var_eur)}</div>
            <div style="font-size: 0.7rem; color: #95A5A6;">{var_pct:.4f} %</div>
        </div>
        <div style="background: white; border-radius: 8px; padding: 0.75rem 1rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
            <div style="font-size: 0.75rem; color: #5D6D7E; text-transform: uppercase;">
                Δ vs Buy & Hold</div>
            <div style="font-size: 1.1rem; font-weight: 700;
                        color: {'#2ca02c' if delta_rent_eur >= 0 else '#d62728'};">
                {_fmt_eur(delta_rent_eur)}</div>
            <div style="font-size: 0.7rem; color: #95A5A6;">{delta_rent_pct:+.2f} pp</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Selectbox de estrategia (default = recomendada) ─────────────────────────
strategy_list = list(STRATEGY_NAMES.keys())
default_idx = strategy_list.index(recommended_strategy)

strategy = st.selectbox("Estrategia", strategy_list, index=default_idx)

if strategy == recommended_strategy:
    st.caption(f"✓ Coincide con la recomendación para perfil **{perfil}**")
else:
    st.caption(f"⚠ La recomendación para perfil **{perfil}** es **{recommended_strategy}**")

w_col = STRATEGY_NAMES[strategy]
color = STRATEGY_COLORS[strategy]

# ── Drawdown interactivo ──────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Drawdown</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

dd = calc_drawdown(bt, w_col)
fig_dd = go.Figure()
fig_dd.add_trace(go.Scatter(
    x=bt.index, y=dd, fill='tozeroy',
    line=dict(color=color, width=1),
    name=strategy,
    hovertemplate='Fecha: %{x|%Y-%m-%d}<br>Drawdown: %{y:.2f} %<extra></extra>',
))

# Marcar eventos macro
evento_dates = bt.index[bt['es_evento'] == 1]
for d in evento_dates:
    fig_dd.add_vline(x=d, line_color="red", opacity=0.05, line_width=1)

fig_dd.update_layout(
    yaxis_title="Drawdown (%)",
    xaxis_title="Fecha",
    annotations=[dict(
        text="Líneas rojas = días de evento macro", x=0.01, y=0.01,
        xref="paper", yref="paper", showarrow=False,
        font=dict(size=10, color="#E74C3C"),
    )],
)
style_plotly_chart(fig_dd, height=360)
st.plotly_chart(fig_dd, use_container_width=True)

# ── Distribución de retornos con VaR/CVaR ─────────────────────────────────────
st.markdown('<div class="section-header"><h3>Distribución de Retornos Diarios con VaR / CVaR</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

rets_pct = (np.exp(bt[f'ret_{w_col}']) - 1) * 100
var_95 = rets_pct.quantile(0.05)
cvar_95 = rets_pct[rets_pct <= var_95].mean()

fig_dist = go.Figure()
fig_dist.add_trace(go.Histogram(
    x=rets_pct, nbinsx=60, name='Retornos',
    marker_color=color, opacity=0.7,
    histnorm='probability density',
))
fig_dist.add_vline(x=var_95, line_dash="dash", line_color="#E74C3C",
                   annotation_text=f"VaR 95 %: {var_95:.3f} %")
fig_dist.add_vline(x=cvar_95, line_dash="dot", line_color="#922B21",
                   annotation_text=f"CVaR 95 %: {cvar_95:.3f} %")
fig_dist.add_vline(x=0, line_dash="dot", line_color="gray", opacity=0.3)

fig_dist.update_layout(
    xaxis_title="Retorno diario (%)", yaxis_title="Densidad",
    showlegend=False,
)
style_plotly_chart(fig_dist, height=400)
st.plotly_chart(fig_dist, use_container_width=True)

var_eur_daily = cartera_eur * var_95 / 100
cvar_eur_daily = cartera_eur * cvar_95 / 100

st.markdown(f"""
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 0.5rem 0 1.5rem 0;">
    <div style="background: white; border-radius: 10px; padding: 1.25rem 1.5rem;
                border-left: 4px solid #E74C3C; box-shadow: 0 2px 6px rgba(0,0,0,0.07);">
        <div style="font-size: 0.8rem; color: #5D6D7E; text-transform: uppercase; font-weight: 600;
                    letter-spacing: 0.5px;">VaR 95 % (diario)</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #d62728; margin: 0.4rem 0;">
            {var_95:.4f} %</div>
        <div style="font-size: 0.95rem; color: #2C3E50; font-weight: 500;">
            {_fmt_eur(var_eur_daily)} sobre cartera</div>
        <div style="font-size: 0.75rem; color: #95A5A6; margin-top: 0.3rem;">
            Pérdida máxima esperada el 95 % de los días</div>
    </div>
    <div style="background: white; border-radius: 10px; padding: 1.25rem 1.5rem;
                border-left: 4px solid #922B21; box-shadow: 0 2px 6px rgba(0,0,0,0.07);">
        <div style="font-size: 0.8rem; color: #5D6D7E; text-transform: uppercase; font-weight: 600;
                    letter-spacing: 0.5px;">CVaR 95 % (diario)</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: #922B21; margin: 0.4rem 0;">
            {cvar_95:.4f} %</div>
        <div style="font-size: 0.95rem; color: #2C3E50; font-weight: 500;">
            {_fmt_eur(cvar_eur_daily)} sobre cartera</div>
        <div style="font-size: 0.75rem; color: #95A5A6; margin-top: 0.3rem;">
            Pérdida media en el peor 5 % de los días</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Rolling Sharpe ────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Rolling Sharpe Ratio (ventana 63 días)</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

fig_rs = go.Figure()
for name, wc in STRATEGY_NAMES.items():
    rs = calc_rolling_sharpe(bt, wc, window=63)
    fig_rs.add_trace(go.Scatter(
        x=bt.index, y=rs, name=name,
        line=dict(color=STRATEGY_COLORS[name], width=1.5),
    ))

fig_rs.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.4)
fig_rs.update_layout(
    yaxis_title="Sharpe Ratio (rolling 63d)",
    xaxis_title="Fecha",
    hovermode="x unified",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
)
style_plotly_chart(fig_rs, height=400)
st.plotly_chart(fig_rs, use_container_width=True)

# ── Mejores y peores días ─────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Mejores y Peores Días</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

best, worst = get_best_worst_days(bt, w_col, n=10)

c1, c2 = st.columns(2)
with c1:
    st.markdown("**Top 10 Mejores Días**")
    best_display = best.copy()
    best_display['Fecha'] = best_display['Fecha'].dt.strftime('%Y-%m-%d')
    st.dataframe(best_display, hide_index=True, use_container_width=True)

with c2:
    st.markdown("**Top 10 Peores Días**")
    worst_display = worst.copy()
    worst_display['Fecha'] = worst_display['Fecha'].dt.strftime('%Y-%m-%d')
    st.dataframe(worst_display, hide_index=True, use_container_width=True)

# Análisis: ¿cuántos de los peores días son eventos macro?
bt_dates_str = set(bt.index.strftime('%Y-%m-%d'))
worst_dates_str = worst['Fecha'].tolist()
worst_eventos = sum(
    1 for d in worst_dates_str
    if d in bt_dates_str and bt.loc[d, 'es_evento'] == 1
)

st.markdown(
    f"""
    <div class="method-note">
        <p>
            De los 10 peores días del período de test,
            <strong>{worst_eventos}</strong> coincidieron con publicaciones
            macroeconómicas, confirmando que los eventos macro son un catalizador
            clave de las pérdidas extremas.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Stress Testing: Períodos de Crisis ──────────────────────────────────────
st.markdown('<div class="section-header"><h3>Stress Test — Períodos de Crisis Históricos</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 12px;">'
    'Rendimiento de cada estrategia durante las principales crisis de mercado. '
    'Muestra retorno acumulado y max drawdown en cada ventana.</p>',
    unsafe_allow_html=True,
)

stress_results = get_stress_test_results(bt)

if stress_results:
    stress_df = pd.DataFrame(stress_results)

    # Mostrar tabla formateada
    display_cols = ['Período', 'Días']
    fmt_dict = {'Días': '{:.0f}'}
    for name in STRATEGY_NAMES:
        short = name.split(':')[-1].strip() if ':' in name else name
        ret_col = f'Ret {short} (%)'
        mdd_col = f'MDD {short} (%)'
        if ret_col in stress_df.columns:
            display_cols.extend([ret_col, mdd_col])
            fmt_dict[ret_col] = '{:+.2f} %'
            fmt_dict[mdd_col] = '{:.2f} %'

    def _stress_color(val):
        if not isinstance(val, (int, float)):
            return ''
        if val > 0:
            return 'color: #059669; font-weight: 700'
        if val < -10:
            return 'color: #DC2626; font-weight: 700'
        if val < 0:
            return 'color: #D97706; font-weight: 700'
        return 'color: #64748B'

    ret_cols = [c for c in display_cols if c.startswith('Ret ')]
    mdd_cols = [c for c in display_cols if c.startswith('MDD ')]
    styled_stress = (
        stress_df[display_cols].style
        .format(fmt_dict)
        .map(_stress_color, subset=ret_cols + mdd_cols)
    )
    st.dataframe(styled_stress, hide_index=True, use_container_width=True)

    st.markdown("""
    <div class="method-note">
        <p>
            <strong>Lectura:</strong> Las estrategias tácticas (Volatilidad,
            Macro y Combinada) limitan las pérdidas en los peores episodios de
            mercado frente al Buy &amp; Hold. La diferencia es más pronunciada
            en crisis con publicaciones macro relevantes (deuda soberana,
            decisiones del BCE). Las estrategias no eliminan las caídas, pero
            reducen la severidad del drawdown.
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.info("No hay períodos de crisis dentro del rango de datos del backtest.")

# ── Conclusión ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Conclusión:</strong> Las estrategias tácticas (B y C) reducen
        tanto el VaR como el CVaR frente al Buy &amp; Hold, acotando el riesgo
        de cola sin necesidad de instrumentos derivados. El rolling Sharpe
        evidencia que las estrategias tácticas mantienen ratios más estables a lo
        largo del tiempo, mientras que el Buy &amp; Hold presenta episodios
        prolongados de Sharpe negativo durante las caídas. El stress test confirma
        que la protección es más efectiva en crisis con componente macroeconómico.
        La recomendación práctica es reducir exposición al 50&nbsp;% en los días
        de evento de alto impacto (PIB y Paro), donde la evidencia estadística
        es más robusta.
    </p>
</div>
""", unsafe_allow_html=True)
