"""Score Inteligente de LubriInsight.
Salud operativa del negocio y segmentación dinámica de clientes.
Adaptado a Lubricadora.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from utils.database import query_df
from utils.footer import show_footer

# ═══ CONFIGURACIÓN ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="LubriInsight | Score Inteligente", page_icon="⭐", layout="wide", initial_sidebar_state="expanded")

BG = "#0A0B0F"
PANEL = "rgba(255,255,255,0.045)"
PANEL_SOLID = "#12141B"
BORDER = "rgba(255,255,255,0.10)"
GOLD = "#E3A73E"
GOLD_LIGHT = "#F5CF7A"
STEEL = "#4F8FC4"
STEEL_LIGHT = "#9CC9EC"
TEAL = "#3FBFA6"
ROSE = "#E88AA8"
TEXT = "#F3F5F8"
MUTED = "#A6B2C0"
GREEN = "#34D399"
RED = "#F0655D"
CONSUMER = "9999999999999"

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
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(227,167,62,.12),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(79,143,196,.10),transparent 40%),{BG};
        overflow-x:hidden;}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}
.block-container{{max-width:1400px;padding:2rem 3rem 4rem;overflow:visible}}
h1,h2,h3{{color:{TEXT};letter-spacing:-.02em;font-family:'Playfair Display',serif;overflow-wrap:break-word}}
p, span, div, label{{color:{TEXT}}}

@keyframes fadeSlideUp{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes softPulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}

.hero{{background:linear-gradient(160deg,#14161F 0%,#0A0B0F 75%);border:1px solid rgba(227,167,62,.28);
    border-radius:22px;padding:32px 36px;margin-bottom:26px;box-shadow:0 18px 46px rgba(0,0,0,.55);
    animation:fadeSlideUp .55s ease-out;width:100%;overflow:hidden}}
.hero h1{{margin:0 0 10px;font-size:clamp(1.6rem,2.6vw,2.6rem);line-height:1.15;
    background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;
    white-space:normal;overflow-wrap:break-word;max-width:100%}}
.hero p{{color:{MUTED};max-width:75ch;font-size:1.02rem;margin:0;line-height:1.55}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:.72rem;color:{GOLD};margin-bottom:12px}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:16px;padding:18px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

.section{{margin:34px 0 16px}}.section h2{{margin-bottom:4px}}.muted{{color:{MUTED}}}

.chart-title{{font-family:'Playfair Display',serif;color:{GOLD_LIGHT};font-size:1.15rem;
    font-weight:700;margin:2px 0 10px 6px}}

[data-baseweb="tab-list"]{{border-bottom:1px solid {BORDER}}}
[data-baseweb="tab"]{{color:{MUTED};font-weight:500}}
[aria-selected="true"][data-baseweb="tab"]{{color:{GOLD_LIGHT} !important}}

[data-testid="stAlert"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px;color:{TEXT}}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden}}
[data-testid="stExpander"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px}}
[data-testid="stExpander"] summary{{color:{STEEL_LIGHT} !important;font-weight:600}}

[data-testid="stSelectbox"]{{background:{PANEL} !important;border:1px solid {BORDER} !important;border-radius:8px}}
[data-testid="stSelectbox"] div{{background:transparent !important}}
[data-testid="stSelectbox"] *{{color:{TEXT} !important}}
[data-baseweb="popover"],[data-baseweb="menu"]{{background:{PANEL_SOLID} !important}}
[data-baseweb="popover"] *,[data-baseweb="menu"] *{{color:{TEXT} !important}}
li[role="option"]{{background:{PANEL_SOLID} !important;color:{TEXT} !important}}
li[role="option"]:hover{{background:rgba(255,255,255,.08) !important}}

[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]{{background:{GOLD_LIGHT} !important}}

/* Tarjeta destacada para gráficos: crece suave al entrar, se eleva al pasar el mouse */
[data-testid="stVerticalBlockBorderWrapper"]{{background:linear-gradient(160deg,rgba(227,167,62,.07),rgba(255,255,255,.015));
    border:1px solid rgba(227,167,62,.25) !important;border-radius:16px !important;
    box-shadow:0 14px 32px rgba(0,0,0,.45);padding:8px;
    animation:fadeSlideUp .6s ease-out;transition:transform .25s ease,box-shadow .25s ease}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{transform:translateY(-3px);box-shadow:0 20px 40px rgba(0,0,0,.55)}}
@media(max-width:900px){{.block-container{{padding:1.2rem}}
  .hero h1{{font-size:1.7rem}}}}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">LAVADORA S.A. · INTELIGENCIA COMERCIAL</div>'
            '<h1>⭐ Score Inteligente</h1>'
            '<p>Descubre qué tan saludable está tu negocio, qué área necesita atención y cómo podría '
            'mejorar su desempeño.</p></div>', unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    xaxis=dict(gridcolor='rgba(255,255,255,.10)'), yaxis=dict(gridcolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT)), hoverlabel=dict(bgcolor=PANEL_SOLID, font_color=TEXT, bordercolor=BORDER))
SEGMENT_COLORS = [GOLD_LIGHT, STEEL_LIGHT, TEAL, ROSE, GOLD, MUTED]


def chart_title(text: str):
    """Título propio en HTML (no depende del render interno de Plotly, así nunca se corta ni desaparece)."""
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix="", suffix="", delta=None):
    """Tarjeta KPI profesional: número que cuenta en vivo desde 0, con delta opcional (verde/rojo)."""
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"
    if delta is not None:
        d_color = GREEN if delta >= 0 else RED
        d_arrow = "▲" if delta >= 0 else "▼"
        sub_html = f'<div class="kpi-delta" style="color:{d_color};">{d_arrow} {abs(delta):.1f} pts vs. actual</div>'
    else:
        sub_html = f'<div class="kpi-sub">{subtext}</div>'
    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; }}
      @keyframes fadeIn {{ from {{opacity:0; transform:translateY(8px);}} to {{opacity:1; transform:translateY(0);}} }}
      .kpi-card {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:15px; padding:16px 16px 14px;
        box-shadow:0 8px 22px rgba(0,0,0,.35); border-top:3px solid {accent}; box-sizing:border-box;
        height:100%; min-height:118px; display:flex; flex-direction:column; justify-content:center;
        animation:fadeIn .5s ease-out; transition:transform .2s ease; }}
      .kpi-card:hover {{ transform:translateY(-2px); }}
      .kpi-badge {{ width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:1rem; margin-bottom:8px; flex-shrink:0;
        background:radial-gradient(circle,{accent}55,{accent}22); }}
      .kpi-label {{ text-transform:uppercase; letter-spacing:.09em; font-weight:800; font-size:.68rem;
        margin-bottom:6px; color:{accent}; }}
      .kpi-value {{ font-size:1.55rem; font-weight:800; color:{TEXT}; font-variant-numeric:tabular-nums; line-height:1.2 }}
      .kpi-sub {{ color:{MUTED}; font-size:.72rem; margin-top:5px; line-height:1.35; word-wrap:break-word }}
      .kpi-delta {{ font-size:.74rem; margin-top:5px; font-weight:700; line-height:1.35; white-space:nowrap; }}
    </style>
    <div class="kpi-card">
      <div class="kpi-badge">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value"><span id="{uid}">0</span></div>
      {sub_html}
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


_gauge_id = [0]
def animated_gauge(score, level_label, level_color):
    """Velocímetro animado (SVG+JS autocontenido): el arco y el número suben desde 0 al cargar.
    Canvas ampliado y etiquetas con anclaje seguro para que nada se corte en los bordes."""
    import math
    _gauge_id[0] += 1
    uid = f"gauge{_gauge_id[0]}"
    R, SW = 90, 20
    C = 2 * math.pi * R
    half_c = C / 2
    VW, VH = 300, 175          # viewBox con margen extra de seguridad a los lados
    cx, cy = VW / 2, 130
    label_r = R + SW / 2 + 14
    bands = [(0, 45, RED), (45, 65, GOLD), (65, 85, STEEL), (85, 100, GREEN)]
    band_svg = ""
    for a, b, color in bands:
        band_len = (b - a) / 100 * half_c
        offset = -(a / 100 * half_c)
        band_svg += (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{color}" stroke-opacity="0.30" '
                     f'stroke-width="{SW}" stroke-dasharray="{band_len} {C-band_len}" '
                     f'stroke-dashoffset="{offset}" transform="rotate(180 {cx} {cy})" stroke-linecap="butt"/>')
    ticks_svg = ""
    for v in [0, 45, 65, 85, 100]:
        ang = math.radians(180 - (v / 100) * 180)
        tx, ty = cx + label_r * math.cos(ang), cy - label_r * math.sin(ang)
        anchor = "middle"
        if v == 0:
            anchor, tx = "start", tx + 4
        elif v == 100:
            anchor, tx = "end", tx - 4
        ticks_svg += (f'<text x="{tx}" y="{ty}" fill="{MUTED}" font-size="12" font-weight="600" '
                      f'text-anchor="{anchor}" dominant-baseline="middle" '
                      f'stroke="{BG}" stroke-width="4" paint-order="stroke" stroke-linejoin="round">{v}</text>')
    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; overflow:visible; }}
      .gauge-wrap {{ display:flex; flex-direction:column; align-items:center; width:100%; }}
      .gauge-svg-box {{ position:relative; width:100%; max-width:340px; }}
      .gauge-svg-box svg {{ width:100%; height:auto; display:block; overflow:visible; }}
      .gauge-number {{ font-size:2.5rem; font-weight:800; color:{GOLD_LIGHT}; margin-top:-22px;
        font-variant-numeric:tabular-nums; text-shadow:0 2px 10px rgba(227,167,62,.35); }}
      .gauge-level {{ display:flex; align-items:center; gap:8px; font-family:'Playfair Display',serif;
        font-size:1.25rem; color:{TEXT}; margin-top:4px; }}
      .gauge-dot {{ width:12px; height:12px; border-radius:50%; background:{level_color};
        box-shadow:0 0 10px {level_color}; animation:softPulse 2s ease-in-out infinite; flex-shrink:0; }}
      @keyframes softPulse{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
    </style>
    <div class="gauge-wrap">
      <div class="gauge-svg-box">
        <svg viewBox="0 0 {VW} {VH}" xmlns="http://www.w3.org/2000/svg">
          {band_svg}
          <circle id="{uid}-fill" cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{GOLD_LIGHT}"
            stroke-width="{SW}" stroke-dasharray="0 {C}" transform="rotate(180 {cx} {cy})" stroke-linecap="round"/>
          {ticks_svg}
        </svg>
      </div>
      <div class="gauge-number"><span id="{uid}-num">0</span>/100</div>
      <div class="gauge-level"><span class="gauge-dot"></span>{level_label}</div>
    </div>
    <script>
    (function(){{
      const fillArc = document.getElementById("{uid}-fill");
      const numEl = document.getElementById("{uid}-num");
      const target = {score};
      const halfC = {half_c};
      const start = performance.now();
      const duration = 1600;
      function step(ts){{
        const p = Math.min((ts - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = eased * target;
        const arcLen = (val / 100) * halfC;
        fillArc.setAttribute("stroke-dasharray", arcLen + " " + ({C} - arcLen));
        numEl.textContent = val.toFixed(1);
        if (p < 1) requestAnimationFrame(step);
        else numEl.textContent = target.toFixed(1);
      }}
      requestAnimationFrame(step);
    }})();
    </script>'''
    components.html(html, height=240)


# ═══ FUNCIONES DE CÁLCULO ═════════════════════════════════════════════════════════

def nivel_de_score(score: float) -> tuple[str, str]:
    """Retorna (nivel_texto, estado_css) según el score 0-100."""
    if score >= 85:
        return "Excelente", "success"
    elif score >= 65:
        return "Favorable", "success"
    elif score >= 45:
        return "En atención", "warning"
    return "Crítico", "risk"


def score_desde_cartera(pct_recurrente: float, pct_churn: float) -> float:
    """Score de cartera: premia recurrencia, penaliza churn."""
    return max(0, min(100, pct_recurrente * 70 + (1 - pct_churn) * 30))


def score_desde_inventario(pct_critico: float) -> float:
    """Score de inventario: penaliza productos en stock crítico."""
    return max(0, min(100, (1 - pct_critico) * 100))


def score_desde_tendencia(crecimiento: float) -> float:
    """Score de tendencia: mapea crecimiento [-50%,+50%] a [0,100]."""
    return max(0, min(100, 50 + crecimiento * 100))


def calcular_score_total(pilares: dict[str, float], pesos: dict[str, float]) -> float:
    """Promedio ponderado de los pilares."""
    return sum(pilares[k] * pesos[k] for k in pilares)


# ═══ CARGA DE DATOS ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def cargar_ventas() -> pd.DataFrame:
    df = query_df("""
        SELECT id_venta, cedula_cliente, fecha_venta::date AS fecha_venta, total
        FROM venta WHERE total IS NOT NULL AND cedula_cliente <> :consumer
    """, {"consumer": CONSUMER})
    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    return df.dropna(subset=["fecha_venta", "total"])


@st.cache_data(ttl=300)
def cargar_inventario() -> pd.DataFrame:
    return query_df("""
        SELECT i.id_inventario, i.id_producto, p.nombre AS producto,
               i.stock_actual, i.stock_minimo, i.stock_maximo,
               i.punto_reorden, i.estado_stock
        FROM inventario i JOIN producto p ON p.id_producto = i.id_producto
    """)


def construir_rfm(ventas: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla RFM por cliente."""
    hoy = ventas["fecha_venta"].max()
    rfm = ventas.groupby("cedula_cliente").agg(
        recencia=("fecha_venta", lambda x: (hoy - x.max()).days),
        frecuencia=("id_venta", "nunique"),
        monto=("total", "sum"),
    ).reset_index()
    return rfm


