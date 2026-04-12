"""
Genera el diagrama de flujo de la Ingeniería del Dato del TFG.
Versión 2: texto más grande, layout más compacto, mejor legibilidad.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse
import os

OUT = "/Users/adriancelada/Library/Mobile Documents/com~apple~CloudDocs/UFV/UNIVERSIDAD FRANCISCO DE VITORIA/4º/TFG/Ingenieria del Dato/Diagrama_Flujo_Ingenieria_Dato.png"

# ── Colores ────────────────────────────────────────────────────────
C_HEADER     = '#003366'
C_HEADER_TXT = '#FFFFFF'
C_ETL1       = '#DCEEFB'
C_ETL2       = '#FDE8D0'
C_VALID      = '#E8D5F5'
C_EDA        = '#D4EDDA'
C_BOX_BORDER = '#5A7DA5'
C_ARROW      = '#4A6D8C'
C_DB         = '#2C5F8A'
C_DB_LIGHT   = '#A8CCE8'
C_TEXT       = '#1A1A2E'

fig, ax = plt.subplots(figsize=(28, 22))
ax.set_xlim(-0.5, 28)
ax.set_ylim(-2, 22)
ax.axis('off')
fig.patch.set_facecolor('white')


def draw_box(x, y, w, h, text, color='#DCEEFB', fontsize=8.5, bold=False,
             border_color=C_BOX_BORDER):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.15",
                         facecolor=color, edgecolor=border_color, linewidth=0.9)
    ax.add_patch(box)
    fw = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize,
            fontweight=fw, color=C_TEXT, fontfamily='sans-serif', linespacing=1.25)


def draw_header(x, y, w, h, text):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.2",
                         facecolor=C_HEADER, edgecolor=C_HEADER, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=12,
            fontweight='bold', color=C_HEADER_TXT, fontfamily='sans-serif')


def draw_phase_bar(x, y, w, h, text, color):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.12",
                         facecolor=color, edgecolor='#999999', linewidth=0.6)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=9.5,
            fontweight='bold', color='#333333', fontfamily='sans-serif')


def draw_db(x, y, text, w=2.8):
    h_body = 0.7
    rect = plt.Rectangle((x, y), w, h_body, facecolor=C_DB_LIGHT, edgecolor=C_DB, linewidth=1.2, zorder=2)
    ax.add_patch(rect)
    ell_top = Ellipse((x + w/2, y + h_body), w, 0.4, facecolor=C_DB_LIGHT, edgecolor=C_DB, linewidth=1.2, zorder=3)
    ax.add_patch(ell_top)
    ell_bot = Ellipse((x + w/2, y), w, 0.4, facecolor=C_DB_LIGHT, edgecolor=C_DB, linewidth=1.2, zorder=1)
    ax.add_patch(ell_bot)
    ax.text(x + w/2, y + h_body/2, text, ha='center', va='center', fontsize=8,
            fontweight='bold', color=C_DB, fontfamily='sans-serif', zorder=4)


def draw_file_icon(x, y, text, w=2.0):
    h = 0.65
    fold = 0.18
    verts = [(x, y), (x, y+h), (x+w-fold, y+h), (x+w, y+h-fold), (x+w, y)]
    poly = Polygon(verts, facecolor='#F0F4FA', edgecolor='#6C8EBF', linewidth=0.9, zorder=2)
    ax.add_patch(poly)
    fold_verts = [(x+w-fold, y+h), (x+w-fold, y+h-fold), (x+w, y+h-fold)]
    fold_poly = Polygon(fold_verts, facecolor='#D0DFEF', edgecolor='#6C8EBF', linewidth=0.6, zorder=3)
    ax.add_patch(fold_poly)
    ax.text(x + w/2 - fold/4, y + h/2, text, ha='center', va='center', fontsize=7,
            color='#4A6D8C', fontfamily='sans-serif', fontweight='bold', zorder=4)


def arrow(x1, y1, x2, y2, color=C_ARROW, lw=1.2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))


# ════════════════════════════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════════════════════════════

BOX_W = 5.0
BOX_H = 0.7
STEP = 0.88  # vertical step between boxes

# Column x-positions
CX1 = 0.3
CX2 = 6.3
CX3 = 12.3
CX4 = 19.5

# ── TÍTULO ─────────────────────────────────────────────────────────
ax.text(14, 21.5, 'Diagrama de Flujo — Ingeniería del Dato', ha='center', va='center',
        fontsize=20, fontweight='bold', color=C_HEADER, fontfamily='sans-serif')
ax.text(14, 21.0, 'Impacto de las variables macroeconómicas en la volatilidad del IBEX 35',
        ha='center', va='center', fontsize=12, color='#555555', fontfamily='sans-serif', style='italic')

# ── BARRAS DE FASE ─────────────────────────────────────────────────
bar_y = 20.35
draw_phase_bar(1.0, bar_y, 3.5, 0.45, 'Extracción', '#B3D4F0')
draw_phase_bar(5.0, bar_y, 4.0, 0.45, 'Transformación', '#FFD699')
draw_phase_bar(9.5, bar_y, 3.0, 0.45, 'Limpieza', '#F5B7B1')
draw_phase_bar(13.0, bar_y, 3.5, 0.45, 'Validación', '#D7BDE2')
draw_phase_bar(17.0, bar_y, 2.5, 0.45, 'EDA', '#A9DFBF')

# ════════════════════════════════════════════════════════════════════
# COL 1: ETL EMPRESAS
# ════════════════════════════════════════════════════════════════════
draw_header(CX1, 19.5, BOX_W, 0.65, '01 — ETL Empresas')

# Fuentes
draw_file_icon(CX1 + 0.15, 18.6, 'Reuters Eikon\n35 archivos .xlsx', w=2.1)
draw_file_icon(CX1 + 2.7, 18.6, 'GridExport.xlsx\nRef. empresas', w=2.1)

y1_start = 17.9
steps1 = [
    ('1.1', 'Lectura sin cabecera (header=None)'),
    ('1.2', 'Detección auto. cabecera\n("Exchange Date")'),
    ('1.3', 'Estandarización nombres\n→ minúsculas'),
    ('1.4', 'Parseo fechas + filtrado ≥ 2005'),
    ('1.5', 'Conversión numérica'),
    ('1.6', 'Concatenar 35 empresas\n→ 157.455 filas × 9 cols'),
    ('1.7', 'Cálculo log_ret = ln(Pₜ/Pₜ₋₁)'),
    ('1.8', 'Cálculo vol_hist_21d\n= std(21d) × √252'),
    ('1.9', 'Detectar 8 nulos en close\n(CABK, FER, MRL, ROVI)'),
    ('1.10', 'Interpolación lineal\npandas.interpolate()'),
    ('1.11', 'Recálculo log_ret y vol_hist_21d'),
]

for i, (num, text) in enumerate(steps1):
    by = y1_start - i * STEP
    c = C_ETL1 if i <= 5 else ('#FDE2D4' if i <= 7 else '#F5D5D5')
    draw_box(CX1, by, BOX_W, BOX_H, f'{num}  {text}', color=c)
    if i > 0:
        arrow(CX1 + BOX_W/2, by + BOX_H + 0.01, CX1 + BOX_W/2, by + BOX_H + 0.17)

# DBs
db1y = y1_start - len(steps1) * STEP - 0.15
draw_db(CX1 + 1.0, db1y, 'precios_empresas\n157.455 filas', w=3.0)
arrow(CX1 + BOX_W/2, db1y + 1.0, CX1 + BOX_W/2, db1y + 0.9, lw=0.8)

draw_db(CX1 + 1.0, db1y - 1.15, 'ref_empresas\n36 filas', w=3.0)

# ════════════════════════════════════════════════════════════════════
# COL 2: ETL MACRO
# ════════════════════════════════════════════════════════════════════
draw_header(CX2, 19.5, BOX_W + 0.5, 0.65, '02 — ETL Macro')

draw_file_icon(CX2 + 0.0, 18.6, 'Reuters Eikon\n6 vars macro', w=1.6)
draw_file_icon(CX2 + 1.8, 18.6, 'Investing.com\n7 vars CSV', w=1.6)
draw_file_icon(CX2 + 3.6, 18.6, 'INE / BCE\n7 vars', w=1.5)

y2_start = 17.9
steps2 = [
    ('2.1', 'parsear_numero_europeo()\npunto→miles, coma→decimal'),
    ('2.2', 'leer_investing_csv()\ndetecta "Último", dd.mm.yyyy'),
    ('2.3', 'leer_reuters_macro()\nparsea "Q1 2005", "Jan 2005"'),
    ('2.4', 'leer_ine_matriz()\nunpivot año×mes → largo'),
    ('2.5', 'Parsing tipos BCE\nmes español → datetime'),
    ('2.6', 'Bloque 1: Actividad Económica\npib_yoy, tasa_paro, ipi_yoy, pmi'),
    ('2.7', 'Bloque 2: Cond. Monetarias\nbonos, spread, EUR/USD, Euribor'),
    ('2.8', 'Bloque 3: Inflación\nipc_yoy, ipc_sub_mom'),
    ('2.9', 'Bloque 4: Riesgo Global\nvix, vibex, vstoxx, brent, gas_ttf'),
    ('2.10', 'Merge por fecha (outer)\npreserva todas las fechas'),
]

for i, (num, text) in enumerate(steps2):
    by = y2_start - i * STEP
    c = C_ETL2 if i < 5 else '#FDD9B5'
    draw_box(CX2, by, BOX_W + 0.5, BOX_H, f'{num}  {text}', color=c)
    if i > 0:
        arrow(CX2 + (BOX_W+0.5)/2, by + BOX_H + 0.01, CX2 + (BOX_W+0.5)/2, by + BOX_H + 0.17)

# DBs macro
db2y = y2_start - len(steps2) * STEP - 0.15
db2_names = ['macro_mon_diario\n5.865 filas', 'macro_mon_mensual\n423 filas',
             'macro_act_mensual\n250 filas', 'macro_act_trimes\n82 filas',
             'macro_riesgo\n5.091 filas']
for j, name in enumerate(db2_names):
    draw_db(CX2 + 1.1, db2y - j * 1.15, name, w=3.0)

# ════════════════════════════════════════════════════════════════════
# COL 3: VALIDACIÓN
# ════════════════════════════════════════════════════════════════════
draw_header(CX3, 19.5, BOX_W + 1.0, 0.65, '03 — Validación y Dataset Maestro')

y3_start = 18.5
steps3 = [
    ('3.1', 'Extraer calendario bursátil\n5.323 fechas únicas'),
    ('3.2', 'Forward-fill (ffill)\nen cada tabla macro'),
    ('3.3', 'pd.merge_asof\ndirection="backward"'),
    ('3.4', 'Combinar 5 tablas macro\n→ df_macro_diario (5.323 × 21)'),
    ('3.5', 'Merge con precios empresas\n→ dataset_maestro'),
    ('3.6', '157.455 filas × 31 columnas\n35 empresas · 2005-2025'),
    ('3.7', 'Verificar 0 duplicados\n(ticker + fecha)'),
    ('3.8', 'Análisis cobertura nulos\npor variable'),
]

for i, (num, text) in enumerate(steps3):
    by = y3_start - i * STEP
    draw_box(CX3, by, BOX_W + 1.0, BOX_H, f'{num}  {text}', color=C_VALID)
    if i > 0:
        arrow(CX3 + (BOX_W+1)/2, by + BOX_H + 0.01, CX3 + (BOX_W+1)/2, by + BOX_H + 0.17)

db3y = y3_start - len(steps3) * STEP - 0.15
draw_db(CX3 + 1.3, db3y, 'dataset_maestro\n157.455 × 31', w=3.5)

# Flechas de entrada a validación
arrow(CX1 + BOX_W, y1_start - 5 * STEP + BOX_H/2,
      CX3, y3_start - 4 * STEP + BOX_H/2, lw=2.0, color='#7B68AE')
arrow(CX2 + BOX_W + 0.5, y2_start - 9 * STEP + BOX_H/2,
      CX3, y3_start - 3 * STEP + BOX_H/2, lw=2.0, color='#7B68AE')

# ════════════════════════════════════════════════════════════════════
# COL 4: EDA
# ════════════════════════════════════════════════════════════════════
draw_header(CX4, 19.5, BOX_W + 2.5, 0.65, '04 — Análisis Exploratorio (EDA)')

y4_start = 18.5
steps4 = [
    ('4.1', 'Estadísticos descriptivos\nmedia, std, curtosis = 16'),
    ('4.2', 'Visualización antes/después\nprecios → log-retornos (Fig. 2)'),
    ('4.3', 'Test ADF estacionariedad\nprecios NO · log_ret SÍ · vol SÍ'),
    ('4.4', 'ACF / PACF (60 lags)\nmemoria larga → justifica GARCH y HAR'),
    ('4.5', 'Correlaciones Pearson\nVIBEX +0,82 · VIX +0,75 · PIB -0,43'),
    ('4.6', 'Cross-correlación (CCF)\nlags 0-60 días, poder predictivo'),
    ('4.7', 'Detección outliers IQR + Z-score\n→ MANTENER (señal económica)'),
    ('4.8', 'Test Jarque-Bera normalidad\ntodas NO normales → t-Student'),
    ('4.9', 'Test Kruskal-Wallis sectores\nH=7.259, p≈0 → sectores difieren'),
    ('4.10', 'Tabla decisión variables\n20 mantener · 2 redund. · 1 limitada'),
    ('4.11', 'Split temporal train/test\nsin data leakage'),
]

for i, (num, text) in enumerate(steps4):
    by = y4_start - i * STEP
    draw_box(CX4, by, BOX_W + 2.5, BOX_H, f'{num}  {text}', color=C_EDA)
    if i > 0:
        arrow(CX4 + (BOX_W+2.5)/2, by + BOX_H + 0.01, CX4 + (BOX_W+2.5)/2, by + BOX_H + 0.17)

# Outputs EDA
out_y = y4_start - len(steps4) * STEP - 0.3
draw_file_icon(CX4 + 0.2, out_y, '15 figuras\nPNG', w=2.1)
draw_file_icon(CX4 + 2.6, out_y, '16 tablas\nestilizadas', w=2.1)
draw_file_icon(CX4 + 5.0, out_y, '5 tests\nestadísticos', w=2.1)

# Flecha dataset_maestro → EDA
arrow(CX3 + BOX_W + 1.0, y3_start - 0 * STEP + BOX_H/2,
      CX4, y4_start - 0 * STEP + BOX_H/2, lw=2.0, color='#2E8B57')

# ════════════════════════════════════════════════════════════════════
# BD FINAL (abajo centro)
# ════════════════════════════════════════════════════════════════════
bfx = 8.5
bfy = -1.0

big_box = FancyBboxPatch((bfx, bfy), 11, 2.5,
                          boxstyle="round,pad=0.12,rounding_size=0.25",
                          facecolor='#F0F4FA', edgecolor=C_HEADER, linewidth=2)
ax.add_patch(big_box)
ax.text(bfx + 5.5, bfy + 2.1, 'tfg.db — Base de datos SQLite',
        ha='center', fontsize=13, fontweight='bold', color=C_HEADER, fontfamily='sans-serif')
ax.text(bfx + 5.5, bfy + 1.7, '8 tablas  ·  >325.000 registros  ·  31 variables',
        ha='center', fontsize=10, color='#555555', fontfamily='sans-serif')

mini_tables = ['precios_empresas', 'ref_empresas', 'macro_mon_diario', 'macro_mon_mensual',
               'macro_act_mensual', 'macro_act_trimes', 'macro_riesgo', 'dataset_maestro']
for i, name in enumerate(mini_tables):
    col = i % 4
    row = i // 4
    mx = bfx + 0.4 + col * 2.65
    my = bfy + 0.7 - row * 0.6
    is_master = name == 'dataset_maestro'
    c_bg = '#B8D4E8' if is_master else C_DB_LIGHT
    c_brd = C_HEADER if is_master else '#5A7DA5'
    fs = 8 if is_master else 7
    box = FancyBboxPatch((mx, my), 2.4, 0.45,
                         boxstyle="round,pad=0.03,rounding_size=0.08",
                         facecolor=c_bg, edgecolor=c_brd, linewidth=0.8 if not is_master else 1.5)
    ax.add_patch(box)
    ax.text(mx + 1.2, my + 0.225, name, ha='center', va='center', fontsize=fs,
            fontweight='bold' if is_master else 'normal', color=c_brd, fontfamily='sans-serif')

# Flechas a BD final
arrow(CX1 + BOX_W/2, db1y - 1.15, bfx + 1.5, bfy + 2.5, lw=1.2, color='#999999')
arrow(CX2 + (BOX_W+0.5)/2, db2y - 4 * 1.15, bfx + 4.0, bfy + 2.5, lw=1.2, color='#999999')
arrow(CX3 + (BOX_W+1)/2, db3y, bfx + 7.0, bfy + 2.5, lw=1.2, color='#999999')

# Backups
draw_file_icon(bfx + 11.5, bfy + 1.3, 'Backup\n.parquet', w=2.0)
draw_file_icon(bfx + 11.5, bfy + 0.4, 'Backup\n.csv', w=2.0)
arrow(bfx + 11, bfy + 1.5, bfx + 11.5, bfy + 1.5, lw=0.8, color='#999999')
arrow(bfx + 11, bfy + 0.8, bfx + 11.5, bfy + 0.7, lw=0.8, color='#999999')

# ── Leyenda ────────────────────────────────────────────────────────
leg_y = -1.8
legend_items = [
    (C_ETL1, 'ETL Empresas (Notebook 01)'),
    (C_ETL2, 'ETL Macro (Notebook 02)'),
    (C_VALID, 'Validación (Notebook 03)'),
    (C_EDA, 'EDA (Notebook 04)'),
]
for i, (color, label) in enumerate(legend_items):
    lx = 2.0 + i * 5.5
    box = FancyBboxPatch((lx, leg_y), 0.5, 0.35,
                         boxstyle="round,pad=0.03,rounding_size=0.06",
                         facecolor=color, edgecolor=C_BOX_BORDER, linewidth=0.6)
    ax.add_patch(box)
    ax.text(lx + 0.7, leg_y + 0.175, label, ha='left', va='center', fontsize=9,
            color=C_TEXT, fontfamily='sans-serif')

# ── Guardar ────────────────────────────────────────────────────────
plt.tight_layout(pad=0.3)
fig.savefig(OUT, dpi=250, bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close(fig)
print(f"✓ Diagrama guardado en:\n  {OUT}")
