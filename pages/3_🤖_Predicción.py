"""Predicción de LubriInsight.
Clasificación binaria de recurrencia y churn sobre la nueva BD Lubricadora_db.
Diseño visual dinámico (tema oscuro dorado/azul) + lógica de entrenamiento avanzada
(Regresión Logística vs Random Forest, validación cruzada repetida para umbral).
"""
from __future__ import annotations

import io
import traceback
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from utils.database import query_df
from utils.footer import show_footer

# ─── Configuración de página ────────────────────────────────────────────────
st.set_page_config(page_title="LubriInsight | Predicción", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ─── Paleta oscura dorado/azul acero (misma identidad del resto de la app) ──
BG = "#0A0B0F"
PANEL = "rgba(255,255,255,0.035)"
PANEL_SOLID = "#12141B"
BORDER = "rgba(255,255,255,0.08)"
GOLD = "#E3A73E"
GOLD_LIGHT = "#F5CF7A"
STEEL = "#4F8FC4"
STEEL_LIGHT = "#9CC9EC"
TEXT = "#EDEFF2"
MUTED = "#98A4B2"
GREEN = "#2ED18C"
RED = "#E5615B"
COLORS = {"navy": TEXT, "blue": STEEL_LIGHT, "gold": GOLD_LIGHT, "green": GREEN, "red": RED, "bg": BG, "muted": MUTED}

st.markdown(f"""<style>
[data-testid="stSidebar"] *{{color:{TEXT} !important}}
[data-testid="stSidebarNav"] a{{border-radius:10px;margin:2px 8px;padding:10px 12px !important;
    transition:background .15s ease}}
[data-testid="stSidebarNav"] span{{font-family:'Playfair Display',serif;font-weight:600;
    font-size:.95rem;letter-spacing:.01em;white-space:normal !important}}
[data-testid="stSidebarNav"] a:hover{{background:rgba(227,167,62,.14) !important}}
[data-testid="stSidebarNav"] a[aria-current="page"]{{
    background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
    border-left:3px solid {GOLD_LIGHT}}}
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(217,169,76,.10),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(143,180,217,.08),transparent 40%),{BG}}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}

/* Oculta el menú/botón "Deploy" nativo de Streamlit — no forma parte del diseño */
[data-testid="stToolbar"]{{display:none !important}}
#MainMenu{{visibility:hidden !important}}
footer{{visibility:hidden !important}}

.block-container{{max-width:1400px;padding:2rem 4rem 4rem}}
h1,h2,h3,h4{{color:{TEXT};letter-spacing:-.03em;font-family:'Playfair Display',serif}}
p, span, div, label{{color:{TEXT}}}

@keyframes fadeSlideUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes softPulse{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
@keyframes ringPulse{{0%{{box-shadow:0 0 0 0 rgba(227,167,62,.45)}}70%{{box-shadow:0 0 0 10px rgba(227,167,62,0)}}100%{{box-shadow:0 0 0 0 rgba(227,167,62,0)}}}}
@keyframes shimmerSweep{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(220%)}}}}
@keyframes heroSheen{{0%{{left:-60%}}50%{{left:120%}}100%{{left:120%}}}}

.hero{{position:relative;background:linear-gradient(160deg,#12141B 0%,#0A0B0F 70%);border:1px solid rgba(217,169,76,.25);
    border-radius:22px;padding:34px 38px;margin-bottom:28px;box-shadow:0 18px 46px rgba(0,0,0,.55);
    animation:fadeSlideUp .55s ease-out;overflow:hidden}}
.hero::after{{content:'';position:absolute;top:0;left:-60%;width:40%;height:100%;
    background:linear-gradient(100deg,transparent,rgba(245,207,122,.06),transparent);
    animation:heroSheen 5s ease-in-out infinite}}
.hero h1{{margin:0 0 10px;font-size:clamp(2rem,4vw,3.7rem);display:flex;align-items:center;gap:14px;
    background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero .hero-icon{{-webkit-text-fill-color:initial;display:inline-block;animation:softPulse 2.4s ease-in-out infinite}}
.hero p{{color:{MUTED};max-width:68ch;font-size:1.05rem;margin:0;line-height:1.55}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:.73rem;color:{GOLD};margin-bottom:12px;
    display:flex;align-items:center;gap:8px}}
.eyebrow .dot{{width:7px;height:7px;border-radius:50%;background:{GOLD_LIGHT};box-shadow:0 0 8px {GOLD_LIGHT};
    animation:softPulse 1.8s ease-in-out infinite}}

.section-title{{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{TEXT};
    display:flex;align-items:center;gap:10px;margin:26px 0 14px 0}}
.section-title .bar{{width:5px;height:22px;border-radius:3px;
    background:linear-gradient(180deg,{GOLD_LIGHT},{STEEL_LIGHT});box-shadow:0 0 10px rgba(245,207,122,.5)}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:16px;padding:18px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

.section{{margin:34px 0 16px}}.section h2{{margin-bottom:4px}}.muted{{color:{MUTED}}}

.var-card{{background:{PANEL};border:1px solid {BORDER};border-radius:14px;padding:18px 20px;margin-bottom:10px;
    box-shadow:0 6px 18px rgba(0,0,0,.3);animation:fadeSlideUp .5s ease-out;
    transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}}
.var-card:hover{{transform:translateY(-3px);box-shadow:0 12px 26px rgba(0,0,0,.45);border-color:rgba(227,167,62,.35)}}
.var-card .var-icon{{font-size:1.3rem;margin-right:8px}}
.var-card .var-name{{font-weight:700;color:{GOLD_LIGHT};font-size:.95rem}}
.var-card .var-desc{{color:{MUTED};font-size:.82rem;margin-top:4px}}

.objetivo-box{{position:relative;background:linear-gradient(135deg,#12141B 0%,#0A0B0F 100%);border:1px solid rgba(227,167,62,.3);
    border-radius:16px;padding:22px 26px;margin:18px 0 24px;box-shadow:0 10px 28px rgba(0,0,0,.4);
    animation:fadeSlideUp .55s ease-out;overflow:hidden}}
.objetivo-box::after{{content:'';position:absolute;top:0;left:-60%;width:35%;height:100%;
    background:linear-gradient(100deg,transparent,rgba(245,207,122,.05),transparent);animation:heroSheen 6s ease-in-out infinite}}
.objetivo-box h4{{color:{GOLD_LIGHT};margin:0 0 6px;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em}}
.objetivo-box p{{color:{TEXT};margin:0;font-size:.95rem;line-height:1.5}}
.objetivo-box code{{background:rgba(227,167,62,.18);color:{GOLD_LIGHT};padding:2px 8px;border-radius:6px}}
.clase-chip{{display:inline-flex;align-items:center;gap:6px;padding:3px 11px;border-radius:999px;font-size:.78rem;font-weight:700;margin:2px 0}}
.clase-activo{{background:rgba(46,209,140,.15);color:{GREEN};border:1px solid rgba(46,209,140,.35)}}
.clase-inactivo{{background:rgba(229,97,91,.15);color:{RED};border:1px solid rgba(229,97,91,.35)}}

.client-card{{background:{PANEL};border:1px solid {BORDER};border-radius:14px;padding:16px 20px;margin-bottom:16px;
    animation:fadeSlideUp .45s ease-out}}
.client-card strong{{color:{GOLD_LIGHT};font-size:1.05rem}}
.client-card span{{color:{MUTED};margin-left:12px}}
.client-card code{{background:rgba(255,255,255,.06);color:{STEEL_LIGHT};padding:2px 6px;border-radius:5px}}

/* Pestañas con la misma tipografía de los títulos (Playfair Display), más grandes y legibles */
[data-baseweb="tab-list"]{{border-bottom:1px solid {BORDER};gap:6px}}
[data-baseweb="tab"]{{color:{MUTED};font-weight:600;transition:color .2s ease}}
[data-baseweb="tab"] p{{font-family:'Playfair Display',serif;font-weight:600;font-size:1.02rem;letter-spacing:.01em}}
[data-baseweb="tab"]:hover{{color:{GOLD_LIGHT} !important}}
[aria-selected="true"][data-baseweb="tab"]{{color:{GOLD_LIGHT} !important}}
[data-baseweb="tab-highlight"]{{background-color:{GOLD_LIGHT} !important;box-shadow:0 0 8px {GOLD_LIGHT}}}

/* Textos secundarios (captions) con mejor contraste para lectura */
[data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"]{{color:#ABB7C6 !important;font-size:.86rem !important;line-height:1.5}}

[data-testid="stAlert"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px;color:{TEXT};animation:fadeSlideUp .5s ease-out}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden;animation:fadeSlideUp .5s ease-out}}
[data-testid="stExpander"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px}}
[data-testid="stExpander"] summary{{color:{STEEL_LIGHT} !important;font-weight:600}}
[data-testid="stForm"]{{background:{PANEL};border:1px solid {BORDER};border-radius:14px;padding:6px}}
[data-testid="stJson"]{{background:{PANEL_SOLID} !important;border:1px solid {BORDER};border-radius:10px}}
[data-testid="stCodeBlock"]{{background:transparent !important}}
[data-testid="stCodeBlock"] pre{{background:{PANEL_SOLID} !important;border:1px solid {BORDER} !important;border-radius:10px !important}}
[data-testid="stCodeBlock"] code{{color:{TEXT} !important;background:transparent !important}}

button[kind="primary"], [data-testid="stFormSubmitButton"] button, [data-testid="baseButton-primary"]{{
    background:linear-gradient(135deg,{GOLD},{GOLD_LIGHT}) !important;color:#0A0B0F !important;
    font-weight:700 !important;border:none !important;border-radius:10px !important;
    transition:transform .2s ease,box-shadow .2s ease}}
button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover{{transform:translateY(-2px);box-shadow:0 10px 22px rgba(227,167,62,.35)}}
[data-testid="stDownloadButton"] button{{background:{PANEL} !important;color:{STEEL_LIGHT} !important;
    border:1px solid {BORDER} !important;border-radius:10px !important}}

[data-testid="stNumberInput"] input, [data-testid="stTextInput"] input{{
    background:{PANEL_SOLID} !important;color:{TEXT} !important;border:1px solid {BORDER} !important}}
[data-testid="stSelectbox"]{{background:{PANEL} !important;border:1px solid {BORDER} !important;border-radius:8px}}
[data-testid="stSelectbox"] div{{background:transparent !important}}
[data-testid="stSelectbox"] *{{color:{TEXT} !important}}
[data-baseweb="popover"],[data-baseweb="menu"]{{background:{PANEL_SOLID} !important}}
[data-baseweb="popover"] *,[data-baseweb="menu"] *{{color:{TEXT} !important}}
li[role="option"]{{background:{PANEL_SOLID} !important;color:{TEXT} !important}}
li[role="option"]:hover{{background:rgba(255,255,255,.08) !important}}

[data-testid="stRadio"] label{{color:{TEXT} !important}}
[data-testid="stProgress"] > div > div{{background:linear-gradient(90deg,{GOLD},{STEEL}) !important}}

[data-testid="stVerticalBlockBorderWrapper"]{{transition:transform .25s ease,box-shadow .25s ease}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{transform:translateY(-2px)}}

@media(max-width:800px){{.block-container{{padding:1.2rem}}}}
</style>""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    title_font=dict(size=17, color=GOLD_LIGHT, family='Playfair Display'),
    xaxis=dict(gridcolor='rgba(255,255,255,.10)'), yaxis=dict(gridcolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT)), hoverlabel=dict(bgcolor=PANEL_SOLID, font_color=TEXT, bordercolor=BORDER))


def section_title(text: str):
    st.markdown(f'<div class="section-title"><span class="bar"></span>{text}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# Tarjeta KPI dinámica: número que cuenta en vivo, borde con brillo
# giratorio y "shimmer" — misma identidad visual que Procesamiento.
# ------------------------------------------------------------------
_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix="", suffix="", trend_pct=None):
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"

    trend_html = ""
    if trend_pct is not None:
        up = trend_pct >= 0
        tcolor = GREEN if up else RED
        tarrow = "▲" if up else "▼"
        trend_html = (f'<div class="kpi-trend" style="color:{tcolor};background:{tcolor}22;'
                      f'border:1px solid {tcolor}55">{tarrow} {abs(trend_pct):.1f}%</div>')

    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; overflow:visible; }}
      @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
      @property --a{{syntax:'<angle>';initial-value:0deg;inherits:false}}
      @keyframes spin{{to{{--a:360deg}}}}
      @keyframes shimmerSweep{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(220%)}}}}
      @keyframes ringPulse{{0%{{box-shadow:0 0 0 0 rgba(227,167,62,.45)}}70%{{box-shadow:0 0 0 10px rgba(227,167,62,0)}}100%{{box-shadow:0 0 0 0 rgba(227,167,62,0)}}}}
      .kpi-wrap{{position:relative;border-radius:16px;padding:1.5px;
        background:conic-gradient(from var(--a),{accent},transparent 30%,transparent 70%,{accent});
        animation:spin 5s linear infinite,fadeIn .5s ease-out;}}
      .kpi-card{{position:relative;background:linear-gradient(160deg,{PANEL_SOLID},#0d0f15);
        border-radius:14.5px;padding:16px 16px 14px;box-sizing:border-box;overflow:hidden;
        transition:transform .25s ease,box-shadow .25s ease;}}
      .kpi-card:hover{{transform:translateY(-4px);box-shadow:0 14px 30px rgba(0,0,0,.5)}}
      .kpi-card::before{{content:'';position:absolute;top:0;left:-40%;width:30%;height:100%;
        background:linear-gradient(100deg,transparent,rgba(255,255,255,.06),transparent);
        animation:shimmerSweep 3.2s ease-in-out infinite;pointer-events:none}}
      .kpi-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}}
      .kpi-badge{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;
        justify-content:center;font-size:1rem;
        background:radial-gradient(circle,{accent}55,{accent}22);
        animation:ringPulse 2.6s ease-out infinite}}
      .kpi-trend{{font-size:.68rem;font-weight:800;padding:2px 8px;border-radius:999px}}
      .kpi-label{{text-transform:uppercase;letter-spacing:.1em;font-weight:800;font-size:.68rem;
        margin-bottom:6px;color:{accent}}}
      .kpi-value{{font-size:1.6rem;font-weight:800;font-variant-numeric:tabular-nums;
        background:linear-gradient(90deg,{TEXT},{accent});-webkit-background-clip:text;
        background-clip:text;-webkit-text-fill-color:transparent}}
      .kpi-sub{{color:{MUTED};font-size:.72rem;margin-top:4px}}
    </style>
    <div class="kpi-wrap">
      <div class="kpi-card">
        <div class="kpi-top">
          <div class="kpi-badge">{icon}</div>
          {trend_html}
        </div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value"><span id="{uid}">0</span></div>
        <div class="kpi-sub">{subtext}</div>
      </div>
    </div>
    <script>
    (function(){{
      const el = document.getElementById("{uid}");
      const end = {value}; const decimals = {decimals}; const prefix = "{prefix}"; const suffix = "{suffix}";
      const start = performance.now(); const duration = 1300;
      function step(ts){{
        const p = Math.min((ts - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + (eased*end).toLocaleString('es-ES', {{minimumFractionDigits:decimals,maximumFractionDigits:decimals}}) + suffix;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = prefix + end.toLocaleString('es-ES', {{minimumFractionDigits:decimals,maximumFractionDigits:decimals}}) + suffix;
      }}
      requestAnimationFrame(step);
    }})();
    </script>'''
    components.html(html, height=150)


# ─── Banner hero ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero"><div class="eyebrow"><span class="dot"></span>LAVADORA S.A. · INTELIGENCIA COMERCIAL</div>'
    '<h1><span class="hero-icon">🤖</span>Predicción</h1>'
    '<p>Anticipa qué clientes van a volver a comprar y cuáles están en riesgo de abandonar, '
    'a partir de su comportamiento real de compra.</p></div>',
    unsafe_allow_html=True)

# ─── Constantes del modelo ───────────────────────────────────────────────────
CORTE = pd.Timestamp("2023-12-31")
DIAS_RECURRENCIA = 90
DIAS_CHURN = 120
RANDOM_STATE = 42
PRECISION_OBJETIVO = 0.80
CONSUMIDOR_FINAL = "9999999999999"
CV_FOLDS = 3
# Validación cruzada REPETIDA para elegir umbral/modelo sin tocar el TEST: 5 particiones
# x 10 repeticiones = 50 evaluaciones independientes por candidato. Mucho más estable que
# una sola pasada de validación cuando hay pocos clientes.
CV_REPETIDA_SPLITS = 5
CV_REPETIDA_REPEATS = 10
UMBRALES_CANDIDATOS = np.arange(0.35, 0.96, 0.01)

NUMERIC_FEATURES = [
    "recencia", "frecuencia", "monto_total", "ticket_promedio", "antiguedad_dias",
    "productos_unicos", "categorias_unicas", "dias_promedio_entre_compras",
]
CATEGORICAL_FEATURES = ["id_tipo_documento", "genero", "localidad"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
# Recurrencia se enfoca en comportamiento real de compra; evita variables demográficas
# que agregan ruido en datasets pequeños. Churn conserva todas las variables.
RECURRENCIA_FEATURES = [
    "recencia", "frecuencia", "monto_total", "ticket_promedio",
    "antiguedad_dias", "productos_unicos", "categorias_unicas",
    "dias_promedio_entre_compras",
]

# ─── Iconos y descripciones para cada variable ───────────────────────────────
FEATURE_META = {
    "recencia": ("📅", "Recencia", "Días desde la última compra hasta el corte"),
    "frecuencia": ("🔁", "Frecuencia", "Número de transacciones únicas realizadas"),
    "monto_total": ("💰", "Monto Total", "Suma total facturada por el cliente"),
    "ticket_promedio": ("🏷️", "Ticket Promedio", "Promedio de gasto por transacción"),
    "antiguedad_dias": ("⏳", "Antigüedad (días)", "Días desde la primera compra hasta el corte"),
    "productos_unicos": ("📦", "Productos Únicos", "Cantidad de productos distintos comprados"),
    "categorias_unicas": ("🏷️", "Categorías Únicas", "Cantidad de categorías distintas exploradas"),
    "dias_promedio_entre_compras": ("⏱️", "Días Prom. entre Compras", "Promedio de días entre cada transacción"),
    "id_tipo_documento": ("🆔", "Tipo de Documento", "Tipo de identificación del cliente"),
    "genero": ("👤", "Género", "Masculino o Femenino"),
    "localidad": ("📍", "Localidad", "Ubicación geográfica del cliente"),
}

# ─── Mapeo de género legible ─────────────────────────────────────────────────
GENERO_MAP = {"1": "Masculino", "2": "Femenino", "1.0": "Masculino", "2.0": "Femenino"}


def mapear_genero(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte valores numéricos de género a etiquetas legibles."""
    df["genero"] = df["genero"].astype(str).str.strip().map(lambda x: GENERO_MAP.get(x, x))
    return df


# ─── Qué significa "Clase 0" y "Clase 1" en lenguaje simple ─────────────────
# Ojo: el significado se INVIERTE entre recurrencia y churn. En recurrencia,
# Clase 1 = buena noticia (el cliente sigue activo). En churn, Clase 1 = mala
# noticia (el cliente está en riesgo / inactivo). Por eso esto se calcula
# según el objetivo seleccionado, no es un texto fijo.
def etiquetas_clase(objetivo: str) -> dict:
    if objetivo == "recurrencia":
        return {
            1: {"nombre": "Activo", "chip": "clase-activo", "icon": "🟢",
                "desc": f"Volvió a comprar dentro de los {DIAS_RECURRENCIA} días"},
            0: {"nombre": "Inactivo", "chip": "clase-inactivo", "icon": "⚪",
                "desc": f"No compró en los {DIAS_RECURRENCIA} días"},
        }
    return {
        1: {"nombre": "En riesgo / Inactivo", "chip": "clase-inactivo", "icon": "🔴",
            "desc": f"No compró en los {DIAS_CHURN} días — señal de abandono"},
        0: {"nombre": "Activo", "chip": "clase-activo", "icon": "🟢",
            "desc": f"Sí compró en los {DIAS_CHURN} días — cliente conservado"},
    }


def cargar_fuentes() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ventas = query_df("""
        SELECT id_venta, cedula_cliente, fecha_venta::date AS fecha_venta, total
        FROM venta
        WHERE fecha_venta IS NOT NULL AND total IS NOT NULL
          AND cedula_cliente <> :consumidor
    """, {"consumidor": CONSUMIDOR_FINAL})
    detalle = query_df("""
        SELECT dv.id_venta, dv.id_producto, dv.cantidad, p.id_categoria
        FROM detalle_venta dv JOIN producto p ON p.id_producto = dv.id_producto
    """)
    clientes = query_df("""
        SELECT cedula, id_tipo_documento, genero, localidad
        FROM cliente WHERE cedula <> :consumidor
    """, {"consumidor": CONSUMIDOR_FINAL})
    ventas["fecha_venta"] = pd.to_datetime(ventas["fecha_venta"], errors="coerce")
    ventas["total"] = pd.to_numeric(ventas["total"], errors="coerce")
    ventas = ventas.dropna(subset=["fecha_venta", "total", "cedula_cliente"])
    if not detalle.empty:
        detalle["cantidad"] = pd.to_numeric(detalle["cantidad"], errors="coerce")
    clientes = mapear_genero(clientes)
    return ventas, detalle, clientes


def _promedio_dias(grupo: pd.DataFrame) -> float:
    fechas = grupo["fecha_venta"].drop_duplicates().sort_values()
    return float(fechas.diff().dt.days.dropna().mean()) if len(fechas) > 1 else 0.0


def construir_dataset(ventas, detalle, clientes, objetivo: str) -> pd.DataFrame:
    historico = ventas[ventas["fecha_venta"] <= CORTE].copy()
    dias = DIAS_RECURRENCIA if objetivo == "recurrencia" else DIAS_CHURN
    futuro = ventas[(ventas["fecha_venta"] > CORTE) & (ventas["fecha_venta"] <= CORTE + pd.Timedelta(days=dias))]
    base = historico.groupby("cedula_cliente").agg(
        primera_compra=("fecha_venta", "min"), ultima_compra=("fecha_venta", "max"),
        frecuencia=("id_venta", "nunique"), monto_total=("total", "sum"), ticket_promedio=("total", "mean"),
    ).reset_index()
    base["recencia"] = (CORTE - base["ultima_compra"]).dt.days.clip(lower=0)
    base["antiguedad_dias"] = (CORTE - base["primera_compra"]).dt.days.clip(lower=0)
    gaps = historico.groupby("cedula_cliente").apply(_promedio_dias, include_groups=False).rename("dias_promedio_entre_compras")
    base = base.merge(gaps, on="cedula_cliente", how="left")
    d = detalle[detalle["id_venta"].isin(historico["id_venta"])]
    if not d.empty:
        d = d.merge(historico[["id_venta", "cedula_cliente"]], on="id_venta", how="inner")
        base = base.merge(d.groupby("cedula_cliente").agg(productos_unicos=("id_producto", "nunique"), categorias_unicas=("id_categoria", "nunique")).reset_index(), on="cedula_cliente", how="left")
    else:
        base["productos_unicos"], base["categorias_unicas"] = 0, 0
    base = base.merge(clientes, left_on="cedula_cliente", right_on="cedula", how="left").drop(columns="cedula", errors="ignore")
    compro = base["cedula_cliente"].astype(str).isin(set(futuro["cedula_cliente"].astype(str))).astype(int)
    base["target"] = compro if objetivo == "recurrencia" else 1 - compro
    for col in NUMERIC_FEATURES:
        base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0)
    for col in CATEGORICAL_FEATURES:
        base[col] = base[col].fillna("SIN ESPECIFICAR").astype(str)
    return base[["cedula_cliente", *FEATURES, "target"]]


def crear_pipeline(clasificador=None, features=None) -> Pipeline:
    features = features or FEATURES
    numeric = [f for f in features if f in NUMERIC_FEATURES]
    categorical = [f for f in features if f in CATEGORICAL_FEATURES]
    transformers = [("numericas", Pipeline([("imputacion", SimpleImputer(strategy="median")), ("escalado", StandardScaler())]), numeric)]
    if categorical:
        transformers.append(("categoricas", Pipeline([("imputacion", SimpleImputer(strategy="most_frequent")), ("codificacion", OneHotEncoder(handle_unknown="ignore"))]), categorical))
    pre = ColumnTransformer(transformers)
    if clasificador is None:
        clasificador = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE)
    return Pipeline([("preprocesamiento", pre), ("clasificador", clasificador)])


