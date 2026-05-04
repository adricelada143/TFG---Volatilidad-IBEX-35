"""
Dashboard de Análisis de Negocio — Gestión Táctica de Carteras IBEX 35
TFG: Impacto de las variables macroeconómicas en la volatilidad del IBEX 35
Autor: Adrián Celada Calderón — UFV, Business Analytics 2025-26

Ejecutar: streamlit run app.py
"""
import streamlit as st
import os

from utils.strategies import get_landing_kpis

st.set_page_config(
    page_title="Gestión Táctica IBEX 35 — TFG Adrián Celada",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar CSS custom
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Gestión Táctica de Carteras IBEX 35</h1>
    <p class="hero-sub">
        Impacto de las variables macroeconómicas en la volatilidad del IBEX 35<br>
        Adrián Celada Calderón &middot; Business Analytics &middot;
        Universidad Francisco de Vitoria &middot; 2025-26
    </p>
</div>
""", unsafe_allow_html=True)

# ── KPI Strip (dinámico) ──────────────────────────────────────────────────────
kpis = get_landing_kpis()

st.markdown(f"""
<div class="kpi-strip">
    <div class="kpi-card">
        <div class="kpi-label">Volatilidad anormal</div>
        <div class="kpi-value">+{kpis['vol_ratio']:.1f} %</div>
        <div class="kpi-detail">en días de publicación macro<br>(Mann-Whitney, p &asymp; 0)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Modelo XGBoost-HAR</div>
        <div class="kpi-value">RMSE {kpis['rmse']:.3f}</div>
        <div class="kpi-detail">predicción de volatilidad<br>split temporal 80/20</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Mejor Sharpe</div>
        <div class="kpi-value">{kpis['best_strategy']}</div>
        <div class="kpi-detail">estrategia con mayor ratio<br>rentabilidad-riesgo</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Coste de implementación</div>
        <div class="kpi-value">{kpis['cost']} &euro;</div>
        <div class="kpi-detail">basado en información<br>pública y gratuita</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Contenido ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header"><h3>Objetivo</h3>'
                '<div class="section-line"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    Esta herramienta permite a un **gestor de carteras** tomar decisiones
    tácticas de exposición al IBEX 35 combinando tres fuentes de señal:

    1. **Asesor de Carteras** — recomendación prescriptiva por variable
       macro publicada (PIB, paro, tipo BCE, IPC…)
    2. **Predicción de volatilidad** — modelo XGBoost-HAR que señala
       regímenes de alta volatilidad en tiempo real
    3. **Señal combinada** — fusión de ambas fuentes para máxima
       convicción en la toma de decisiones
    """)

with col2:
    st.markdown('<div class="section-header"><h3>Metodología</h3>'
                '<div class="section-line"></div></div>', unsafe_allow_html=True)
    st.markdown("""
    - **Datos:** IBEX 35 (índice sintético equiponderado) + 7 variables
      macro del INE, BCE y Eurostat (2005-2025)
    - **Modelo:** XGBoost-HAR con 15 features (3 HAR + 12 macro/mercado),
      split temporal 80/20, validación TimeSeriesSplit
    - **Señales macro:** Retornos forward a 1d, 5d y 21d tras cada
      publicación, test de significación Mann-Whitney U
    - **Backtesting:** 4 estrategias con métricas estándar (Sharpe,
      drawdown, VaR/CVaR, Calmar)
    """)

# ── Objetivos de investigación ────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Objetivos de investigación</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
            'Cada pregunta del TFG se responde en una sección específica del dashboard</p>',
            unsafe_allow_html=True)

st.markdown("""
<div class="method-note" style="margin-bottom:1rem;">
    <p>
        <strong>Q1. ¿Es predecible la volatilidad del IBEX 35?</strong><br>
        <em>Sí.</em> El modelo XGBoost-HAR alcanza un ajuste elevado (R² > 0.96).
        &rarr; <strong>Página 5</strong> (Predictor: evolución predicha vs. real)
    </p>
    <p style="margin-top:0.75rem;">
        <strong>Q2. ¿Qué modelo ofrece mejor pronóstico?</strong><br>
        <em>XGBoost</em> obtiene el menor RMSE frente a los benchmarks HAR puros.
        &rarr; <strong>Página 5</strong> (Feature importance) y <strong>Página 1</strong> (métricas comparativas)
    </p>
    <p style="margin-top:0.75rem;">
        <strong>Q3. ¿Añaden valor las variables macroeconómicas?</strong><br>
        <em>Sí, marginal pero accionable.</em> El calendario macro permite reducir exposición
        en días de alta incertidumbre con coste mínimo en rentabilidad.
        &rarr; <strong>Página 4</strong> (Asesor de Carteras) y <strong>Página 2</strong> (Estrategias)
    </p>
</div>
""", unsafe_allow_html=True)

# ── Aportación original ──────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Aportación original</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)

st.markdown("""
<div class="method-note" style="margin-bottom:1rem;">
    <p>
        La contribución diferencial de este TFG es la <strong>señal combinada
        XGBoost + calendario macro</strong> como herramienta prescriptiva para el
        gestor de carteras. A diferencia de los modelos de volatilidad tradicionales
        (GARCH, HAR), esta propuesta:
    </p>
    <ul style="margin:0.5rem 0 0 1.2rem; color:#334155;">
        <li>Fusiona predicción cuantitativa (ML) con información cualitativa
            (calendario de eventos)</li>
        <li>Traduce la predicción en una <strong>señal accionable</strong>
            (semáforo + recomendación de exposición)</li>
        <li>Demuestra que la información pública y gratuita genera valor
            táctico medible (menor VaR/CVaR con coste mínimo en rentabilidad)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# ── Navegación ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header"><h3>Navegación</h3>'
            '<div class="section-line"></div></div>', unsafe_allow_html=True)
