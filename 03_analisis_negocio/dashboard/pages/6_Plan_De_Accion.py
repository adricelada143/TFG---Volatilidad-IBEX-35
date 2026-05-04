"""Página 6: Plan de Acción Táctico — Hoja de ruta personalizada con fechas, exposición y € concretos."""
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from utils.strategies import (
    run_backtest, get_current_signal, get_upcoming_events,
    analyze_macro_event, calc_exposure,
    compute_composite_risk_score, generate_action_calendar,
    detect_event_clusters, build_scenario_table,
    INVESTOR_PROFILES, MACRO_EVENT_LABELS, ACCION_COLORS,
    EXPOSURE_PCT,
    style_plotly_chart, load_css,
)

load_css()
st.header("Plan de Acción Táctico")
st.caption(
    "Tu hoja de ruta personalizada: fechas, exposición y € concretos "
    "fusionando volatilidad, eventos macro y perfil de inversor"
)

# ── Datos base ───────────────────────────────────────────────────────────────
bt = run_backtest()
signal = get_current_signal(bt)
upcoming = get_upcoming_events()

# ── Inputs ───────────────────────────────────────────────────────────────────
col_in1, col_in2, col_in3 = st.columns(3)

with col_in1:
    profile = st.select_slider(
        "Perfil de inversor",
        options=['Conservador', 'Moderado', 'Agresivo'],
        value='Moderado',
    )

with col_in2:
    portfolio_eur = st.number_input(
        "Cartera IBEX 35 (€)",
        value=1_000_000,
        step=100_000,
        min_value=10_000,
    )

with col_in3:
    lookahead = st.select_slider(
        "Horizonte (días hábiles)",
        options=[7, 14, 30],
        value=30,
    )

prof = INVESTOR_PROFILES[profile]

# ── Sección 1: SITREP Banner ────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>SITREP — Situación de Riesgo</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

risk = compute_composite_risk_score(signal, upcoming, window_days=lookahead)

if risk['risk_level'] == 'Bajo':
    sitrep_color = '#059669'
    sitrep_bg = '#D1FAE5'
    sitrep_text = '#065F46'
    sitrep_glow = 'rgba(5,150,105,0.15)'
elif risk['risk_level'] == 'Medio':
    sitrep_color = '#D97706'
    sitrep_bg = '#FEF3C7'
    sitrep_text = '#92400E'
    sitrep_glow = 'rgba(217,119,6,0.15)'
else:
    sitrep_color = '#DC2626'
    sitrep_bg = '#FEE2E2'
    sitrep_text = '#991B1B'
    sitrep_glow = 'rgba(220,38,38,0.15)'

score_bar_pct = min(risk['score'], 100)

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {sitrep_bg} 0%, #ffffff 100%);
    border: 2px solid {sitrep_color};
    border-radius: 18px;
    padding: 32px 36px;
    margin: 0 0 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 30px {sitrep_glow};
">
    <div style="display: flex; align-items: center; justify-content: space-between; gap: 28px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 300px;">
            <div style="font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: 0.12em; color: {sitrep_color}; margin-bottom: 8px;">
                Composite Risk Score &nbsp;&middot;&nbsp; Perfil {profile} {prof['icon']}
            </div>
            <div style="display: flex; align-items: baseline; gap: 16px; margin-bottom: 10px;">
                <div style="font-size: 3.2rem; font-weight: 900; color: {sitrep_text}; line-height: 1;
                            letter-spacing: -0.04em;">
                    {risk['score']:.0f}
                </div>
                <div style="font-size: 1.3rem; font-weight: 800; color: {sitrep_color};">
                    / 100 &nbsp;&mdash;&nbsp; RIESGO {risk['risk_level'].upper()}
                </div>
            </div>
            <div style="height: 8px; background: #E2E8F0; border-radius: 4px; overflow: hidden; margin-bottom: 14px; max-width: 400px;">
                <div style="height: 100%; width: {score_bar_pct}%; background: {sitrep_color}; border-radius: 4px;
                            transition: width 0.3s ease;"></div>
            </div>
            <div style="font-size: 0.88rem; color: {sitrep_text}; line-height: 1.5;">
                {risk['summary']}
            </div>
        </div>
        <div style="display: flex; gap: 12px;">
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px; padding: 14px 18px;
                        text-align: center; border: 1px solid {sitrep_color}30; min-width: 100px;">
                <div style="font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {sitrep_color}; margin-bottom: 4px;">Componente Vol</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: {sitrep_text}; line-height: 1;">
                    {risk['vol_component']:.0f}</div>
                <div style="font-size: 0.65rem; color: {sitrep_color}; opacity: 0.7; margin-top: 2px;">/ 50</div>
            </div>
            <div style="background: rgba(255,255,255,0.75); border-radius: 12px; padding: 14px 18px;
                        text-align: center; border: 1px solid {sitrep_color}30; min-width: 100px;">
                <div style="font-size: 0.55rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.1em; color: {sitrep_color}; margin-bottom: 4px;">Componente Eventos</div>
                <div style="font-size: 1.6rem; font-weight: 900; color: {sitrep_text}; line-height: 1;">
                    {risk['event_component']:.0f}</div>
                <div style="font-size: 0.65rem; color: {sitrep_color}; opacity: 0.7; margin-top: 2px;">/ 50</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sección 2: Acción de Hoy ────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Acción de Hoy</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