def _umbral_por_cv_repetida(pipeline_ajustado, X, y, umbrales,
                             n_splits=CV_REPETIDA_SPLITS, n_repeats=CV_REPETIDA_REPEATS,
                             random_state=RANDOM_STATE):
    """Evalúa cada umbral candidato con validación cruzada repetida y estratificada.

    Para cada una de las (n_splits x n_repeats) particiones se clona y reentrena el
    pipeline SOLO con los datos de esa partición de entrenamiento, y se predice sobre
    su propio bloque de validación (nunca visto por ese ajuste). Se exige un mínimo de
    predicciones positivas por partición (evita que 1-2 aciertos sueltos disparen una
    "precisión perfecta" espuria), y se exige que el umbral produzca resultados válidos
    en al menos el 80% de las particiones para considerarlo confiable. Devuelve, por
    umbral, la precisión y el recall PROMEDIO junto con su desviación estándar.
    """
    rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
    folds = list(rskf.split(X, y))
    minimo_positivos_por_fold = max(3, int(round(len(X) / n_splits * 0.05)))
    acumulado = {float(u): {"precision": [], "recall": []} for u in umbrales}

    for train_idx, valid_idx in folds:
        modelo = clone(pipeline_ajustado)
        modelo.fit(X.iloc[train_idx], y.iloc[train_idx])
        proba = modelo.predict_proba(X.iloc[valid_idx])[:, 1]
        y_valid = y.iloc[valid_idx]
        for u in umbrales:
            pred = (proba >= u).astype(int)
            if pred.sum() < minimo_positivos_por_fold:
                continue
            acumulado[float(u)]["precision"].append(precision_score(y_valid, pred, zero_division=0))
            acumulado[float(u)]["recall"].append(recall_score(y_valid, pred, zero_division=0))

    total_folds = n_splits * n_repeats
    resumen = []
    for u, valores in acumulado.items():
        if len(valores["precision"]) < total_folds * 0.8:
            continue
        resumen.append({
            "umbral": u,
            "precision": float(np.mean(valores["precision"])),
            "precision_std": float(np.std(valores["precision"])),
            "recall": float(np.mean(valores["recall"])),
            "n_evaluaciones": len(valores["precision"]),
        })
    return resumen