st.markdown('<p style="color:#64748B; font-size:0.9rem; margin-top:-0.5rem;">'
            'Usa el menú lateral para acceder a cada sección</p>',
            unsafe_allow_html=True)

st.markdown("""
<div class="nav-grid">
    <div class="nav-card">
        <div class="nav-icon">📈</div>
        <div class="nav-num">Página 1</div>
        <div class="nav-title">Resumen Ejecutivo</div>
        <div class="nav-desc">KPIs, equity curves y tabla comparativa de las 4 estrategias</div>
    </div>
    <div class="nav-card">
        <div class="nav-icon">⚖️</div>
        <div class="nav-num">Página 2</div>
        <div class="nav-title">Estrategias</div>
        <div class="nav-desc">Comparativa interactiva con filtros temporales y scatter riesgo-retorno</div>
    </div>
    <div class="nav-card">
        <div class="nav-icon">🛡️</div>
        <div class="nav-num">Página 3</div>
        <div class="nav-title">Análisis de Riesgo</div>
        <div class="nav-desc">Drawdown, VaR/CVaR, rolling Sharpe y mejores/peores días</div>
    </div>
    <div class="nav-card">
        <div class="nav-icon">🧭</div>
        <div class="nav-num">Página 4</div>
        <div class="nav-title">Asesor de Carteras</div>
        <div class="nav-desc">Recomendación prescriptiva por variable macro con evidencia histórica</div>
    </div>
    <div class="nav-card">
        <div class="nav-icon">🚦</div>
        <div class="nav-num">Página 5</div>
        <div class="nav-title">Predictor</div>
        <div class="nav-desc">Semáforo de riesgo y señal combinada volatilidad + macro</div>
    </div>
    <div class="nav-card">
        <div class="nav-icon">📋</div>
        <div class="nav-num">Página 6</div>
        <div class="nav-title">Plan de Acción</div>
        <div class="nav-desc">Tu hoja de ruta táctica personalizada con fechas, exposición y € concretos</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="method-note">
    <p>
        <strong>Aviso legal:</strong> Esta herramienta tiene finalidad exclusivamente
        académica y de investigación. Los resultados presentados se basan en datos
        históricos y no constituyen asesoramiento financiero. Los retornos pasados
        no garantizan resultados futuros.
    </p>
</div>
""", unsafe_allow_html=True)