SEGMENT_DESC = {
    "🏆 Mejores clientes": "Compran seguido, gastan más que el promedio y compraron hace poco. Tu grupo más valioso.",
    "💙 Clientes frecuentes": "Compran con regularidad y siguen activos, aunque no son los que más gastan.",
    "🌱 Clientes nuevos": "Compraron hace poco pero todavía tienen pocas compras o gasto bajo — recién empiezan.",
    "⚠️ Se están perdiendo": "Antes gastaban bien, pero ya llevan bastante tiempo sin volver a comprar. Riesgo de perderlos.",
    "💤 Clientes inactivos": "Llevan mucho tiempo sin comprar y su gasto histórico es bajo.",
}

# Color fijo por segmento: el mismo color se usa en la tabla, el donut y el scatter,
# para que un cliente se identifique igual sin importar en qué gráfico lo veas.
SEGMENT_COLOR_MAP = {
    "🏆 Mejores clientes": GOLD_LIGHT,
    "💙 Clientes frecuentes": STEEL_LIGHT,
    "🌱 Clientes nuevos": TEAL,
    "⚠️ Se están perdiendo": RED,
    "💤 Clientes inactivos": MUTED,
}
_FALLBACK_COLORS = [ROSE, GOLD, "#8E7CC3", "#6FCF97"]