def entrenar(df: pd.DataFrame, objetivo: str) -> dict:
    """Entrena cada objetivo con variables y modelo apropiados.

    División real 80% train / 20% test (holdout único, se usa una sola vez al final).
    El umbral de decisión y la comparación de modelos se resuelven con VALIDACIÓN
    CRUZADA REPETIDA (StratifiedKFold de 5 particiones × 10 repeticiones = 50
    evaluaciones independientes) DENTRO del 80% de train. Esto reemplaza la selección
    por una sola validación (mucho más sensible al azar de una única partición cuando
    hay pocos clientes) y nunca toca el TEST. Para 'recurrencia' se prioriza Random
    Forest sobre Regresión Logística siempre que Random Forest alcance el objetivo de
    precisión, porque en este dataset generaliza mejor a datos nunca vistos aunque su
    precisión nominal de validación sea, a veces, un poco menor que la de la Logística.
    """
    features = RECURRENCIA_FEATURES if objetivo == "recurrencia" else FEATURES
    if df["target"].nunique() < 2 or df["target"].value_counts().min() < 10:
        raise ValueError("No hay suficientes observaciones en ambas clases; se requieren al menos 10 por clase.")

    X_train, X_test, y_train, y_test = train_test_split(
        df[features], df["target"].astype(int), test_size=0.20,
        stratify=df["target"], random_state=RANDOM_STATE
    )

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    modelos = [("Regresión Logística", crear_pipeline(features=features), {"clasificador__C": [0.01, 0.1, 1, 10, 100]})]
    if objetivo == "recurrencia":
        modelos.append((
            "Random Forest",
            crear_pipeline(RandomForestClassifier(
                n_estimators=600, class_weight="balanced_subsample",
                random_state=RANDOM_STATE, n_jobs=-1, min_samples_leaf=2
            ), features=features),
            {"clasificador__max_depth": [3, 5, 8, None], "clasificador__max_features": ["sqrt", 0.7]},
        ))

    candidatos = []
    for nombre, pipeline, params in modelos:
        grid = GridSearchCV(pipeline, params, scoring="roc_auc", cv=cv, n_jobs=-1, refit=True)
        grid.fit(X_train, y_train)

        # Umbral y comparación de modelos resueltos por CV repetida (50 evaluaciones)
        # sobre el 80% de train; el TEST no se usa aquí en absoluto.
        resumen_umbrales = _umbral_por_cv_repetida(grid.best_estimator_, X_train, y_train, UMBRALES_CANDIDATOS)
        for r in resumen_umbrales:
            candidatos.append({
                "cumple": r["precision"] >= PRECISION_OBJETIVO,
                "precision": r["precision"], "precision_std": r["precision_std"],
                "recall": r["recall"], "umbral": r["umbral"],
                "grid": grid, "nombre": nombre,
            })

    if not candidatos:
        raise ValueError("No fue posible generar suficientes predicciones positivas en validación cruzada repetida.")

    if objetivo == "recurrencia":
        # Prioridad explícita a Random Forest si logra el objetivo de precisión en CV repetida.
        candidatos_rf = [c for c in candidatos if c["nombre"] == "Random Forest" and c["cumple"]]
        if candidatos_rf:
            seleccion = max(candidatos_rf, key=lambda c: (c["precision"], c["recall"], -c["precision_std"]))
        else:
            validos = [c for c in candidatos if c["cumple"]]
            seleccion = max(validos or candidatos, key=lambda c: (c["cumple"], c["precision"], c["recall"], -c["precision_std"]))
    else:
        validos = [c for c in candidatos if c["cumple"]]
        seleccion = max(validos or candidatos, key=lambda c: (c["cumple"], c["precision"], c["recall"], -c["precision_std"]))

    if seleccion["nombre"] == "Random Forest":
        modelo = crear_pipeline(RandomForestClassifier(
            n_estimators=600, class_weight="balanced_subsample",
            random_state=RANDOM_STATE, n_jobs=-1, min_samples_leaf=2
        ), features=features)
    else:
        modelo = crear_pipeline(features=features)
    modelo.set_params(**seleccion["grid"].best_params_)
    modelo.fit(X_train, y_train)  # se entrena con el 80% completo (train), test queda intacto
    proba_test = modelo.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= seleccion["umbral"]).astype(int)
    metrics = {
        "accuracy": accuracy_score(y_test, pred_test),
        "precision": precision_score(y_test, pred_test, zero_division=0),
        "recall": recall_score(y_test, pred_test, zero_division=0),
        "f1": f1_score(y_test, pred_test, zero_division=0),
        "roc_auc": roc_auc_score(y_test, proba_test),
    }
    return {
        "modelo": modelo, "grid": seleccion["grid"], "X_test": X_test,
        "y_test": y_test, "y_pred": pred_test, "y_proba": proba_test,
        "umbral": seleccion["umbral"], "modelo_nombre": seleccion["nombre"],
        "features": features,
        "precision_cv": seleccion["precision"], "precision_cv_std": seleccion["precision_std"],
        "recall_cv": seleccion["recall"],
        "precision_objetivo_cumplido": bool(seleccion["precision"] >= PRECISION_OBJETIVO),
        "metrics": metrics,
    }