calendar_df = generate_action_calendar(
    signal, upcoming, portfolio_eur, profile, lookahead)

if len(calendar_df) > 0:
    today_row = calendar_df.iloc[0]
    today_exposure = today_row['exposure_pct']
    today_action = today_row['action']
    today_delta = today_row['delta_eur']
    today_reasoning = today_row['reasoning']
    today_events = today_row['events']

    # Buscar próxima fecha donde la acción cambie
    next_change = None
    for _, row in calendar_df.iloc[1:].iterrows():
        if row['exposure_pct'] != today_exposure:
            next_change = row['date']
            break
    next_change_text = (next_change.strftime('%d/%m/%Y')
                        if next_change is not None else 'Sin cambios previstos')

    # Config visual
    ACTION_CFG = {
        'MANTENER': {'bg': '#DBEAFE', 'border': '#2563EB', 'text': '#1E40AF',
                     'icon': '⚖️', 'glow': 'rgba(37,99,235,0.15)'},
        'CAUTELA':  {'bg': '#FEF3C7', 'border': '#D97706', 'text': '#92400E',
                     'icon': '⚠️', 'glow': 'rgba(217,119,6,0.15)'},
        'REDUCIR':  {'bg': '#FEE2E2', 'border': '#DC2626', 'text': '#991B1B',
                     'icon': '📉', 'glow': 'rgba(220,38,38,0.15)'},
    }
    ac = ACTION_CFG.get(today_action, ACTION_CFG['MANTENER'])

    if today_delta < 0:
        delta_label = f"Vender {abs(today_delta):,.0f} €"
        delta_color = '#DC2626'
    elif today_delta > 0:
        delta_label = f"Comprar {today_delta:,.0f} €"
        delta_color = '#059669'
    else:
        delta_label = "Sin cambios"
        delta_color = '#64748B'

    bar_pct = min(today_exposure / 150 * 100, 100)
    bar_color = '#059669' if today_exposure >= 100 else (
        '#D97706' if today_exposure >= 70 else '#DC2626')

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {ac['bg']} 0%, #ffffff 100%);
        border: 2px solid {ac['border']};
        border-radius: 18px;
        padding: 36px 40px;
        margin: 0 0 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 30px {ac['glow']};
    ">
        <div style="position: absolute; top: -10px; right: 10px; font-size: 9rem;
                    opacity: 0.06; line-height: 1; pointer-events: none;">{ac['icon']}</div>
        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 28px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 300px;">
                <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.14em; color: {ac['border']}; margin-bottom: 8px;">
                    {signal['fecha'].strftime('%d/%m/%Y')} &nbsp;&mdash;&nbsp; Recomendaci&#243;n t&#225;ctica
                </div>
                <div style="font-size: 2.6rem; font-weight: 900; color: {ac['text']};
                            letter-spacing: -0.04em; line-height: 1; margin-bottom: 10px;">
                    {ac['icon']}&nbsp; {today_action} &mdash; {today_exposure}%
                </div>
                <div style="font-size: 0.95rem; color: {ac['text']}; opacity: 0.82;
                            margin-bottom: 6px; line-height: 1.5;">
                    {today_reasoning}
                </div>
                <div style="font-size: 0.82rem; color: {ac['text']}; opacity: 0.65; margin-top: 10px;">
                    Pr&#243;xima fecha de acci&#243;n: <strong>{next_change_text}</strong>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; min-width: 180px;">
                <div style="background: rgba(255,255,255,0.75); border-radius: 12px;
                            padding: 16px 20px; text-align: center; border: 1px solid {ac['border']}30;">
                    <div style="font-size: 0.58rem; font-weight: 700; text-transform: uppercase;
                                letter-spacing: 0.1em; color: {bar_color}; margin-bottom: 4px;">
                        Exposici&#243;n objetivo
                    </div>
                    <div style="font-size: 2rem; font-weight: 900; color: {bar_color}; line-height: 1;">
                        {today_exposure}%
                    </div>
                    <div style="margin-top: 8px; height: 6px; background: #E2E8F0;
                                border-radius: 3px; overflow: hidden;">
                        <div style="height: 100%; width: {bar_pct}%; background: {bar_color};
                                    border-radius: 3px;"></div>
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
                        Objetivo: {portfolio_eur * today_exposure / 100:,.0f} &euro;
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Sección 3: Calendario de Acción ─────────────────────────────────────────
st.markdown(f'<div class="section-header"><h3>Calendario de Acción — {lookahead} días</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

if len(calendar_df) > 0:
    fig_cal = go.Figure()

    # Barras de exposición coloreadas
    colors_bar = []
    for _, row in calendar_df.iterrows():
        pct = row['exposure_pct']
        if pct >= 100:
            colors_bar.append('#059669')
        elif pct >= 70:
            colors_bar.append('#D97706')
        else:
            colors_bar.append('#DC2626')

    fig_cal.add_trace(go.Bar(
        x=calendar_df['date'],
        y=calendar_df['exposure_pct'],
        marker_color=colors_bar,
        name='Exposición %',
        hovertemplate='%{x|%d/%m}<br>Exposición: %{y}%<extra></extra>',
        opacity=0.85,
    ))

    # Marcadores scatter para eventos
    event_rows = calendar_df[calendar_df['events'] != '—']
    if len(event_rows) > 0:
        fig_cal.add_trace(go.Scatter(
            x=event_rows['date'],
            y=event_rows['exposure_pct'] + 5,
            mode='markers+text',
            marker=dict(
                size=12,
                color='#DC2626',
                symbol='diamond',
                line=dict(width=1, color='#fff'),
            ),
            text=['📅'] * len(event_rows),
            textposition='top center',
            name='Evento macro',
            hovertemplate=(
                '%{x|%d/%m/%Y}<br>'
                '%{customdata}<extra>Evento</extra>'
            ),
            customdata=event_rows['events'].values,
        ))

    fig_cal.add_hline(
        y=100, line_dash='dot', line_color='#94A3B8', line_width=1,
        annotation_text='100% (plena inversión)',
        annotation_position='bottom right',
        annotation_font_size=10,
        annotation_font_color='#94A3B8',
    )

    fig_cal.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Exposición (%)',
        yaxis=dict(range=[0, 130]),
        showlegend=True,
        legend=dict(yanchor='top', y=0.99, xanchor='right', x=0.99),
        hovermode='x unified',
    )
    style_plotly_chart(fig_cal, height=400)
    st.plotly_chart(fig_cal, use_container_width=True)

    # Tabla detallada
    display_df = calendar_df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
    display_df['delta_eur'] = display_df['delta_eur'].apply(
        lambda x: f"{x:+,.0f} €" if x != 0 else "—")
    display_df['exposure_pct'] = display_df['exposure_pct'].apply(lambda x: f"{x}%")

    display_df = display_df.rename(columns={
        'date': 'Fecha',
        'events': 'Evento(s)',
        'vol_signal': 'Señal Vol',
        'score': 'Score',
        'exposure_pct': 'Exposición %',
        'action': 'Acción',
        'delta_eur': 'Importe €',
        'reasoning': 'Razonamiento',
    })

    st.dataframe(
        display_df[['Fecha', 'Evento(s)', 'Señal Vol', 'Exposición %',
                     'Acción', 'Importe €', 'Razonamiento']],
        hide_index=True,
        use_container_width=True,
    )