def color_de_segmento(etiqueta: str, extra_idx: list[str]) -> str:
    """Devuelve el color fijo del segmento, o uno de la paleta de respaldo si es un
    grupo adicional (más de 5 clusters) que no tiene color predefinido."""
    if etiqueta in SEGMENT_COLOR_MAP:
        return SEGMENT_COLOR_MAP[etiqueta]
    otros = [e for e in extra_idx if e not in SEGMENT_COLOR_MAP]
    return _FALLBACK_COLORS[otros.index(etiqueta) % len(_FALLBACK_COLORS)]


def etiquetar_clusters(rfm: pd.DataFrame) -> dict:
    """Asigna a cada cluster una etiqueta de negocio según su comportamiento real
    (qué tan reciente, frecuente y valioso es), no solo por el monto promedio.
    Así el nombre del segmento coincide con lo que realmente hacen esos clientes."""
    rec_q1, rec_q2 = rfm["recencia"].quantile([1 / 3, 2 / 3])

    stats = rfm.groupby("segmento").agg(
        recencia=("recencia", "mean"),
        frecuencia=("frecuencia", "mean"),
        monto=("monto", "mean"),
    )
    # "Valor" combinado (frecuencia + monto) normalizado, para no depender de una sola métrica
    val_z = (
        (stats["frecuencia"] - stats["frecuencia"].mean()) / (stats["frecuencia"].std() or 1)
        + (stats["monto"] - stats["monto"].mean()) / (stats["monto"].std() or 1)
    )
    val_q1, val_q2 = val_z.quantile([1 / 3, 2 / 3])

    etiquetas = {}
    for seg, row in stats.iterrows():
        reciente = row["recencia"] <= rec_q1
        medio_reciente = row["recencia"] <= rec_q2
        valor = val_z.loc[seg]
        alto_valor = valor >= val_q2
        bajo_valor = valor <= val_q1

        if reciente and alto_valor:
            etiquetas[seg] = "🏆 Mejores clientes"
        elif reciente and bajo_valor:
            etiquetas[seg] = "🌱 Clientes nuevos"
        elif reciente:
            etiquetas[seg] = "💙 Clientes frecuentes"
        elif medio_reciente and alto_valor:
            etiquetas[seg] = "💙 Clientes frecuentes"
        elif not medio_reciente and alto_valor:
            etiquetas[seg] = "⚠️ Se están perdiendo"
        else:
            etiquetas[seg] = "💤 Clientes inactivos"
    return etiquetas