def mostrar_variables(df: pd.DataFrame, objetivo: str) -> None:
    st.subheader("📊 Variables del Modelo")
    st.caption("Variables calculadas con datos históricos hasta el 31/12/2023. El consumidor final genérico se excluye.")

    features_usadas = RECURRENCIA_FEATURES if objetivo == "recurrencia" else FEATURES

    # ─── 1) Variables Predictoras (X) — primero, porque son el punto de partida ───
    section_title("🛠️ Variables Predictoras (X)")
    st.caption("Estas son las características que el modelo usa para hacer la predicción.")
    if objetivo == "recurrencia":
        st.caption("🌲 Recurrencia entrena solo con variables de comportamiento de compra (sin demográficas) para reducir ruido.")

    numericas_usadas = [f for f in NUMERIC_FEATURES if f in features_usadas]
    st.markdown("**📊 Numéricas**")
    cols_per_row = 4
    for i in range(0, len(numericas_usadas), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, feat in enumerate(numericas_usadas[i:i+cols_per_row]):
            icon, name, desc = FEATURE_META[feat]
            with cols[j]:
                st.markdown(f"""
                <div class="var-card">
                    <span class="var-icon">{icon}</span><span class="var-name">{name}</span>
                    <div class="var-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

    categoricas_usadas = [f for f in CATEGORICAL_FEATURES if f in features_usadas]
    if categoricas_usadas:
        st.markdown("**🏷️ Categóricas**")
        cols = st.columns(len(categoricas_usadas))
        for j, feat in enumerate(categoricas_usadas):
            icon, name, desc = FEATURE_META[feat]
            with cols[j]:
                st.markdown(f"""
                <div class="var-card">
                    <span class="var-icon">{icon}</span><span class="var-name">{name}</span>
                    <div class="var-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.caption("Sin variables categóricas para este objetivo.")

    # ─── 2) Variable Objetivo (Y) — después, ya con el contexto de las X ───
    section_title("🎯 Variable Objetivo (Y)")
    etiquetas = etiquetas_clase(objetivo)
    e1, e0 = etiquetas[1], etiquetas[0]
    if objetivo == "recurrencia":
        y_desc = f"El cliente <strong>compró</strong> en los {DIAS_RECURRENCIA} días posteriores al corte (31/12/2023)."
        y_zero = "No compró en ese periodo."
    else:
        y_desc = f"El cliente <strong>no compró</strong> en los {DIAS_CHURN} días posteriores al corte (31/12/2023)."
        y_zero = "Sí compró en ese periodo."

    st.markdown(f"""
    <div class="objetivo-box">
        <h4>🎯 Variable Objetivo (Y): <code>{objetivo}</code></h4>
        <p>
        <span class="clase-chip {e1['chip']}">{e1['icon']} Clase 1 · {e1['nombre']}</span><br>
        {y_desc}<br><br>
        <span class="clase-chip {e0['chip']}">{e0['icon']} Clase 0 · {e0['nombre']}</span><br>
        {y_zero}
        </p>
    </div>
    """, unsafe_allow_html=True)
    if objetivo == "churn":
        st.info("⚠️ Ojo: en el modelo de **Churn** la lógica se invierte respecto a Recurrencia — aquí Clase 1 es la mala noticia (cliente en riesgo), no la buena.")

    with st.expander("📊 Ver distribución de la variable objetivo"):
        balance = df["target"].value_counts().rename_axis("clase").reset_index(name="registros")
        balance["etiqueta"] = balance["clase"].map(lambda c: f"{etiquetas[c]['icon']} {etiquetas[c]['nombre']} (Clase {c})")
        fig = px.bar(balance, x="etiqueta", y="registros", color="etiqueta", color_discrete_sequence=[STEEL_LIGHT, GOLD_LIGHT])
        fig.update_traces(marker_line_width=1, marker_line_color=PANEL_SOLID)
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)


def mostrar_evaluacion(resultado: dict, objetivo: str) -> None:
    # ─── Confirmación secundaria: una sola partición de TEST nunca vista ───
    st.markdown("**🔒 Confirmación en TEST (20%, una sola partición nunca vista durante el entrenamiento)**")
    st.caption("Con pocos clientes, una sola partición de test tiene alta varianza estadística. Se muestra como confirmación adicional, no como la cifra principal.")
    labels = [("Accuracy", "accuracy", "🎯", GOLD_LIGHT), ("Precision", "precision", "🔍", STEEL_LIGHT),
              ("Recall", "recall", "📡", "#3FA6A6"), ("F1-Score", "f1", "⚖️", GREEN), ("ROC-AUC", "roc_auc", "📈", GOLD)]
    cols = st.columns(5)
    for col, (label, key, icon, accent) in zip(cols, labels):
        with col:
            kpi_counter(icon, label, resultado['metrics'][key] * 100, "", accent, decimals=1, suffix="%")
    st.caption(f"80% entrenamiento · 20% prueba · {resultado['X_test'].shape[0]} clientes en TEST · Modelo: {resultado['modelo_nombre']} · CV ROC-AUC (GridSearchCV): {resultado['grid'].best_score_:.3f}")

    a, b = st.columns(2)
    with a:
        cm = confusion_matrix(resultado["y_test"], resultado["y_pred"], labels=[0, 1])
        fig = go.Figure(go.Heatmap(z=cm, x=["Predicho 0", "Predicho 1"], y=["Real 0", "Real 1"], text=cm, texttemplate="%{text}",
            colorscale=[[0, "#12141B"], [0.5, STEEL], [1, GOLD_LIGHT]], showscale=False, textfont=dict(color=TEXT, size=18)))
        fig.update_layout(title="Matriz de confusión", height=360, **PLOTLY_LAYOUT)
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)
    with b:
        fpr, tpr, _ = roc_curve(resultado["y_test"], resultado["y_proba"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"Modelo AUC={resultado['metrics']['roc_auc']:.2f}",
            line={"color": GOLD_LIGHT, "width": 4}, fill="tozeroy", fillcolor="rgba(245,207,122,.12)"))
        fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Azar", line={"color": MUTED, "dash": "dash"}))
        fig.update_layout(title="Curva ROC", height=360, **PLOTLY_LAYOUT)
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)

    report = pd.DataFrame(classification_report(resultado["y_test"], resultado["y_pred"], target_names=["Clase 0", "Clase 1"], output_dict=True)).T.reset_index().rename(columns={"index": "Clase"})
    with st.expander("📄 Ver reporte de clasificación completo", expanded=False):
        st.dataframe(report.round(3), hide_index=True, use_container_width=True)

    with st.expander("Diagnóstico de probabilidades"):
        dist = pd.DataFrame({"probabilidad": resultado["y_proba"]})
        counts, edges = np.histogram(dist.probabilidad, bins=25, range=(0, 1))
        centers = (edges[:-1] + edges[1:]) / 2
        fig = go.Figure(go.Bar(x=centers, y=counts, marker=dict(color=centers, colorscale=[[0, STEEL], [0.5, "#3FA6A6"], [1, GOLD_LIGHT]],
            line=dict(width=1, color=PANEL_SOLID))))
        fig.update_layout(title="Distribución de probabilidades predichas", xaxis_title="Probabilidad", yaxis_title="Frecuencia", **PLOTLY_LAYOUT)
        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)
        st.write(f"Mínimo: {dist.probabilidad.min():.4f} · Máximo: {dist.probabilidad.max():.4f} · Desviación: {dist.probabilidad.std():.4f}")