# ── Sección 4: Alertas de Clustering ────────────────────────────────────────
clusters = detect_event_clusters(upcoming, cluster_window=5)

if clusters:
    st.markdown('<div class="section-header"><h3>Alertas de Clustering</h3>'
                '<div class="section-line"></div></div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#64748B; font-size:0.85rem; margin:-4px 0 16px;">'
        '2 o más eventos en una ventana de 5 días hábiles amplifican el riesgo '
        '(exposición multiplicativa)</p>',
        unsafe_allow_html=True,
    )

    for cluster in clusters:
        c_exp = cluster['combined_exposure_pct']
        if c_exp < 60:
            cl_color = '#DC2626'
            cl_bg = '#FEE2E2'
            cl_text = '#991B1B'
            cl_icon = '🔴'
        else:
            cl_color = '#D97706'
            cl_bg = '#FEF3C7'
            cl_text = '#92400E'
            cl_icon = '🟡'

        event_labels = [e['label'] for e in cluster['events']]
        event_tiers = [f"T{e['tier']}" for e in cluster['events']]
        event_list = ' + '.join(
            [f"{l} ({t})" for l, t in zip(event_labels, event_tiers)])

        # Mostrar cálculo multiplicativo
        pcts = []
        for evt in cluster['events']:
            pct = EXPOSURE_PCT.get((evt['accion'], evt['tier']), 100)
            pcts.append(str(pct))
        calc_str = ' × '.join([f"{p}%" for p in pcts]) + f" / {'100 ' * (len(pcts) - 1)}= {c_exp:.0f}%"

        delta_cluster = portfolio_eur * (c_exp / 100) - portfolio_eur

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {cl_bg} 0%, #ffffff 100%);
            border: 2px solid {cl_color};
            border-radius: 14px;
            padding: 24px 28px;
            margin: 0 0 16px;
            box-shadow: 0 4px 16px {cl_color}20;
        ">
            <div style="display: flex; align-items: flex-start; gap: 16px;">
                <div style="font-size: 2rem; line-height: 1;">{cl_icon}</div>
                <div style="flex: 1;">
                    <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
                                letter-spacing: 0.12em; color: {cl_color}; margin-bottom: 6px;">
                        Clustering detectado &nbsp;&middot;&nbsp;
                        {cluster['start_date'].strftime('%d/%m')} – {cluster['end_date'].strftime('%d/%m/%Y')}
                    </div>
                    <div style="font-size: 1rem; font-weight: 700; color: {cl_text}; margin-bottom: 8px;">
                        {event_list}
                    </div>
                    <div style="font-size: 0.85rem; color: {cl_text}; margin-bottom: 8px;">
                        Exposici&#243;n combinada (multiplicativa): <strong>{c_exp:.0f}%</strong>
                        &nbsp;&mdash;&nbsp; {calc_str}
                    </div>
                    <div style="font-size: 0.82rem; color: {cl_text}; opacity: 0.8;">
                        Ajuste: <strong style="color: {cl_color};">{delta_cluster:+,.0f} &euro;</strong>
                        &nbsp;&middot;&nbsp;
                        El clustering amplifica el riesgo porque m&#250;ltiples fuentes de incertidumbre
                        coinciden en el tiempo, reduciendo la capacidad de reacci&#243;n del gestor.
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Sección 5: Escenarios del Próximo Evento Clave ──────────────────────────
key_events = [e for e in upcoming if e['tier'] <= 2]