# ═══ EJECUCIÓN PRINCIPAL ══════════════════════════════════════════════════════════

try:
    ventas = cargar_ventas()
    inventario = cargar_inventario()

    if ventas.empty:
        st.warning("No existen ventas registradas para calcular el Score.")
        st.stop()

    rfm = construir_rfm(ventas)

    # ─── SIDEBAR: Configuración interactiva de pesos ──────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Configuración del Score")
        st.caption("Ajusta la importancia de cada pilar. Los pesos se normalizan automáticamente.")
        w_cartera = st.slider("👥 Peso Clientes", 0, 100, 40, 5)
        w_inventario = st.slider("📦 Peso Inventario", 0, 100, 30, 5)
        w_tendencia = st.slider("📈 Peso Ventas", 0, 100, 30, 5)
        suma_pesos = w_cartera + w_inventario + w_tendencia
        if suma_pesos == 0:
            suma_pesos = 1
        pesos = {
            "cartera": w_cartera / suma_pesos,
            "inventario": w_inventario / suma_pesos,
            "tendencia": w_tendencia / suma_pesos,
        }
        st.markdown(f"""**Distribución actual:**  
        👥 {pesos['cartera']:.0%} | 📦 {pesos['inventario']:.0%} | 📈 {pesos['tendencia']:.0%}""")

        st.markdown("---")
        st.markdown("### 🧩 Segmentación de Clientes")
        auto_k = st.toggle("Elegir segmentos automáticamente", value=True)
        k_manual = st.slider("Número de segmentos", 2, 6, 4, disabled=auto_k)

    # ─── CÁLCULO DE PILARES ───────────────────────────────────────────

    # Pilar Clientes
    dias_churn = 120
    fecha_max = ventas["fecha_venta"].max()
    rfm["es_recurrente"] = rfm["frecuencia"] > 1
    rfm["es_churn"] = rfm["recencia"] > dias_churn
    pct_recurrente = rfm["es_recurrente"].mean()
    pct_churn = rfm["es_churn"].mean()
    score_clientes = score_desde_cartera(pct_recurrente, pct_churn)

    # Pilar Inventario
    if not inventario.empty:
        inventario["stock_actual"] = pd.to_numeric(inventario["stock_actual"], errors="coerce").fillna(0)
        inventario["punto_reorden"] = pd.to_numeric(inventario["punto_reorden"], errors="coerce").fillna(0)
        inventario["es_critico"] = inventario["stock_actual"] <= inventario["punto_reorden"]
        pct_critico = inventario["es_critico"].mean()
    else:
        pct_critico = 0.0
    score_inv = score_desde_inventario(pct_critico)

    # Pilar Tendencia de Ventas
    mensual = ventas.set_index("fecha_venta").resample("ME")["total"].sum().reset_index()
    if len(mensual) >= 4:
        reciente = mensual["total"].iloc[-2:].sum()
        anterior = mensual["total"].iloc[-4:-2].sum()
        crecimiento = (reciente - anterior) / anterior if anterior > 0 else 0.0
    elif len(mensual) >= 2:
        crecimiento = (mensual["total"].iloc[-1] - mensual["total"].iloc[0]) / mensual["total"].iloc[0] if mensual["total"].iloc[0] > 0 else 0.0
    else:
        crecimiento = 0.0
    score_ventas = score_desde_tendencia(crecimiento)

    # Score total
    pilares_scores = {"cartera": score_clientes, "inventario": score_inv, "tendencia": score_ventas}
    score_total = calcular_score_total(pilares_scores, pesos)
    nivel, estado = nivel_de_score(score_total)

    NIVEL_COLOR = {"Excelente": GREEN, "Favorable": STEEL_LIGHT, "En atención": GOLD, "Crítico": RED}

    # ─── TABS PRINCIPALES ───────────────────────────────────────────
    tab_score, tab_seg, tab_sim = st.tabs(["⭐ Score del Negocio", "👥 Segmentación de Clientes", "🔮 Simulador"])

    # ====================================================================
    # TAB 1: SCORE
    # ====================================================================
    with tab_score:

        # Gauge principal
        st.markdown("## 🎯 ¿Qué tan saludable está tu negocio?")
        col_gauge, col_info = st.columns([1, 1.15], gap="large")

        with col_gauge:
            with st.container(border=True):
                animated_gauge(score_total, nivel, NIVEL_COLOR[nivel])

        with col_info:
            explicaciones = {
                "Excelente": "El negocio presenta una salud operativa excelente. Las principales áreas funcionan de forma favorable.",
                "Favorable": "El negocio presenta un desempeño favorable. Existe una oportunidad concreta de mejora.",
                "En atención": "Existen señales de alerta que requieren atención. Resolver las áreas más débiles puede mejorar significativamente el desempeño.",
                "Crítico": "El negocio presenta una situación crítica. Es importante actuar sobre las áreas de menor desempeño.",
            }
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
                f'<span style="width:14px;height:14px;border-radius:50%;background:{NIVEL_COLOR[nivel]};'
                f'box-shadow:0 0 10px {NIVEL_COLOR[nivel]};display:inline-block;flex-shrink:0"></span>'
                f'<h3 style="margin:0">Tu negocio está en nivel <span style="color:{NIVEL_COLOR[nivel]}">{nivel}</span></h3>'
                f'</div>', unsafe_allow_html=True)
            st.markdown(f"**{explicaciones[nivel]}**")

            # Pilar más débil
            debil = min(pilares_scores, key=pilares_scores.get)
            iconos_pilar = {"cartera": "👥", "inventario": "📦", "tendencia": "📈"}
            nombres_pilar = {"cartera": "Clientes", "inventario": "Inventario", "tendencia": "Ventas"}
            st.warning(f"**🎯 Principal área de atención:** {iconos_pilar[debil]} {nombres_pilar[debil]} ({pilares_scores[debil]:.0f}/100)")

        # Bandas de interpretación
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        st.markdown("### 🚦 ¿Cómo interpretar el Score?")
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("🔴 Crítico", "0 – 44")
        b2.metric("🟡 En atención", "45 – 64")
        b3.metric("🔵 Favorable", "65 – 84")
        b4.metric("🟢 Excelente", "85 – 100")

        st.markdown("---")

        # Pilares detallados
        st.markdown("## 🧩 Desglose por Pilares")
        p1, p2, p3 = st.columns(3)

        pilar_data = [
            ("cartera", "👥", "Clientes", f"Recurrentes: {pct_recurrente:.0%} | En riesgo: {pct_churn:.0%}"),
            ("inventario", "📦", "Inventario", f"Productos en stock crítico: {pct_critico:.0%}"),
            ("tendencia", "📈", "Ventas", f"Crecimiento reciente: {crecimiento:+.1%}"),
        ]
        accents = {"cartera": STEEL_LIGHT, "inventario": GOLD_LIGHT, "tendencia": TEAL}

        for col, (key, icon, name, detalle) in zip([p1, p2, p3], pilar_data):
            s = pilares_scores[key]
            n, _ = nivel_de_score(s)
            with col:
                kpi_counter(icon, name, s, f"{detalle} · {n}", accents[key])

        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)

        # Gráfico comparativo
        with st.container(border=True):
            chart_title("📊 Comparación de pilares")
            fig_bar = px.bar(
                x=[pilares_scores[k] for k in ["cartera", "inventario", "tendencia"]],
                y=["Clientes", "Inventario", "Ventas"],
                orientation="h",
                range_x=[0, 100],
                text=[f"{pilares_scores[k]:.0f}" for k in ["cartera", "inventario", "tendencia"]],
            )
            color_map = {"success": GREEN, "warning": GOLD, "risk": RED}
            fig_bar.update_traces(
                marker_color=[color_map[nivel_de_score(pilares_scores[k])[1]] for k in ["cartera", "inventario", "tendencia"]],
                textposition="outside", marker_line_width=2, marker_line_color=PANEL_SOLID,
                textfont=dict(size=15, color=TEXT),
                hovertemplate="<b>%{y}</b><br>Score: %{x:.0f}/100<extra></extra>",
            )
            fig_bar.update_layout(height=290, showlegend=False, margin=dict(t=15, b=20, l=10, r=50), xaxis_title="Score", **PLOTLY_LAYOUT)
            fig_bar.update_layout(yaxis=dict(tickfont=dict(size=15)), xaxis=dict(tickfont=dict(size=12)))
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

        # Fórmula
        st.markdown("### 📐 Fórmula del Score")
        st.markdown(
            f"**Score =** ({score_clientes:.1f} × {pesos['cartera']:.0%}) "
            f"+ ({score_inv:.1f} × {pesos['inventario']:.0%}) "
            f"+ ({score_ventas:.1f} × {pesos['tendencia']:.0%}) "
            f"= **{score_total:.1f}/100**"
        )

        st.markdown("---")

        st.info("💡 Usa la pestaña **🔮 Simulador** para probar escenarios sin mezclarlo con el Score actual.")

    # ====================================================================
    # TAB 2: SEGMENTACIÓN DE CLIENTES
    # ====================================================================
    with tab_seg:

        st.markdown("## 👥 ¿Quiénes son nuestros clientes?")
        st.caption("Agrupación automática basada en comportamiento de compra (Recencia, Frecuencia, Monto).")

        if len(rfm) < 6:
            st.warning("Se necesitan al menos 6 clientes con compras para la segmentación.")
            st.stop()

        # Escalado
        scaler = StandardScaler()
        X = scaler.fit_transform(rfm[["recencia", "frecuencia", "monto"]])

        # Determinar K
        if auto_k:
            best_k, best_sil = 2, -1
            for k in range(2, min(7, len(rfm))):
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                labels = km.fit_predict(X)
                sil = silhouette_score(X, labels)
                if sil > best_sil:
                    best_k, best_sil = k, sil
            n_clusters = best_k
            st.info(f"🤖 Segmentos óptimos detectados automáticamente: **{n_clusters}** (silhouette: {best_sil:.3f})")
        else:
            n_clusters = k_manual

        # Entrenar K-Means
        km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        rfm["segmento"] = km.fit_predict(X)

        # Etiquetar segmentos según comportamiento real (recencia + frecuencia + monto)
        mapa_etiquetas = etiquetar_clusters(rfm)
        rfm["etiqueta"] = rfm["segmento"].map(mapa_etiquetas)

        # Color fijo por segmento (mismo color en tabla, donut y scatter)
        etiquetas_presentes = rfm["etiqueta"].unique().tolist()
        color_map_activo = {et: color_de_segmento(et, etiquetas_presentes) for et in etiquetas_presentes}

        # Métricas de segmentos
        st.markdown("### 📊 Resumen de Segmentos")
        resumen = rfm.groupby("etiqueta").agg(
            clientes=("cedula_cliente", "count"),
            recencia_prom=("recencia", "mean"),
            frecuencia_prom=("frecuencia", "mean"),
            monto_prom=("monto", "mean"),
        ).reset_index().sort_values("monto_prom", ascending=False)
        resumen.columns = ["Segmento", "Clientes", "Recencia Prom (días)", "Frecuencia Prom", "Monto Prom ($)"]
        resumen["Recencia Prom (días)"] = resumen["Recencia Prom (días)"].round(0).astype(int)
        resumen["Frecuencia Prom"] = resumen["Frecuencia Prom"].round(1)
        resumen["Monto Prom ($)"] = resumen["Monto Prom ($)"].round(2)

        # Tabla propia en HTML con un punto de color igual al de los gráficos
        filas_html = ""
        for _, r in resumen.iterrows():
            c = color_map_activo.get(r["Segmento"], MUTED)
            filas_html += f'''<tr>
                <td style="padding:10px 14px;display:flex;align-items:center;gap:10px;white-space:nowrap">
                    <span style="width:11px;height:11px;border-radius:50%;background:{c};box-shadow:0 0 8px {c};flex-shrink:0"></span>
                    {r["Segmento"]}
                </td>
                <td style="padding:10px 14px;text-align:right">{r["Clientes"]}</td>
                <td style="padding:10px 14px;text-align:right">{r["Recencia Prom (días)"]}</td>
                <td style="padding:10px 14px;text-align:right">{r["Frecuencia Prom"]}</td>
                <td style="padding:10px 14px;text-align:right">${r["Monto Prom ($)"]:,.2f}</td>
            </tr>'''
        tabla_html = f'''
        <div style="border:1px solid {BORDER};border-radius:12px;overflow:hidden">
        <table style="width:100%;border-collapse:collapse;font-size:.92rem">
            <thead>
                <tr style="background:{PANEL_SOLID};border-bottom:1px solid {BORDER}">
                    <th style="padding:10px 14px;text-align:left;color:{MUTED};font-weight:600">Segmento</th>
                    <th style="padding:10px 14px;text-align:right;color:{MUTED};font-weight:600">Clientes</th>
                    <th style="padding:10px 14px;text-align:right;color:{MUTED};font-weight:600">Recencia Prom (días)</th>
                    <th style="padding:10px 14px;text-align:right;color:{MUTED};font-weight:600">Frecuencia Prom</th>
                    <th style="padding:10px 14px;text-align:right;color:{MUTED};font-weight:600">Monto Prom ($)</th>
                </tr>
            </thead>
            <tbody>{filas_html}</tbody>
        </table>
        </div>'''
        st.markdown(tabla_html, unsafe_allow_html=True)

        with st.expander("❓ ¿Qué significa cada segmento?"):
            for seg_nombre in resumen["Segmento"].tolist():
                desc = SEGMENT_DESC.get(seg_nombre, "Grupo de clientes con un comportamiento de compra particular.")
                st.markdown(f"**{seg_nombre}** — {desc}")

        # Gráficos interactivos
        c1, c2 = st.columns(2, gap="large")
        with c1:
            with st.container(border=True):
                chart_title("🥧 Distribución de clientes por segmento")
                top_seg = rfm["etiqueta"].value_counts().idxmax()
                pulls_seg = [0.08 if et == top_seg else 0 for et in rfm["etiqueta"].value_counts().index]
                fig_pie = px.pie(rfm, names="etiqueta", hole=0.45, color="etiqueta", color_discrete_map=color_map_activo)
                fig_pie.update_traces(marker_line=dict(color=PANEL_SOLID, width=3), pull=pulls_seg,
                    textinfo="percent", textfont=dict(size=13, color="#0A0B0F"),
                    hovertemplate="<b>%{label}</b><br>%{value} clientes (%{percent})<extra></extra>")
                fig_pie.add_annotation(text=f"<b>{len(rfm)}</b><br><span style='font-size:11px;color:{MUTED}'>Clientes</span>",
                    x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=GOLD_LIGHT, family="Playfair Display"))
                fig_pie.update_layout(height=380, showlegend=True, margin=dict(t=10, b=10, l=10, r=10), **PLOTLY_LAYOUT)
                fig_pie.update_layout(legend=dict(font=dict(color=TEXT), orientation="h", y=-0.12))
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        with c2:
            with st.container(border=True):
                chart_title("🔎 Recencia vs monto (tamaño = frecuencia)")
                fig_scatter = px.scatter(
                    rfm, x="recencia", y="monto", size="frecuencia", color="etiqueta",
                    labels={"recencia": "Recencia (días)", "monto": "Monto Total ($)", "etiqueta": "Segmento"},
                    color_discrete_map=color_map_activo, size_max=28,
                )
                fig_scatter.update_traces(marker=dict(line=dict(width=1, color=PANEL_SOLID), opacity=0.85))
                fig_scatter.update_layout(height=380, margin=dict(t=10, b=10, l=10, r=10), **PLOTLY_LAYOUT)
                fig_scatter.update_layout(legend=dict(font=dict(color=TEXT), orientation="h", y=-0.18))
                st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

        # Detalle por segmento seleccionado
        st.markdown("### 🔍 Explorar un Segmento")
        seg_elegido = st.selectbox("Selecciona un segmento", resumen["Segmento"].tolist())
        clientes_seg = rfm[rfm["etiqueta"] == seg_elegido].sort_values("monto", ascending=False)

        # Traer nombres
        cedulas = clientes_seg["cedula_cliente"].tolist()
        if cedulas:
            placeholders = ",".join([f"'{c}'" for c in cedulas[:200]])
            nombres = query_df(f"SELECT cedula, nombre, apellido FROM cliente WHERE cedula IN ({placeholders})")
            nombres["nombre_completo"] = (nombres["nombre"].fillna("").astype(str) + " " + nombres["apellido"].fillna("").astype(str)).str.strip()
            clientes_seg = clientes_seg.merge(nombres[["cedula", "nombre_completo"]], left_on="cedula_cliente", right_on="cedula", how="left")
            cols_mostrar = ["nombre_completo", "cedula_cliente", "recencia", "frecuencia", "monto"]
            clientes_seg_display = clientes_seg[cols_mostrar].rename(columns={
                "nombre_completo": "Cliente", "cedula_cliente": "Cédula",
                "recencia": "Recencia (días)", "frecuencia": "Compras", "monto": "Monto Total ($)"
            })
            st.dataframe(clientes_seg_display.head(20), hide_index=True, use_container_width=True)
            st.caption(f"Mostrando los primeros 20 de {len(clientes_seg)} clientes en este segmento.")

    # ====================================================================
    # TAB 3: SIMULADOR INTERACTIVO
    # ====================================================================
    with tab_sim:

        # ─── SIMULADOR INTERACTIVO ───────────────────────────────────────
        st.markdown("## 🔮 ¿Qué pasaría si mejoramos?")
        st.caption("Simula diferentes escenarios y observa cómo cambia el Score. Los valores reales no se modifican.")

        sim1, sim2, sim3 = st.columns(3)
        with sim1:
            st.markdown(f"**👥 Clientes** (actual: {score_clientes:.0f}/100)")
            sim_recurrente = st.slider("Clientes recurrentes (%)", 0, 100, round(pct_recurrente * 100), 1, key="sim_rec")
            sim_churn = st.slider("Clientes en riesgo (%)", 0, 100, round(pct_churn * 100), 1, key="sim_churn")
        with sim2:
            st.markdown(f"**📦 Inventario** (actual: {score_inv:.0f}/100)")
            sim_critico = st.slider("Productos en stock crítico (%)", 0, 100, round(pct_critico * 100), 1, key="sim_crit")
        with sim3:
            st.markdown(f"**📈 Ventas** (actual: {score_ventas:.0f}/100)")
            sim_crecimiento = st.slider("Crecimiento de ventas (%)", -50, 50, round(crecimiento * 100), 1, key="sim_crec")

        sim_s_cli = score_desde_cartera(sim_recurrente / 100, sim_churn / 100)
        sim_s_inv = score_desde_inventario(sim_critico / 100)
        sim_s_ven = score_desde_tendencia(sim_crecimiento / 100)
        sim_total = calcular_score_total({"cartera": sim_s_cli, "inventario": sim_s_inv, "tendencia": sim_s_ven}, pesos)
        sim_nivel, _ = nivel_de_score(sim_total)
        delta = sim_total - score_total

        st.markdown("### 📊 Resultado del escenario")
        r1, r2, r3, r4 = st.columns(4)
        with r1: kpi_counter("👥", "Clientes", sim_s_cli, "", STEEL_LIGHT, delta=sim_s_cli - score_clientes)
        with r2: kpi_counter("📦", "Inventario", sim_s_inv, "", GOLD_LIGHT, delta=sim_s_inv - score_inv)
        with r3: kpi_counter("📈", "Ventas", sim_s_ven, "", TEAL, delta=sim_s_ven - score_ventas)
        with r4: kpi_counter("⭐", "Score Total", sim_total, "", GREEN if delta >= 0 else RED, decimals=1, delta=delta)

        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

        # Gráfico comparativo actual vs simulado
        with st.container(border=True):
            chart_title("📊 Actual vs. escenario simulado")
            categorias = ["Clientes", "Inventario", "Ventas", "Score Total"]
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(name="Actual", x=categorias, y=[score_clientes, score_inv, score_ventas, score_total],
                marker=dict(color=STEEL_LIGHT, line=dict(width=1, color=PANEL_SOLID)),
                hovertemplate="<b>%{x}</b><br>Actual: %{y:.1f}/100<extra></extra>"))
            fig_comp.add_trace(go.Bar(name="Simulado", x=categorias, y=[sim_s_cli, sim_s_inv, sim_s_ven, sim_total],
                marker=dict(color=GREEN if delta >= 0 else RED, line=dict(width=1, color=PANEL_SOLID)),
                hovertemplate="<b>%{x}</b><br>Simulado: %{y:.1f}/100<extra></extra>"))
            fig_comp.update_layout(barmode="group", height=320, yaxis_range=[0, 100], yaxis_title="Score",
                margin=dict(t=15, b=20, l=10, r=10), **PLOTLY_LAYOUT)
            fig_comp.update_layout(legend=dict(font=dict(color=TEXT), orientation="h", y=-0.15))
            st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

        if abs(delta) < 0.5:
            st.info("Este escenario prácticamente no cambia la situación actual.")
        elif delta > 0:
            st.success(f"🚀 El Score subiría **{delta:+.1f} puntos** a **{sim_total:.1f}/100** (nivel {sim_nivel}).")
        else:
            st.error(f"⚠️ El Score caería **{abs(delta):.1f} puntos** a **{sim_total:.1f}/100** (nivel {sim_nivel}).")


except Exception as e:
    st.error("No fue posible cargar el Score Inteligente. Revisa la conexión a la base de datos.")
    with st.expander("Detalle técnico"):
        import traceback
        st.code(traceback.format_exc())

# Pie de página (autoría), agregado automáticamente
show_footer()