def laboratorio(resultado: dict, df: pd.DataFrame, objetivo: str) -> None:
    st.subheader("🔮 Laboratorio de predicción")
    st.caption("Selecciona un cliente real para probar el modelo con sus variables históricas, o ajusta los valores en el formulario.")
    clientes = query_df("SELECT cedula, nombre, apellido FROM cliente WHERE cedula <> :consumer", {"consumer": CONSUMIDOR_FINAL})
    clientes["nombre_completo"] = (clientes.nombre.fillna("").astype(str).str.strip() + " " + clientes.apellido.fillna("").astype(str).str.strip()).str.strip()
    disponibles = df.merge(clientes[["cedula", "nombre_completo"]], left_on="cedula_cliente", right_on="cedula", how="left").drop_duplicates("cedula_cliente").sort_values("nombre_completo")
    disponibles["etiqueta"] = disponibles.apply(lambda r: f"{r.nombre_completo or 'Sin nombre'} · {r.cedula_cliente}", axis=1)
    opciones = disponibles["etiqueta"].tolist()
    elegido = st.selectbox("👤 Cliente real", opciones, key=f"selector_{objetivo}")
    fila = disponibles[disponibles.etiqueta == elegido].iloc[0]

    with st.form(f"formulario_{objetivo}"):
        st.markdown(f"""
        <div class="client-card">
            <span style="font-size:1.2rem;">👤</span>
            <strong>{fila['nombre_completo'] or 'Sin nombre'}</strong>
            <span>Cédula: <code>{fila['cedula_cliente']}</code></span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**📊 Variables Numéricas**")
        entradas = {}
        c1, c2, c3 = st.columns(3)
        for idx, feature in enumerate(NUMERIC_FEATURES):
            icon, label, _ = FEATURE_META[feature]
            target_col = [c1, c2, c3][idx % 3]
            with target_col:
                entradas[feature] = st.number_input(
                    f"{icon} {label}",
                    min_value=0.0,
                    value=float(fila[feature]),
                    step=1.0,
                    format="%.0f",
                    key=f"{objetivo}_{feature}"
                )

        st.markdown(f"**🏷️ Variables Categóricas**")
        cat_cols = st.columns(3)
        for idx, feature in enumerate(CATEGORICAL_FEATURES):
            icon, label, _ = FEATURE_META[feature]
            opciones_cat = sorted(df[feature].astype(str).unique().tolist())
            actual = str(fila[feature])
            default = opciones_cat.index(actual) if actual in opciones_cat else 0
            with cat_cols[idx]:
                entradas[feature] = st.selectbox(f"{icon} {label}", opciones_cat, index=default, key=f"{objetivo}_{feature}")

        ejecutar = st.form_submit_button("🔮 Ejecutar predicción", type="primary", use_container_width=True)

    if ejecutar:
        # El pipeline solo toma las columnas con las que fue entrenado (resultado["features"]);
        # el resto de columnas del formulario se ignoran de forma segura por el ColumnTransformer.
        entrada = pd.DataFrame([entradas], columns=FEATURES)
        prob = float(resultado["modelo"].predict_proba(entrada)[:, 1][0])
        positivo = prob >= resultado["umbral"]
        etiquetas = etiquetas_clase(objetivo)
        st.markdown("---")
        st.markdown("### 🎯 Resultado de la Predicción")
        r1, r2 = st.columns([1, 2])
        with r1:
            st.metric("📊 Probabilidad", f"{prob:.1%}", f"umbral {resultado['umbral']:.0%}")
        with r2:
            clase_predicha = etiquetas[1] if positivo else etiquetas[0]
            if objetivo == "recurrencia":
                if positivo:
                    st.success(f"🟢 Cliente potencialmente **{clase_predicha['nombre'].lower()}** — recurrente")
                else:
                    st.error(f"🔴 Baja probabilidad de recurrencia — cliente **{clase_predicha['nombre'].lower()}**")
            else:
                if positivo:
                    st.error(f"🔴 Alto riesgo de abandono — cliente **{clase_predicha['nombre'].lower()}**")
                else:
                    st.success(f"🟢 Bajo riesgo de abandono — cliente **{clase_predicha['nombre'].lower()}**")
        st.progress(prob)
        with st.expander("📝 Ver datos de entrada utilizados"):
            st.dataframe(entrada, hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
try:
    ventas, detalle, clientes = cargar_fuentes()
    if ventas.empty:
        st.warning("No existen ventas válidas para construir los modelos.")
    else:
        st.info("📆 Diseño temporal: observación hasta 31/12/2023. Recurrencia usa 90 días futuros y churn usa 120 días futuros. El consumidor final no se modela.")
        objetivo = st.radio("Selecciona el modelo", ["recurrencia", "churn"], format_func=lambda x: "🧾 Recurrencia" if x == "recurrencia" else "⚠️ Churn", horizontal=True)
        df = construir_dataset(ventas, detalle, clientes, objetivo)
        etiquetas = etiquetas_clase(objetivo)

        # ─── TARJETAS MÉTRICAS ARRIBA (antes de los tabs) ────────────────────
        balance = df.target.value_counts()
        e1, e0 = etiquetas[1], etiquetas[0]
        cards = st.columns(3)
        with cards[0]:
            kpi_counter("👥", "CLIENTES MODELABLES", len(df), "Consumidor final excluido", STEEL_LIGHT)
        with cards[1]:
            kpi_counter(e1["icon"], f"CLASE 1 · {e1['nombre']}", int(balance.get(1, 0)), e1["desc"],
                        GREEN if e1["chip"] == "clase-activo" else RED)
        with cards[2]:
            kpi_counter(e0["icon"], f"CLASE 0 · {e0['nombre']}", int(balance.get(0, 0)), e0["desc"],
                        GREEN if e0["chip"] == "clase-activo" else RED)

        # ─── TABS ────────────────────────────────────────────────────────────
        tabs = st.tabs(["📘 Entender el modelo", "⚙️ Entrenamiento", "📊 Evaluación", "🔮 Probar predicción"])
        with tabs[0]:
            mostrar_variables(df, objetivo)
        with tabs[1]:
            st.markdown("**⚙️ Configuración aplicada**")
            st.write(
                f"Recurrencia: 8 variables de comportamiento, comparando Regresión Logística vs Random Forest "
                f"(se prioriza Random Forest si alcanza el objetivo de precisión). Churn: variables completas + "
                f"Regresión Logística. División real 80% entrenamiento / 20% prueba. El umbral de decisión y la "
                f"comparación de modelos se deciden con validación cruzada repetida ({CV_REPETIDA_SPLITS} "
                f"particiones × {CV_REPETIDA_REPEATS} repeticiones = 50 evaluaciones) dentro del 80%, sin usar "
                f"el test en ningún momento."
            )
            if st.button("🚀 Entrenar / reentrenar modelo", type="primary", key=f"entrenar_{objetivo}"):
                with st.spinner("Separando datos 80/20 y ajustando el modelo..."):
                    try:
                        st.session_state[f"resultado_{objetivo}"] = entrenar(df, objetivo)
                        st.success("✅ Modelo entrenado correctamente.")
                    except Exception as exc:
                        st.error("No fue posible entrenar el modelo con los datos disponibles.")
                        st.exception(exc)
            if f"resultado_{objetivo}" in st.session_state:
                st.json({k.replace("clasificador__", ""): v for k, v in st.session_state[f"resultado_{objetivo}"]["grid"].best_params_.items()})
        resultado = st.session_state.get(f"resultado_{objetivo}")
        with tabs[2]:
            if resultado:
                mostrar_evaluacion(resultado, objetivo)
            else:
                st.info("Entrena el modelo para ver métricas reales, matriz de confusión, curva ROC y reporte de clasificación.")
        with tabs[3]:
            if resultado:
                laboratorio(resultado, df, objetivo)
            else:
                st.info("Primero entrena el modelo. Después podrás seleccionar un cliente real y cambiar los predictores antes de ejecutar la predicción.")
        if resultado:
            with st.expander("⬇️ Exportar resultados"):
                out = resultado["X_test"].copy()
                out["real"] = resultado["y_test"]
                out["predicho"] = resultado["y_pred"]
                out["probabilidad"] = resultado["y_proba"]
                st.download_button("💾 Descargar predicciones TEST", out.to_csv(index=False).encode("utf-8"), f"predicciones_{objetivo}.csv", "text/csv")
                buf = io.BytesIO()
                joblib.dump(resultado["modelo"], buf)
                st.download_button("💾 Descargar modelo .joblib", buf.getvalue(), f"modelo_{objetivo}.joblib", "application/octet-stream")
except Exception:
    st.error("No fue posible cargar el módulo de Predicción. Revisa la conexión y las tablas reales.")
    with st.expander("Detalle técnico"):
        st.code(traceback.format_exc())

# Pie de página (autoría), agregado automáticamente
show_footer()