if key_events:
    next_evt = key_events[0]
    st.markdown(
        f'<div class="section-header">'
        f'<h3>Escenarios — {next_evt["label"]} '
        f'({next_evt["next_date"].strftime("%d/%m/%Y")})</h3>'
        f'<div class="section-line"></div></div>', unsafe_allow_html=True)

    scenarios = build_scenario_table(next_evt, portfolio_eur)

    col_s1, col_s2, col_s3 = st.columns(3)

    # Escenario SUBE
    with col_s1:
        s = scenarios.get('sube')
        if s:
            s_color = '#059669' if s['ret_21d_mean'] >= 0 else '#D97706'
            s_delta = s['delta_eur']
            s_delta_label = (f"Comprar {s_delta:,.0f} €" if s_delta > 0
                             else (f"Vender {abs(s_delta):,.0f} €" if s_delta < 0
                                   else "Sin ajuste"))
            st.markdown(f"""
            <div style="background: #D1FAE5; border: 2px solid #059669; border-radius: 14px;
                        padding: 24px; height: 100%;">
                <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.12em; color: #059669; margin-bottom: 10px;">
                    &#9650; Si sube</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #065F46; line-height: 1;
                            margin-bottom: 8px;">{s['exposure_pct']}%</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #065F46;
                            margin-bottom: 12px;">{s['accion']} &mdash; {s_delta_label}</div>
                <div style="font-size: 0.78rem; color: #065F46; line-height: 1.5;">
                    Ret. medio 21d: <strong>{s['ret_21d_mean']:+.2f}%</strong><br>
                    Ret. medio 1d: <strong>{s['ret_1d_mean']:+.2f}%</strong><br>
                    Eventos hist&#243;ricos: <strong>{s['n_events']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sin datos históricos para 'sube'")

    # Escenario BAJA
    with col_s2:
        s = scenarios.get('baja')
        if s:
            s_delta = s['delta_eur']
            s_delta_label = (f"Comprar {s_delta:,.0f} €" if s_delta > 0
                             else (f"Vender {abs(s_delta):,.0f} €" if s_delta < 0
                                   else "Sin ajuste"))
            st.markdown(f"""
            <div style="background: #FEE2E2; border: 2px solid #DC2626; border-radius: 14px;
                        padding: 24px; height: 100%;">
                <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.12em; color: #DC2626; margin-bottom: 10px;">
                    &#9660; Si baja</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #991B1B; line-height: 1;
                            margin-bottom: 8px;">{s['exposure_pct']}%</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #991B1B;
                            margin-bottom: 12px;">{s['accion']} &mdash; {s_delta_label}</div>
                <div style="font-size: 0.78rem; color: #991B1B; line-height: 1.5;">
                    Ret. medio 21d: <strong>{s['ret_21d_mean']:+.2f}%</strong><br>
                    Ret. medio 1d: <strong>{s['ret_1d_mean']:+.2f}%</strong><br>
                    Eventos hist&#243;ricos: <strong>{s['n_events']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sin datos históricos para 'baja'")

    # Escenario NO ACTÚO
    with col_s3:
        s = scenarios.get('no_action')
        if s:
            var_label = f"{abs(s['var_95']):.2f}" if s['var_95'] != 0 else 'N/D'
            st.markdown(f"""
            <div style="background: #F1F5F9; border: 2px solid #94A3B8; border-radius: 14px;
                        padding: 24px; height: 100%;">
                <div style="font-size: 0.62rem; font-weight: 700; text-transform: uppercase;
                            letter-spacing: 0.12em; color: #64748B; margin-bottom: 10px;">
                    &#9724; Si no act&#250;o (Buy &amp; Hold)</div>
                <div style="font-size: 1.8rem; font-weight: 900; color: #334155; line-height: 1;
                            margin-bottom: 8px;">100%</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #334155;
                            margin-bottom: 12px;">Sin ajuste &mdash; 0 &euro;</div>
                <div style="font-size: 0.78rem; color: #475569; line-height: 1.5;">
                    Ret. medio 21d: <strong>{s['ret_21d_mean']:+.2f}%</strong><br>
                    Ret. medio 1d: <strong>{s['ret_1d_mean']:+.2f}%</strong><br>
                    VaR 95% (d&#237;a evento): <strong>-{var_label}%</strong><br>
                    Eventos hist&#243;ricos: <strong>{s['n_events']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sin datos históricos para escenario neutral")

# ── Nota metodológica ────────────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Metodología:</strong> El Plan de Acción Táctico fusiona tres fuentes de señal:
        (1) el <strong>percentil de volatilidad predicha</strong> por el modelo XGBoost-HAR,
        (2) el <strong>calendario de eventos macro</strong> con tiers de impacto (T1/T2/T3), y
        (3) el <strong>perfil del inversor</strong> (Conservador/Moderado/Agresivo).
        La exposición diaria es el mínimo entre la señal de volatilidad y la señal de eventos.
        El perfil Conservador extiende la ventana de eventos ±1 día; el Agresivo ignora T3.
        El clustering usa exposición <strong>multiplicativa</strong> (no mínimo simple)
        para capturar la amplificación de riesgo por coincidencia temporal.
        Los escenarios se basan en retornos forward históricos
        (log-retornos acumulados a 1d y 21d). <strong>Los retornos pasados no garantizan
        resultados futuros.</strong>
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("Limitaciones y supuestos"):
    st.markdown("""
- **Sin costes de transacción integrados**: las acciones diarias (comprar/vender) no
  descuentan comisiones, spreads ni impacto de mercado. En carteras grandes, el coste
  de rotación diaria podría erosionar el alpha táctico. Véase la Página 1 para un
  análisis del impacto de costes de transacción.
- **Liquidez asumida**: se asume que el IBEX 35 puede ajustarse al % indicado de forma
  instantánea. En la práctica, posiciones grandes requerirían ejecución gradual (TWAP/VWAP).
- **Exposición uniforme**: se modela una cartera IBEX 35 como un único activo agregado,
  sin descomposición por sectores ni valores individuales.
- **Calendario macro estático**: los eventos se basan en un calendario histórico fijo.
  Eventos imprevistos (cisnes negros, convocatorias extraordinarias) no están contemplados.
- **Perfil inversor simplificado**: tres perfiles discretos no capturan el espectro
  completo de tolerancia al riesgo, horizonte y restricciones regulatorias de cada cliente.
- **Clustering multiplicativo**: la fórmula de exposición combinada asume independencia
  entre eventos. Eventos correlacionados (p. ej. reunión BCE + dato IPC eurozona)
  podrían requerir un modelo de correlación explícito.
- **No sustituye el juicio profesional**: esta herramienta es un apoyo analítico,
  no una recomendación de inversión regulada (MiFID II).
""")

