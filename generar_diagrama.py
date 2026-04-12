#!/usr/bin/env python3
"""
Diagrama de Flujo — Ingenieria del Dato
Impacto de las variables macroeconomicas en la volatilidad del IBEX 35

Genera un diagrama visual estilo Lucidchart / draw.io usando solo matplotlib.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np

# ─── Global config ───────────────────────────────────────────────────────────
fig_w, fig_h = 34, 26
DPI = 200

# Colors
COL_PINK_BG    = '#F5DCDC'
COL_BLUE_BG    = '#DCEAF5'
COL_WHITE      = '#FFFFFF'
COL_STEP_BG    = '#FFFFFF'
COL_STEP_EDGE  = '#B8B8B8'
COL_NAVY       = '#1B3A5C'
COL_DB_TOP     = '#2D5F8A'
COL_HEADER_01  = '#EAC89A'
COL_HEADER_02  = '#B8D498'
COL_HEADER_03  = '#98C8D8'
COL_HEADER_04  = '#C8A8D8'
COL_SRC_BG     = '#F2F2F2'
COL_ARROW      = '#444444'

FONT_BASE = 'sans-serif'

# ─── Layout constants ────────────────────────────────────────────────────────
COL_CENTERS = [5.0, 13.5, 22.0, 30.0]
COL_WIDTHS  = [7.5, 7.5, 7.5, 6.8]

Y_TITLE       = 25.2
Y_PHASES      = 24.4
Y_NB_HEADER   = 23.5
Y_SOURCES     = 22.5
Y_STEPS_START = 21.3

STEP_H = 0.52
STEP_GAP = 0.10


def rounded_box(ax, x, y, w, h, fc, ec='none', lw=0.8, rad=0.08,
                alpha=1.0, zorder=1):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0,rounding_size={rad}",
                         facecolor=fc, edgecolor=ec, linewidth=lw,
                         alpha=alpha, zorder=zorder)
    ax.add_patch(box)
    return box


def step_box(ax, cx, cy, w, h, text, zorder=5):
    """White step box with text."""
    rounded_box(ax, cx - w/2, cy - h/2, w, h, COL_STEP_BG,
                ec=COL_STEP_EDGE, lw=0.6, rad=0.06, zorder=zorder)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=6.8,
            fontfamily=FONT_BASE, color='#222222', zorder=zorder+1,
            linespacing=1.15)


def cylinder(ax, cx, cy, w, h, label, sublabel="", zorder=6):
    rect_x = cx - w/2
    rect_y = cy - h/2
    rect_h = h * 0.65
    ell_h = h * 0.35
    # Bottom ellipse
    ax.add_patch(Ellipse((cx, rect_y), w, ell_h, facecolor=COL_NAVY,
                          edgecolor='#0D2137', lw=0.8, zorder=zorder))
    # Body
    ax.add_patch(plt.Rectangle((rect_x, rect_y), w, rect_h,
                                facecolor=COL_NAVY, edgecolor='none',
                                zorder=zorder+1))
    ax.plot([rect_x, rect_x], [rect_y, rect_y + rect_h],
            color='#0D2137', lw=0.8, zorder=zorder+2)
    ax.plot([rect_x + w, rect_x + w], [rect_y, rect_y + rect_h],
            color='#0D2137', lw=0.8, zorder=zorder+2)
    # Top ellipse
    ax.add_patch(Ellipse((cx, rect_y + rect_h), w, ell_h,
                          facecolor=COL_DB_TOP, edgecolor='#0D2137',
                          lw=0.8, zorder=zorder+3))
    ax.text(cx, rect_y + rect_h * 0.55, label, ha='center', va='center',
            color='white', fontsize=7, fontweight='bold',
            fontfamily=FONT_BASE, zorder=zorder+4)
    if sublabel:
        ax.text(cx, rect_y + rect_h * 0.15, sublabel, ha='center',
                va='center', color='#AABBCC', fontsize=5.5,
                fontfamily=FONT_BASE, zorder=zorder+4)


def source_badge(ax, cx, cy, line1, line2, icon="", w=3.0, h=0.70):
    rounded_box(ax, cx - w/2, cy - h/2, w, h, COL_SRC_BG,
                ec='#BBBBBB', lw=0.5, rad=0.08, zorder=4)
    if icon:
        r = 0.18
        ix = cx - w/2 + 0.32
        ax.add_patch(plt.Circle((ix, cy), r, facecolor='#D0E0F0',
                                edgecolor='#7799AA', lw=0.5, zorder=5))
        ax.text(ix, cy, icon, ha='center', va='center', fontsize=5.5,
                fontfamily=FONT_BASE, color='#335577', fontweight='bold',
                zorder=6)
        tx = cx + 0.18
    else:
        tx = cx
    ax.text(tx, cy + 0.10, line1, ha='center', va='center', fontsize=6.5,
            fontfamily=FONT_BASE, color='#333333', fontweight='bold', zorder=5)
    ax.text(tx, cy - 0.12, line2, ha='center', va='center', fontsize=5.8,
            fontfamily=FONT_BASE, color='#666666', zorder=5)


def arr_down(ax, x, y1, y2, zorder=3):
    ax.annotate('', xy=(x, y2), xytext=(x, y1),
                arrowprops=dict(arrowstyle='->', color=COL_ARROW,
                                lw=0.7, shrinkA=1, shrinkB=1),
                zorder=zorder)


def arr_right(ax, x1, y1, x2, y2, rad=0.15, zorder=3):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=COL_ARROW, lw=0.7,
                                connectionstyle=f'arc3,rad={rad}',
                                shrinkA=2, shrinkB=2),
                zorder=zorder)


def place_steps(ax, cx, steps, y_start, col_w=6.6, side_by_side=None):
    """
    Place steps. side_by_side is a set of indices i where steps[i] and
    steps[i+1] go side by side.
    Returns list of (cx, cy) per step and y_end.
    """
    if side_by_side is None:
        side_by_side = set()
    positions = []
    y = y_start
    i = 0
    while i < len(steps):
        if i in side_by_side and i + 1 < len(steps):
            w = col_w / 2 - 0.06
            lx = cx - col_w/4 - 0.02
            rx = cx + col_w/4 + 0.02
            step_box(ax, lx, y, w, STEP_H, steps[i])
            step_box(ax, rx, y, w, STEP_H, steps[i+1])
            positions.append((lx, y))
            positions.append((rx, y))
            i += 2
        else:
            step_box(ax, cx, y, col_w, STEP_H, steps[i])
            positions.append((cx, y))
            i += 1
        y -= (STEP_H + STEP_GAP)
    return positions, y


def draw_sequential_arrows(ax, positions, steps, side_by_side, cx):
    """Draw vertical arrows connecting sequential steps, handling side-by-side."""
    # Build rows: list of (row_indices, is_pair)
    rows = []
    i = 0
    while i < len(steps):
        if i in side_by_side and i + 1 < len(steps):
            rows.append(([i, i+1], True))
            i += 2
        else:
            rows.append(([i], False))
            i += 1

    for r in range(len(rows) - 1):
        cur_idxs, cur_pair = rows[r]
        nxt_idxs, nxt_pair = rows[r + 1]
        src_y = positions[cur_idxs[0]][1] - STEP_H/2
        tgt_y = positions[nxt_idxs[0]][1] + STEP_H/2

        if not cur_pair and not nxt_pair:
            arr_down(ax, positions[cur_idxs[0]][0], src_y, tgt_y)
        elif cur_pair and not nxt_pair:
            # Both sides converge to center
            arr_down(ax, cx, src_y, tgt_y)
        elif not cur_pair and nxt_pair:
            arr_down(ax, cx, src_y, tgt_y)
        else:
            # Both pairs
            arr_down(ax, cx - 0.3, src_y, tgt_y)
            arr_down(ax, cx + 0.3, src_y, tgt_y)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(1, 1, figsize=(fig_w, fig_h))
fig.patch.set_facecolor(COL_WHITE)
ax.set_xlim(0, fig_w)
ax.set_ylim(0, fig_h)
ax.set_aspect('equal')
ax.axis('off')

# ─── Title ───────────────────────────────────────────────────────────────────
ax.text(fig_w/2, Y_TITLE, 'Diagrama de Flujo — Ingeniería del Dato',
        ha='center', va='center', fontsize=18, fontweight='bold',
        fontfamily=FONT_BASE, color='#1B3A5C', zorder=10)
ax.text(fig_w/2, Y_TITLE - 0.45,
        'Impacto de las variables macroeconómicas en la volatilidad del IBEX 35',
        ha='center', va='center', fontsize=11, fontstyle='italic',
        fontfamily=FONT_BASE, color='#555555', zorder=10)

# ─── Phase badges ────────────────────────────────────────────────────────────
phases = [
    ('Extracción', '#F0F0F0', '#555555'),
    ('Transformación', '#B8D4F0', '#2255AA'),
    ('Limpieza', '#D0E8D0', '#227744'),
    ('Validación', '#E0E0E0', '#555555'),
    ('EDA', '#D0E8D0', '#227744'),
]
px_start = 6.0
px_gap = 4.8
for idx, (ptxt, pbg, ptc) in enumerate(phases):
    px = px_start + idx * px_gap
    pw, ph = 3.8, 0.42
    rounded_box(ax, px - pw/2, Y_PHASES - ph/2, pw, ph, pbg,
                ec='#AAAAAA', lw=0.6, rad=0.12, zorder=4)
    ax.text(px, Y_PHASES, ptxt, ha='center', va='center',
            fontsize=9, fontweight='bold', fontfamily=FONT_BASE,
            color=ptc, zorder=5)

# ─── Column background panels ───────────────────────────────────────────────
panel_top = Y_NB_HEADER + 0.6
panel_bot = 4.2
for i, (ccx, cw) in enumerate(zip(COL_CENTERS, COL_WIDTHS)):
    bg = COL_BLUE_BG if i == 3 else COL_PINK_BG
    ec = '#B0C0D0' if i == 3 else '#D8C8C8'
    rounded_box(ax, ccx - cw/2 - 0.5, panel_bot, cw + 1.0,
                panel_top - panel_bot, bg, ec=ec, lw=0.5, rad=0.18,
                alpha=0.50, zorder=1)

# ─── Notebook headers ───────────────────────────────────────────────────────
nb_headers = [
    ('01 — ETL Empresas', COL_HEADER_01),
    ('02 — ETL Macro', COL_HEADER_02),
    ('03 — Validación y Dataset Maestro', COL_HEADER_03),
    ('04 — Análisis Exploratorio (EDA)', COL_HEADER_04),
]
for i, (txt, col) in enumerate(nb_headers):
    cx = COL_CENTERS[i]
    w = COL_WIDTHS[i] + 0.3
    h = 0.52
    rounded_box(ax, cx - w/2, Y_NB_HEADER - h/2, w, h, col,
                ec='#888888', lw=0.7, rad=0.14, zorder=4)
    ax.text(cx, Y_NB_HEADER, txt, ha='center', va='center',
            fontsize=11, fontweight='bold', fontfamily=FONT_BASE,
            color='#222222', zorder=5)

# ─── Sources ─────────────────────────────────────────────────────────────────
# Col 1
source_badge(ax, 3.7, Y_SOURCES, "Reuters Eikon", "35 archivos .xlsx", "R", w=3.0)
source_badge(ax, 6.7, Y_SOURCES, "GridExport.xlsx", "Ref. empresas", "G", w=2.6)
# Col 2
source_badge(ax, 11.5, Y_SOURCES, "Reuters Eikon", "6 vars macro", "R", w=2.6)
source_badge(ax, 14.1, Y_SOURCES, "Investing.com", "7 vars CSV", "I", w=2.4)
source_badge(ax, 16.3, Y_SOURCES, "INE / BCE", "7 vars", "E", w=2.0)
# Col 3
source_badge(ax, 22.0, Y_SOURCES, "Tablas de NB 01 y 02", "(desde tfg.db)", "", w=4.0)
# Col 4
source_badge(ax, 30.0, Y_SOURCES, "dataset_maestro", "(desde NB 03)", "", w=3.4)

# ─── Small notebook badges ──────────────────────────────────────────────────
by = Y_SOURCES - 0.55
nb_badges = [
    ("ETL Python", COL_HEADER_01),
    ("ETL Python", COL_HEADER_02),
    ("Validación", COL_HEADER_03),
    ("EDA Python", COL_HEADER_04),
]
for i, (bt, bc) in enumerate(nb_badges):
    bw, bh = 2.0, 0.34
    rounded_box(ax, COL_CENTERS[i] - bw/2, by - bh/2, bw, bh, bc,
                ec='#888888', lw=0.5, rad=0.10, zorder=5)
    ax.text(COL_CENTERS[i], by, bt, ha='center', va='center',
            fontsize=7, fontweight='bold', fontfamily=FONT_BASE,
            color='#333333', zorder=6)

# ═════════════════════════════════════════════════════════════════════════════
# STEPS
# ═════════════════════════════════════════════════════════════════════════════
y0 = by - 0.60

# ─── Column 1 ────────────────────────────────────────────────────────────────
s01 = [
    "1.0  Exploración previa dataset",
    "1.1  Lectura sin cabecera (header=None)",
    "1.2  Detección auto. cabecera\n(\"Exchange Date\")",
    "1.3  Estandarización nombres\n→ minúsculas",
    "1.4  Parseo fechas + filtrado ≥ 2005",
    "1.5  Conversión numérica",
    "1.6  Concatenar 35 empresas\n→ 157.455 filas",
    "1.7  Cálculo log_ret = ln(Pₜ/Pₜ₋₁)",
    "1.8  Cálculo vol_hist_21d\n= std(21d) × √252",
    "1.9  Detectar 8 nulos en close\n(CABK, FER, MRL, ROVI)",
    "1.10  Interpolación lineal\n(pandas.interpolate())",
    "1.11  Recálculo log_ret y vol_hist_21d",
]
p01, ye01 = place_steps(ax, COL_CENTERS[0], s01, y0, col_w=6.8)
draw_sequential_arrows(ax, p01, s01, set(), COL_CENTERS[0])

# ─── Column 2 ────────────────────────────────────────────────────────────────
s02 = [
    "2.0  Exploración previa datasets",
    "2.1  parsear_numero_europeo()\npunto=miles, coma=decimal",
    "2.2  leer_investing_csv()\ndetecta \"Último\", dd.mm.yyyy",
    "2.3  leer_reuters_macro()\nparsea \"Q1 2005\", \"Jan 2005\"",
    "2.4  leer_ine_matriz() — unpivot",
    "2.5  Parsing tipos BCE\nmes español → datetime",
    "2.6  Bloque 1: Actividad Económica\npib, paro, ipi_yoy, pmi",
    "2.7  Bloque 2: Cond. Monetarias\nbonos, spread, EUR/USD, Euríbor",
    "2.8  Bloque 3: Inflación\nipc_yoy, ipc_sub_yoy",
    "2.9  Bloque 4: Riesgo Global\nvix, vibex, vstoxx, brent, gas_ttf",
    "2.10  Merge por fecha (outer)\npreserva todas las fechas",
]
sbs02 = {1, 3, 6, 8}
p02, ye02 = place_steps(ax, COL_CENTERS[1], s02, y0, col_w=6.8,
                         side_by_side=sbs02)
draw_sequential_arrows(ax, p02, s02, sbs02, COL_CENTERS[1])

# ─── Column 3 ────────────────────────────────────────────────────────────────
s03 = [
    "3.1  Extraer calendario bursátil\n5.323 fechas únicas",
    "3.2  Forward-fill (ffill)\nen cada tabla macro",
    "3.3  pd.merge_asof\ndirection=\"backward\"",
    "3.4  Combinar 5 tablas macro\n→ df_macro_diario (5.323 × 21)",
    "3.5  Merge con precios empresas\n→ dataset_maestro",
    "3.6  157.455 filas × 31 columnas\n35 empresas · 2005-2025",
    "3.7  Verificar 0 duplicados\n(ticker + fecha)",
    "3.8  Análisis cobertura nulos\npor variable",
]
p03, ye03 = place_steps(ax, COL_CENTERS[2], s03, y0, col_w=6.8)
draw_sequential_arrows(ax, p03, s03, set(), COL_CENTERS[2])

# ─── Column 4 ────────────────────────────────────────────────────────────────
s04 = [
    "4.1  Estadísticos descriptivos\nmedia, std, curtosis = 16",
    "4.2  Visualización antes/después\nprecios → log-retornos (fig. 2)",
    "4.3  Test ADF estacionariedad\nprecios NO · log_ret Sí · vol Sí",
    "4.4  ACF / PACF (60 lags)\nmemoria larga → justifica GARCH y HAR",
    "4.5  Correlaciones Pearson\nVIBEX +0.82 · VIX +0.75 · PIB -0.43",
    "4.6  Cross-correlación (CCF)\nlags 0-60 días, poder predictivo",
    "4.7  Detección outliers → IQR + Z-score\n→ MANTENER (señal económica)",
    "4.8  Test Jarque-Bera normalidad\ntodas NO normales → t-Student",
    "4.9  Test Kruskal-Wallis sectores\nH=7.259, p=0 → sectores difieren",
    "4.10  Tabla decisión variables\n20 mantener · 2 redund. · 1 limitada",
    "4.11  Split temporal train/test\nsin data leakage",
]
sbs04 = {0, 2, 4, 6}
p04, ye04 = place_steps(ax, COL_CENTERS[3], s04, y0, col_w=6.2,
                         side_by_side=sbs04)
draw_sequential_arrows(ax, p04, s04, sbs04, COL_CENTERS[3])

# ═════════════════════════════════════════════════════════════════════════════
# OUTPUT BOXES (intermediate)
# ═════════════════════════════════════════════════════════════════════════════

# ─── Col 1 outputs ───────────────────────────────────────────────────────────
oy1 = ye01 - 0.05
rounded_box(ax, COL_CENTERS[0] - 2.6, oy1 - 0.30, 5.2, 0.60,
            '#E0E8F2', ec='#6688AA', lw=0.7, rad=0.08, zorder=4)
ax.text(COL_CENTERS[0], oy1, "precios_empresas\n157.455 filas",
        ha='center', va='center', fontsize=7.5, fontweight='bold',
        fontfamily=FONT_BASE, color='#224466', zorder=5)

oy1b = oy1 - 0.78
rounded_box(ax, COL_CENTERS[0] - 1.8, oy1b - 0.25, 3.6, 0.50,
            '#E0E8F2', ec='#6688AA', lw=0.7, rad=0.08, zorder=4)
ax.text(COL_CENTERS[0], oy1b, "ref_empresas\n36 filas",
        ha='center', va='center', fontsize=7.5, fontweight='bold',
        fontfamily=FONT_BASE, color='#224466', zorder=5)

arr_down(ax, COL_CENTERS[0], p01[-1][1] - STEP_H/2, oy1 + 0.30)

# ─── Col 2 outputs ───────────────────────────────────────────────────────────
macro_tabs = [
    ("macro_mon_diario", "5.069 filas"),
    ("macro_mon_mensual", "623 filas"),
    ("macro_act_mensual", "250 filas"),
    ("macro_act_trimes", "83 filas"),
    ("macro_riesgo", "5.091 filas"),
]
oy2_start = ye02 - 0.05
for j, (mn, ms) in enumerate(macro_tabs):
    my = oy2_start - j * 0.65
    rounded_box(ax, COL_CENTERS[1] - 2.0, my - 0.25, 4.0, 0.50,
                '#DEF0DE', ec='#558855', lw=0.7, rad=0.08, zorder=4)
    ax.text(COL_CENTERS[1], my, f"{mn}\n{ms}",
            ha='center', va='center', fontsize=6.8, fontweight='bold',
            fontfamily=FONT_BASE, color='#2A5A2A', zorder=5)
arr_down(ax, COL_CENTERS[1], p02[-1][1] - STEP_H/2, oy2_start + 0.25)

# ─── Col 3 output ────────────────────────────────────────────────────────────
oy3 = ye03 - 0.15
rounded_box(ax, COL_CENTERS[2] - 2.6, oy3 - 0.30, 5.2, 0.65,
            '#D0E4F0', ec='#4477AA', lw=0.8, rad=0.08, zorder=4)
ax.text(COL_CENTERS[2], oy3, "dataset_maestro\n157.455 × 31",
        ha='center', va='center', fontsize=8.5, fontweight='bold',
        fontfamily=FONT_BASE, color='#1A3A5A', zorder=5)
arr_down(ax, COL_CENTERS[2], p03[-1][1] - STEP_H/2, oy3 + 0.35)

# ─── Col 4 outputs ───────────────────────────────────────────────────────────
oy4 = min(ye04, ye03) - 0.4
out4_items = [
    ("15 figuras\nPNG", '#F5E8D0', '#996622'),
    ("16 tablas\nestilizadas", '#E0D8F0', '#554488'),
    ("5 tests\nestadísticos", '#D0F0D0', '#336633'),
]
ow = 1.8
total = len(out4_items) * ow + (len(out4_items)-1) * 0.15
sx = COL_CENTERS[3] - total/2
for j, (ot, obg, otc) in enumerate(out4_items):
    ox = sx + j * (ow + 0.15)
    rounded_box(ax, ox, oy4 - 0.25, ow, 0.50, obg, ec=otc,
                lw=0.7, rad=0.08, zorder=4)
    ax.text(ox + ow/2, oy4, ot, ha='center', va='center',
            fontsize=6.8, fontweight='bold', fontfamily=FONT_BASE,
            color=otc, zorder=5)
arr_down(ax, COL_CENTERS[3], p04[-1][1] - STEP_H/2, oy4 + 0.25)

# ═════════════════════════════════════════════════════════════════════════════
# CROSS-COLUMN ARROWS
# ═════════════════════════════════════════════════════════════════════════════
# Col 1 → Col 3 (step 3.5)
arr_right(ax, COL_CENTERS[0] + 3.5, oy1, p03[4][0] - 3.5, p03[4][1],
          rad=0.12)
# Col 2 → Col 3 (step 3.2)
arr_right(ax, COL_CENTERS[1] + 3.5, oy2_start, p03[1][0] - 3.5,
          p03[1][1], rad=0.10)
# Col 3 → Col 4
arr_right(ax, COL_CENTERS[2] + 3.5, oy3, COL_CENTERS[3] - 3.3,
          p04[0][1], rad=0.12)

# ═════════════════════════════════════════════════════════════════════════════
# DATABASE SECTION (bottom)
# ═════════════════════════════════════════════════════════════════════════════
db_top = 3.5
db_h = 2.5
rounded_box(ax, 2.5, db_top - db_h, fig_w - 5.0, db_h, '#EEF2F8',
            ec='#8899AA', lw=0.8, rad=0.18, alpha=0.75, zorder=2)

ax.text(fig_w/2, db_top - 0.30, 'tfg.db — Base de datos SQLite',
        ha='center', va='center', fontsize=14, fontweight='bold',
        fontfamily=FONT_BASE, color=COL_NAVY, zorder=5)
ax.text(fig_w/2, db_top - 0.65,
        '8 tablas  ·  >325.000 registros  ·  31 variables',
        ha='center', va='center', fontsize=9.5, fontfamily=FONT_BASE,
        color='#556677', zorder=5)

db_names = [
    ['precios_empresas', 'ref_empresas', 'macro_mon_diario',
     'macro_mon_mensual'],
    ['macro_act_mensual', 'macro_act_trimes', 'macro_riesgo',
     'dataset_maestro'],
]
cyl_w = 2.8
cyl_h = 0.55
cy_start = db_top - 1.10
cg = 6.5
for ri, row in enumerate(db_names):
    cy = cy_start - ri * 0.82
    tw = len(row) * cg
    sx = fig_w/2 - tw/2 + cg/2
    for ci, nm in enumerate(row):
        cylinder(ax, sx + ci * cg, cy, cyl_w, cyl_h, nm)

# Arrows from output sections → DB
arr_down(ax, COL_CENTERS[0], oy1b - 0.25, db_top + 0.05)
last_m_y = oy2_start - 4 * 0.65 - 0.25
arr_down(ax, COL_CENTERS[1], last_m_y, db_top + 0.05)
arr_down(ax, COL_CENTERS[2], oy3 - 0.30, db_top + 0.05)

# Backup badges
bx = fig_w - 4.0
rounded_box(ax, bx - 0.9, db_top - 1.3, 1.8, 0.50, '#FFF5E0',
            ec='#CC9933', lw=0.6, rad=0.08, zorder=5)
ax.text(bx, db_top - 1.06, "Backup\n.parquet", ha='center', va='center',
        fontsize=6.8, fontweight='bold', fontfamily=FONT_BASE,
        color='#886622', zorder=6)

rounded_box(ax, bx - 0.9, db_top - 1.90, 1.8, 0.50, '#EEF5E0',
            ec='#669933', lw=0.6, rad=0.08, zorder=5)
ax.text(bx, db_top - 1.66, "Backup\n.csv", ha='center', va='center',
        fontsize=6.8, fontweight='bold', fontfamily=FONT_BASE,
        color='#446622', zorder=6)

# ─── Legend ──────────────────────────────────────────────────────────────────
ly = 0.35
leg = [
    (COL_HEADER_01, "ETL Empresas (Notebook 01)"),
    (COL_HEADER_02, "ETL Macro (Notebook 02)"),
    (COL_HEADER_03, "Validación (Notebook 03)"),
    (COL_HEADER_04, "EDA (Notebook 04)"),
]
lx0 = 6.0
lgap = 7.0
for i, (lc, lt) in enumerate(leg):
    lx = lx0 + i * lgap
    rounded_box(ax, lx, ly - 0.12, 0.50, 0.28, lc, ec='#888888',
                lw=0.5, rad=0.06, zorder=5)
    ax.text(lx + 0.70, ly + 0.02, lt, ha='left', va='center',
            fontsize=8, fontfamily=FONT_BASE, color='#333333', zorder=5)

# ─── Separator line ──────────────────────────────────────────────────────────
ax.axhline(y=by - 0.30, xmin=0.05, xmax=0.95, color='#D8D8D8',
           lw=0.4, ls='--', zorder=1)

# ─── Save ────────────────────────────────────────────────────────────────────
output_path = (
    "/Users/adriancelada/Library/Mobile Documents/"
    "com~apple~CloudDocs/UFV/UNIVERSIDAD FRANCISCO DE VITORIA/"
    "4º/TFG/Ingenieria del Dato/Diagrama_Flujo_Ingenieria_Dato.png"
)

plt.tight_layout(pad=0.5)
fig.savefig(output_path, dpi=DPI, bbox_inches='tight',
            facecolor=COL_WHITE, edgecolor='none')
plt.close(fig)
print(f"Diagrama guardado en:\n{output_path}")
print(f"Tamaño: {fig_w}x{fig_h} pulgadas a {DPI} DPI")
