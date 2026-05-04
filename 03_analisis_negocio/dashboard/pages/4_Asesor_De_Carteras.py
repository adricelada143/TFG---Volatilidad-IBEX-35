"""Página 4: Asesor de Carteras — Herramienta prescriptiva para el gestor."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from utils.strategies import (
    analyze_macro_event, get_event_history, calc_exposure,
    get_bonferroni_results,
    ASESOR_VARIABLES, ACCION_COLORS, MACRO_RECOMMENDATIONS,
    style_plotly_chart, load_css,
)

load_css()
st.header("Asesor de Carteras")
st.caption(
    "Selecciona el dato macro que se va a publicar y obtén una recomendación "
    "de exposición basada en evidencia histórica"
)

# ── Selectores ────────────────────────────────────────────────────────────────
col_sel1, col_sel2, col_sel3 = st.columns([2, 1, 1])

with col_sel1:
    var_label = st.selectbox(
        "Variable macro a publicar",
        options=list(ASESOR_VARIABLES.keys()),
        index=0,
    )

with col_sel2:
    dir_label = st.radio(
        "Dirección esperada",
        options=['No sé', 'Sube', 'Baja'],
        horizontal=True,
    )

with col_sel3:
    cartera = st.number_input(
        "Cartera IBEX 35 (€)",
        value=1_000_000,
        step=100_000,
        min_value=10_000,
    )

variable = ASESOR_VARIABLES[var_label]
direction = {'Sube': 'sube', 'Baja': 'baja', 'No sé': None}[dir_label]

# ── Cálculo de exposición ────────────────────────────────────────────────────
exposure = calc_exposure(variable, direction, cartera)

# ── Análisis ──────────────────────────────────────────────────────────────────
analysis = analyze_macro_event(variable, direction)

if analysis is None:
    st.warning("No hay suficientes datos históricos para esta combinación.")
    st.stop()

rec = analysis['recommendation']
color = ACCION_COLORS.get(rec['accion'], '#1f77b4')
tier = rec['tier']
accion_lower = rec['accion'].lower()

# ── Configuración visual por acción ──────────────────────────────────────────
ACTION_CONFIG = {
    'AUMENTAR': {'bg': '#D1FAE5', 'border': '#059669', 'text': '#065F46', 'icon': '📈', 'glow': 'rgba(5,150,105,0.15)'},
    'REDUCIR':  {'bg': '#FEE2E2', 'border': '#DC2626', 'text': '#991B1B', 'icon': '📉', 'glow': 'rgba(220,38,38,0.15)'},
    'CAUTELA':  {'bg': '#FEF3C7', 'border': '#D97706', 'text': '#92400E', 'icon': '⚠️', 'glow': 'rgba(217,119,6,0.15)'},
    'MANTENER': {'bg': '#DBEAFE', 'border': '#2563EB', 'text': '#1E40AF', 'icon': '⚖️', 'glow': 'rgba(37,99,235,0.15)'},
}
ac = ACTION_CONFIG.get(rec['accion'], ACTION_CONFIG['MANTENER'])

TIER_CONFIG = {
    1: {'label': 'Alta confianza', 'bg': '#059669', 'text': '#fff'},
    2: {'label': 'Confianza moderada', 'bg': '#D97706', 'text': '#fff'},
    3: {'label': 'Sin señal accionable', 'bg': '#94A3B8', 'text': '#fff'},
}
tc = TIER_CONFIG[tier]

sig_icon  = '✓' if analysis['p_vol'] < 0.05 else '✗'
sig_color = '#059669' if analysis['p_vol'] < 0.05 else '#94A3B8'
sig_label = 'Significativo' if analysis['p_vol'] < 0.05 else 'No significativo'

dir_arrow = ' ↑' if direction == 'sube' else (' ↓' if direction == 'baja' else '')

# ── Decision Banner ───────────────────────────────────────────────────────────
exp_pct = exposure['exposure_pct']
exp_delta = exposure['delta_eur']
exp_target = exposure['target_eur']
exp_arrow = '→' if exp_pct == 100 else ('↑' if exp_pct > 100 else '↓')
exp_line = f"Ajustar al {exp_pct}%" if exp_pct != 100 else "Mantener exposición actual"

# Colores para la sub-tarjeta de ajuste €
if exp_delta > 0:
    delta_color = '#059669'
    delta_label = f"Comprar {exp_delta:,.0f} €"
elif exp_delta < 0:
    delta_color = '#DC2626'
    delta_label = f"Vender {abs(exp_delta):,.0f} €"
else:
    delta_color = '#64748B'
    delta_label = "Sin ajuste"

# Barra visual de exposición (escala 0-150%)
bar_pct = min(exp_pct / 150 * 100, 100)
bar_color = '#059669' if exp_pct >= 100 else ('#D97706' if exp_pct >= 70 else '#DC2626')

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {ac['bg']} 0%, #ffffff 100%);
    border: 2px solid {ac['border']};
    border-radius: 18px;
    padding: 36px 40px;
    margin: 24px 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 30px {ac['glow']};
">
    <div style="position: absolute; top: -10px; right: 10px; font-size: 9rem; opacity: 0.06; line-height:1; pointer-events:none;">{ac['icon']}</div>
    <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 28px;">
        <div style="flex: 1;">
            <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.14em; color: {ac['border']}; margin-bottom: 8px;">{var_label}{dir_arrow} &nbsp;&mdash;&nbsp; Recomendaci&#243;n t&#225;ctica</div>
            <div style="font-size: 2.6rem; font-weight: 900; color: {ac['text']}; letter-spacing: -0.04em; line-height: 1; margin-bottom: 10px;">{ac['icon']}&nbsp; {rec['accion']} EXPOSICI&#211;N</div>
            <div style="font-size: 0.97rem; color: {ac['text']}; opacity: 0.82; margin-bottom: 6px; line-height: 1.5;">{rec['desc']}</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: {ac['text']}; margin-bottom: 18px;">{exp_arrow} {exp_line}</div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">
                <span style="background: {tc['bg']}; color: {tc['text']}; padding: 5px 14px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em;">T{tier} &nbsp;&middot;&nbsp; {tc['label']}</span>
                <span style="background: rgba(255,255,255,0.7); color: {sig_color}; padding: 5px 14px; border-radius: 20px; border: 1px solid {sig_color}; font-size: 0.68rem; font-weight: 700;">{sig_icon} {sig_label} (p = {analysis['p_vol']:.4f})</span>
            </div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 10px; min-width: 180px;">
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px;
                        padding: 16px 20px; text-align: center; border: 1px solid {ac['border']}30;">
                <div style="font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {ac['border']}; margin-bottom: 4px;">
                    Publicaciones históricas
                </div>
                <div style="font-size: 2rem; font-weight: 900; color: {ac['text']}; line-height: 1;">
                    {analysis['n_events']}
                </div>
                <div style="font-size: 0.68rem; color: {ac['border']}; opacity: 0.75; margin-top: 2px;">
                    desde {analysis['first_year']} &middot; {analysis['n_up']} ↑ / {analysis['n_down']} ↓
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px;
                        padding: 16px 20px; text-align: center; border: 1px solid {ac['border']}30;">
                <div style="font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {ac['border']}; margin-bottom: 4px;">
                    Volatilidad anormal
                </div>
                <div style="font-size: 1.6rem; font-weight: 900; color: {ac['text']}; line-height: 1;">
                    {analysis['vol_ratio']:.2f}x
                </div>
                <div style="font-size: 0.68rem; color: {ac['border']}; opacity: 0.75; margin-top: 2px;">
                    vs. días sin evento
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px;
                        padding: 16px 20px; text-align: center; border: 1px solid {ac['border']}30;">
                <div style="font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {bar_color}; margin-bottom: 4px;">
                    Exposición objetivo
                </div>
                <div style="font-size: 2rem; font-weight: 900; color: {bar_color}; line-height: 1;">
                    {exp_pct}%
                </div>
                <div style="margin-top: 8px; height: 6px; background: #E2E8F0; border-radius: 3px; overflow: hidden;">
                    <div style="height: 100%; width: {bar_pct}%; background: {bar_color}; border-radius: 3px;"></div>
                </div>
            </div>
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px;
                        padding: 16px 20px; text-align: center; border: 1px solid {delta_color}30;">
                <div style="font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {delta_color}; margin-bottom: 4px;">
                    Ajuste recomendado
                </div>
                <div style="font-size: 1.4rem; font-weight: 900; color: {delta_color}; line-height: 1.2;">
                    {delta_label}
                </div>
                <div style="font-size: 0.68rem; color: {delta_color}; opacity: 0.75; margin-top: 2px;">
                    Objetivo: {exp_target:,.0f} €
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tarjetas de impacto en retornos ───────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Impacto histórico en el IBEX 35</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

def _ret_color(v):
    if v > 0.15:  return ('#059669', '#D1FAE5')
    if v < -0.15: return ('#DC2626', '#FEE2E2')
    return ('#64748B', '#F1F5F9')

r1  = analysis['ret_1d_mean']
r5  = analysis['ret_5d_mean']
r21 = analysis['ret_21d_mean']
rvol = (analysis['vol_ratio'] - 1) * 100

metrics_data = [
    ('Retorno día +1',      r1,   analysis['ret_1d_std'],  '%'),
    ('Retorno días 1–5',    r5,   analysis['ret_5d_std'],  '%'),
    ('Retorno días 1–21',   r21,  analysis['ret_21d_std'], '%'),
    ('Vol. extra vs normal', rvol, None,                   '%'),
]

ret_cards = []
for label, val, std, unit in metrics_data:
    txt_col, bg_col = _ret_color(val)
    sign  = '+' if val >= 0 else ''
    bar_w = min(abs(val) * 4, 100)
    std_div = f'<div style="font-size:0.7rem;color:#94A3B8;margin-top:3px;">&#963; {std:.2f}&nbsp;%</div>' if std is not None else ''
    card = (
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:14px;padding:22px 20px;box-shadow:0 2px 8px rgba(0,0,0,0.05);position:relative;overflow:hidden;">'
        f'<div style="position:absolute;top:0;left:0;right:0;height:3px;background:{txt_col};opacity:0.6;"></div>'
        f'<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#64748B;margin-bottom:10px;">{label}</div>'
        f'<div style="font-size:1.6rem;font-weight:900;color:{txt_col};letter-spacing:-0.04em;line-height:1.1;">{sign}{val:.2f}&nbsp;{unit}</div>'
        f'{std_div}'
        f'<div style="margin-top:12px;height:5px;background:#F1F5F9;border-radius:3px;overflow:hidden;">'
        f'<div style="height:100%;width:{bar_w}%;background:{txt_col};border-radius:3px;opacity:0.7;"></div></div>'
        f'</div>'
    )
    ret_cards.append(card)

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:16px 0;">'
    + ''.join(ret_cards)
    + '</div>',
    unsafe_allow_html=True,
)

# ── Mapa de señal — todas las variables ───────────────────────────────────────
st.markdown('<div class="section-header"><h3>Mapa de señal — todas las variables</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 16px;">'
    'Capacidad de señal de cada variable macro (la seleccionada aparece resaltada)</p>',
    unsafe_allow_html=True,
)

# Tier máximo (más favorable) para cada variable
VAR_SIGNAL_MAP = {
    'PIB':            {'var': 'pib_yoy',     'tier': 1, 'icon': '📊', 'best': 'AUMENTAR / REDUCIR'},
    'Tasa de Paro':   {'var': 'tasa_paro',   'tier': 1, 'icon': '👥', 'best': 'AUMENTAR (baja)'},
    'Tipo BCE':       {'var': 'tipo_dfr',    'tier': 1, 'icon': '🏦', 'best': 'REDUCIR (sube)'},
    'IPC':            {'var': 'ipc_yoy',     'tier': 2, 'icon': '🛒', 'best': 'MANTENER'},
    'IPI':            {'var': 'ipi_yoy',     'tier': 3, 'icon': '🏭', 'best': 'Sin señal'},
    'Euríbor':        {'var': 'euribor_3m',  'tier': 3, 'icon': '💶', 'best': 'Sin señal'},
    'IPC Subyacente': {'var': 'ipc_sub_mom', 'tier': 3, 'icon': '📉', 'best': 'Sin señal'},
}

TIER_STYLE = {
    1: {'bg': '#D1FAE5', 'border': '#059669', 'badge_bg': '#059669', 'badge_txt': '#fff',
        'label': 'Alta señal', 'txt': '#065F46'},
    2: {'bg': '#FEF3C7', 'border': '#D97706', 'badge_bg': '#D97706', 'badge_txt': '#fff',
        'label': 'Señal moderada', 'txt': '#92400E'},
    3: {'bg': '#F8FAFC', 'border': '#CBD5E1', 'badge_bg': '#94A3B8', 'badge_txt': '#fff',
        'label': 'Ruido', 'txt': '#64748B'},
}

var_cards = []
for name, cfg in VAR_SIGNAL_MAP.items():
    t  = cfg['tier']
    ts = TIER_STYLE[t]
    is_sel = (ASESOR_VARIABLES.get(name) == variable)
    border  = f"3px solid {ts['border']}" if is_sel else f"1px solid {ts['border']}50"
    shadow  = f"0 6px 20px {ts['border']}30" if is_sel else "0 1px 4px rgba(0,0,0,0.05)"
    scale   = "transform:scale(1.04);" if is_sel else ""
    sel_div = f'<div style="font-size:0.55rem;color:{ts["border"]};font-weight:700;margin-top:4px;">&#9664; SELECCIONADA</div>' if is_sel else ''
    card = (
        f'<div style="background:{ts["bg"]};border:{border};border-radius:14px;padding:18px 12px;text-align:center;box-shadow:{shadow};{scale}transition:all 0.2s ease;">'
        f'<div style="font-size:1.8rem;margin-bottom:8px;line-height:1;">{cfg["icon"]}</div>'
        f'<div style="font-size:0.78rem;font-weight:700;color:{ts["txt"]};margin-bottom:8px;line-height:1.2;">{name}</div>'
        f'<div style="display:inline-block;background:{ts["badge_bg"]};color:{ts["badge_txt"]};padding:3px 10px;border-radius:20px;font-size:0.6rem;font-weight:700;letter-spacing:0.06em;margin-bottom:5px;">T{t}</div>'
        f'<div style="font-size:0.65rem;color:{ts["txt"]};opacity:0.8;line-height:1.3;">{ts["label"]}</div>'
        f'<div style="font-size:0.6rem;color:{ts["txt"]};opacity:0.6;margin-top:4px;">{cfg["best"]}</div>'
        f'{sel_div}'
        f'</div>'
    )
    var_cards.append(card)

st.markdown(
    '<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:10px;margin:16px 0 28px;">'
    + ''.join(var_cards)
    + '</div>',
    unsafe_allow_html=True,
)

# ── Gráfico: comparativa de retornos evento vs normal ─────────────────────────
st.markdown('<div class="section-header"><h3>Retornos acumulados: evento vs. día normal</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

normal_1d  = analysis['normal_1d_series']
normal_21d = analysis['normal_21d_series']
ret_1d_s   = analysis['ret_1d_series']
ret_21d_s  = analysis['ret_21d_series']

fig = go.Figure()

# Distribución días normales (21d)
fig.add_trace(go.Histogram(
    x=normal_21d.values,
    name='Días sin evento (21d)',
    marker_color='#CBD5E1',
    opacity=0.5,
    nbinsx=40,
    legendgroup='normal',
))

# Distribución días de evento (21d)
if len(ret_21d_s) > 2:
    label_dir = (' ↑' if direction == 'sube' else (' ↓' if direction == 'baja' else ''))
    fig.add_trace(go.Histogram(
        x=ret_21d_s.values,
        name=f'Tras {var_label}{label_dir} (21d)',
        marker_color=color,
        opacity=0.8,
        nbinsx=min(20, max(5, len(ret_21d_s) // 2)),
    ))

mean_evt    = analysis['ret_21d_mean']
mean_normal = float(normal_21d.mean()) if len(normal_21d) > 0 else 0

fig.add_vline(x=mean_evt, line_dash='dash', line_color=color, line_width=2,
              annotation_text=f"Media evento: {mean_evt:+.2f} %",
              annotation_position='top left',
              annotation_font_size=11, annotation_font_color=color)
fig.add_vline(x=mean_normal, line_dash='dot', line_color='#94A3B8', line_width=1.5,
              annotation_text=f"Media normal: {mean_normal:+.2f} %",
              annotation_position='top right',
              annotation_font_size=11, annotation_font_color='#94A3B8')

fig.update_layout(
    barmode='overlay',
    xaxis_title='Retorno acumulado 21d (%)',
    yaxis_title='Frecuencia',
    legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99),
)
style_plotly_chart(fig, height=400)
st.plotly_chart(fig, use_container_width=True)

# ── Historial de publicaciones ────────────────────────────────────────────────
st.markdown(f'<div class="section-header"><h3>Últimas publicaciones: {var_label}</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

history = get_event_history(variable, n=15)
if not history.empty:
    def _color_ret(val):
        if not isinstance(val, (int, float)):
            return ''
        if val > 0.5:  return 'color: #059669; font-weight: 700'
        if val < -0.5: return 'color: #DC2626; font-weight: 700'
        return 'color: #64748B'

    def _color_dir(val):
        v = str(val)
        if '↑' in v: return 'color: #059669; font-weight: 700'
        if '↓' in v: return 'color: #DC2626; font-weight: 700'
        return 'color: #94A3B8'

    styled = (
        history.style
        .format({
            'Valor':       '{:.2f}',
            'Cambio':      '{:+.3f}',
            'Ret. día (%)': '{:+.2f}',
            'Ret. 5d (%)': '{:+.2f}',
            'Ret. 21d (%)': '{:+.2f}',
        })
        .map(_color_ret,  subset=['Ret. día (%)', 'Ret. 5d (%)', 'Ret. 21d (%)'])
        .map(_color_dir,  subset=['Dirección'])
    )
    st.dataframe(styled, hide_index=True, use_container_width=True)
else:
    st.info("No hay historial disponible para esta variable.")

# ── Corrección por pruebas múltiples (Bonferroni) ───────────────────────────
st.markdown('<div class="section-header"><h3>Robustez: Corrección de Bonferroni</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

bonf_results = get_bonferroni_results()
if bonf_results:
    n_tests = bonf_results[0]['n_tests']
    st.markdown(
        f'<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 12px;">'
        f'Se realizan <strong>{n_tests} tests</strong> (7 variables × 2 direcciones). '
        f'La corrección de Bonferroni multiplica cada p-valor por {n_tests} para '
        f'controlar la tasa de falsos positivos (FWER). Solo las variables que '
        f'mantienen significación tras la corrección se consideran señales robustas.</p>',
        unsafe_allow_html=True,
    )

    bonf_rows = []
    for r in bonf_results:
        dir_icon = '↑' if r['direction'] == 'sube' else '↓'
        sig_raw = '✓' if r['sig_raw'] else '✗'
        sig_corr = '✓' if r['sig_corrected'] else '✗'
        bonf_rows.append({
            'Variable': f"{r['label']} {dir_icon}",
            'Tier': f"T{r['tier']}",
            'N eventos': r['n_events'],
            'Vol ratio': round(r['vol_ratio'], 2),
            'p bruto': round(r['p_raw'], 4),
            'p Bonferroni': round(r['p_bonferroni'], 4),
            'Sig. bruta': sig_raw,
            'Sig. corregida': sig_corr,
        })

    bonf_df = pd.DataFrame(bonf_rows)

    def _sig_style(val):
        if val == '✓':
            return 'color: #059669; font-weight: 700'
        if val == '✗':
            return 'color: #DC2626; font-weight: 700'
        return ''

    styled_bonf = bonf_df.style.map(_sig_style, subset=['Sig. bruta', 'Sig. corregida'])
    st.dataframe(styled_bonf, hide_index=True, use_container_width=True)

    n_sig_raw = sum(1 for r in bonf_results if r['sig_raw'])
    n_sig_corr = sum(1 for r in bonf_results if r['sig_corrected'])
    st.markdown(
        f'<div class="method-note"><p>'
        f'<strong>Resultado:</strong> {n_sig_raw}/{n_tests} combinaciones son '
        f'significativas sin corrección (p &lt; 0.05), y '
        f'<strong>{n_sig_corr}/{n_tests}</strong> mantienen significación tras '
        f'Bonferroni. Las variables Tier 1 (PIB, Paro, Tipo BCE) son las más '
        f'robustas, validando la clasificación por tiers del Asesor.'
        f'</p></div>',
        unsafe_allow_html=True,
    )

# ── Nota metodológica ─────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="method-note">
        <p>
            <strong>Metodología:</strong> Análisis basado en
            <strong>{analysis['n_events']} eventos</strong> históricos desde
            {analysis['first_year']} ({analysis['n_up']} subidas,
            {analysis['n_down']} bajadas). Retornos forward calculados como
            log-retornos acumulados a 1, 5 y 21 días hábiles tras la publicación.
            Significación estadística evaluada mediante test de Mann-Whitney U
            con <strong>corrección de Bonferroni</strong> para {n_tests if bonf_results else 14}
            pruebas múltiples. Los retornos pasados no garantizan resultados futuros.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Limitaciones ─────────────────────────────────────────────────────────────
with st.expander("Limitaciones y supuestos"):
    st.markdown("""
    **Limitaciones metodológicas:**
    - **Tamaño muestral:** Las publicaciones macro son trimestrales/mensuales,
      lo que limita el número de eventos por variable (15-80 observaciones por
      dirección). Los resultados deben interpretarse como guías probabilísticas.
    - **Correlación ≠ Causalidad:** La relación observada entre publicaciones y
      retornos no implica causalidad directa. Puede haber variables omitidas
      (sentimiento de mercado, posicionamiento institucional).
    - **Estabilidad temporal:** Las recomendaciones se basan en datos desde 2005.
      Los regímenes de mercado cambian y las relaciones históricas pueden no
      mantenerse en el futuro.
    - **Costes no modelados:** El Asesor no descuenta costes de transacción ni
      impacto de mercado al ejecutar los ajustes de exposición recomendados.
    - **Exposiciones heurísticas:** Los niveles de exposición (50%, 80%, 100%,
      110%, 120%) son heurísticos basados en la evidencia empírica, no óptimos
      matemáticos derivados de maximización de utilidad.
    """)

# ── Conclusión prescriptiva ──────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Conclusión:</strong> El Asesor de Carteras demuestra que no todas
        las variables macroeconómicas tienen la misma capacidad de señal. El
        <strong>PIB</strong>, la <strong>Tasa de paro</strong> y el
        <strong>Tipo BCE</strong> generan reacciones estadísticamente significativas
        y direccionalmente consistentes (Tier 1), incluso tras corrección de
        Bonferroni, mientras que el IPI, Euríbor e IPC subyacente se comportan
        como ruido (Tier 3). Desde el punto de vista prescriptivo, el gestor
        debería concentrar su atención en las 3 variables de alta señal y ajustar
        la exposición solo cuando la dirección del dato confirme un escenario
        históricamente adverso. La principal limitación es el tamaño muestral
        (frecuencia trimestral/mensual de las publicaciones), que impone prudencia:
        las recomendaciones deben interpretarse como guías probabilísticas, no como
        reglas deterministas.
    </p>
</div>
""", unsafe_allow_html=True)
