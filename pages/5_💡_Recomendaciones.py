"""Motor de Recomendaciones de LubriInsight.
Genera acciones priorizadas a partir de indicadores reales del negocio.
Adaptado a Lubricadora. No guarda recomendaciones: lee datos en tiempo real.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from utils.database import query_df
from utils.footer import show_footer

# ═══ CONFIGURACIÓN ═══════════════════════════════════════════════════════════════
st.set_page_config(page_title="LubriInsight | Recomendaciones", page_icon="💡", layout="wide", initial_sidebar_state="expanded")

BG = "#0A0B0F"
PANEL = "rgba(255,255,255,0.035)"
PANEL_SOLID = "#12141B"
BORDER = "rgba(255,255,255,0.08)"
GOLD = "#E3A73E"
GOLD_LIGHT = "#F5CF7A"
STEEL = "#4F8FC4"
STEEL_LIGHT = "#9CC9EC"
TEAL = "#3FA6A6"
TEXT = "#EDEFF2"
MUTED = "#ACB8C4"
GREEN = "#2ED18C"
RED = "#E5615B"
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
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(217,169,76,.10),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(143,180,217,.08),transparent 40%),{BG}}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stDeployButton"]{{display:none !important}}
[data-testid="stAppDeployButton"]{{display:none !important}}
[data-testid="stToolbarActions"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}
.block-container{{max-width:1400px;padding:2rem 4rem 4rem}}
h1,h2,h3{{color:{TEXT};letter-spacing:-.03em;font-family:'Playfair Display',serif}}
p, span, div, label{{color:{TEXT}}}

.hero{{background:linear-gradient(160deg,#12141B 0%,#0A0B0F 70%);border:1px solid rgba(217,169,76,.25);
    border-radius:22px;padding:34px 38px;margin-bottom:28px;box-shadow:0 18px 46px rgba(0,0,0,.55)}}
.hero h1{{margin:0 0 10px;font-size:clamp(2rem,4vw,3.7rem);background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero p{{color:{MUTED};max-width:68ch;font-size:1.05rem;margin:0;line-height:1.55}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:.73rem;color:{GOLD};margin-bottom:12px}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:16px;padding:18px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

/* ─── Tarjetas de recomendación: aparición suave, borde dorado giratorio, shimmer y hover elevado ─── */
@keyframes rec-fade-in {{
  from {{ opacity:0; transform:translateY(18px); }}
  to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes rec-border-spin {{
  to {{ transform:rotate(360deg); }}
}}
@keyframes rec-shimmer-sweep {{
  0%   {{ left:-160%; }}
  55%  {{ left:160%; }}
  100% {{ left:160%; }}
}}

.rec-card{{
    position:relative; overflow:hidden; isolation:isolate;
    background:{PANEL}; border:1px solid {BORDER}; border-radius:16px; padding:20px 24px; margin:12px 0;
    box-shadow:0 8px 22px rgba(0,0,0,.32);
    animation:rec-fade-in .55s cubic-bezier(.2,.8,.2,1) both;
    transition:transform .28s ease, box-shadow .28s ease, border-color .28s ease;
}}
.rec-card:hover{{
    transform:translateY(-6px);
    box-shadow:0 22px 44px rgba(0,0,0,.5);
    border-color:rgba(227,167,62,.4);
}}
.rec-card::before{{
    content:""; position:absolute; inset:-1px; z-index:0; border-radius:17px; padding:1.5px;
    background:conic-gradient(from 0deg, transparent 0 62%, {GOLD} 74%, {GOLD_LIGHT} 82%, transparent 92%);
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor; mask-composite:exclude;
    animation:rec-border-spin 6s linear infinite;
    opacity:.65; pointer-events:none;
}}
.rec-card::after{{
    content:""; position:absolute; top:0; left:-160%; width:55%; height:100%; z-index:0;
    background:linear-gradient(115deg, transparent, rgba(245,207,122,.10), transparent);
    animation:rec-shimmer-sweep 3.6s ease-in-out infinite;
    pointer-events:none;
}}
.rec-card > *{{position:relative; z-index:1}}
.rec-card h4{{color:{TEXT};margin:8px 0 6px;font-family:'Playfair Display',serif}}
.rec-card p{{color:{MUTED};margin:0;line-height:1.55}}
.pill{{display:inline-block;border-radius:999px;padding:4px 12px;font-weight:800;font-size:.73rem;margin-bottom:8px}}
.pill-high{{background:rgba(229,97,91,.16);color:{RED};border:1px solid rgba(229,97,91,.4)}}
.pill-medium{{background:rgba(227,167,62,.16);color:{GOLD_LIGHT};border:1px solid rgba(227,167,62,.4)}}
.pill-low{{background:rgba(46,209,140,.16);color:{GREEN};border:1px solid rgba(46,209,140,.4)}}
.section{{margin:34px 0 16px}}.muted{{color:{MUTED}}}

[data-baseweb="tab-list"]{{border-bottom:1px solid {BORDER}}}
[data-baseweb="tab"]{{color:{MUTED};font-family:'Playfair Display',serif;font-weight:600;letter-spacing:.01em}}
[aria-selected="true"][data-baseweb="tab"]{{color:{GOLD_LIGHT} !important}}

[data-testid="stAlert"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px;color:{TEXT}}}
[data-testid="stDataFrame"]{{border:1px solid {BORDER};border-radius:12px;overflow:hidden}}
[data-testid="stExpander"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px}}
[data-testid="stExpander"] summary{{color:{STEEL_LIGHT} !important;font-weight:600}}

[data-testid="stSelectbox"],[data-testid="stMultiSelect"]{{background:{PANEL} !important;
    border:1px solid {BORDER} !important;border-radius:8px}}
[data-testid="stSelectbox"] div,[data-testid="stMultiSelect"] div{{background:transparent !important}}
[data-testid="stSelectbox"] *,[data-testid="stMultiSelect"] *{{color:{TEXT} !important}}
[data-baseweb="tag"]{{background:{GOLD} !important}}
[data-baseweb="tag"] span{{color:#0A0B0F !important}}
[data-baseweb="popover"],[data-baseweb="menu"]{{background:{PANEL_SOLID} !important}}
[data-baseweb="popover"] *,[data-baseweb="menu"] *{{color:{TEXT} !important}}
li[role="option"]{{background:{PANEL_SOLID} !important;color:{TEXT} !important}}
li[role="option"]:hover{{background:rgba(255,255,255,.08) !important}}

/* Tarjeta destacada para gráficos */
[data-testid="stVerticalBlockBorderWrapper"]{{background:linear-gradient(160deg,rgba(227,167,62,.06),rgba(255,255,255,.01));
    border:1px solid rgba(227,167,62,.25) !important;border-radius:16px !important;
    box-shadow:0 14px 32px rgba(0,0,0,.45);padding:6px}}
@media(max-width:800px){{.block-container{{padding:1.2rem}}}}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">LAVADORA S.A. · INTELIGENCIA COMERCIAL</div><h1>💡 Recomendaciones</h1><p>Acciones priorizadas basadas en el análisis automático de inventario, clientes y ventas.</p></div>', unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    title_font=dict(size=17, color=GOLD_LIGHT, family='Playfair Display'),
    xaxis=dict(gridcolor='rgba(255,255,255,.10)'), yaxis=dict(gridcolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT)), hoverlabel=dict(bgcolor=PANEL_SOLID, font_color=TEXT, bordercolor=BORDER))
PALETTE = [GOLD_LIGHT, STEEL_LIGHT, TEAL, GOLD, STEEL, MUTED, GREEN, RED]

_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix="", suffix=""):
    """Tarjeta KPI con número que cuenta en vivo desde 0 hasta su valor real (CSS autocontenido).
    Incluye aparición suave, borde dorado giratorio sutil y barrido de brillo (shimmer)."""
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"
    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; overflow:hidden; }}
      @keyframes kpi-fade-in {{
        from {{ opacity:0; transform:translateY(14px); }}
        to   {{ opacity:1; transform:translateY(0); }}
      }}
      @keyframes kpi-border-spin {{
        to {{ transform:rotate(360deg); }}
      }}
      @keyframes kpi-shimmer-sweep {{
        0%   {{ left:-160%; }}
        55%  {{ left:160%; }}
        100% {{ left:160%; }}
      }}
      .kpi-card {{ position:relative; overflow:hidden; isolation:isolate;
        background:{PANEL}; border:1px solid {BORDER}; border-radius:15px; padding:16px 16px 14px;
        box-shadow:0 8px 22px rgba(0,0,0,.35); border-top:3px solid {accent}; box-sizing:border-box; min-height:118px;
        animation:kpi-fade-in .55s cubic-bezier(.2,.8,.2,1) both; }}
      .kpi-card::before {{
        content:""; position:absolute; inset:-1px; z-index:0; border-radius:16px; padding:1.5px;
        background:conic-gradient(from 0deg, transparent 0 62%, {GOLD} 74%, {GOLD_LIGHT} 82%, transparent 92%);
        -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite:xor; mask-composite:exclude;
        animation:kpi-border-spin 6s linear infinite;
        opacity:.5; pointer-events:none;
      }}
      .kpi-card::after {{
        content:""; position:absolute; top:0; left:-160%; width:55%; height:100%; z-index:0;
        background:linear-gradient(115deg, transparent, rgba(245,207,122,.09), transparent);
        animation:kpi-shimmer-sweep 3.8s ease-in-out infinite;
        pointer-events:none;
      }}
      .kpi-card > * {{ position:relative; z-index:1; }}
      .kpi-badge {{ width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:1rem; margin-bottom:8px;
        background:radial-gradient(circle,{accent}55,{accent}22); }}
      .kpi-label {{ text-transform:uppercase; letter-spacing:.1em; font-weight:800; font-size:.68rem;
        margin-bottom:6px; color:{accent}; }}
      .kpi-value {{ font-size:1.55rem; font-weight:800; color:{TEXT}; font-variant-numeric:tabular-nums; }}
      .kpi-sub {{ color:{MUTED}; font-size:.72rem; margin-top:5px; line-height:1.3; }}
    </style>
    <div class="kpi-card">
      <div class="kpi-badge">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value"><span id="{uid}">0</span></div>
      <div class="kpi-sub">{subtext}</div>
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


# ═══ CARGA DE DATOS ══════════════════════════════════════════════════════════════

@st.cache_data(ttl=300)
def cargar_inventario() -> pd.DataFrame:
    return query_df("""
        SELECT i.id_producto, p.nombre AS producto, p.precio, p.costo,
               c.nombre AS categoria,
               i.stock_actual, i.stock_minimo, i.stock_maximo,
               i.punto_reorden, i.estado_stock
        FROM inventario i
        JOIN producto p ON p.id_producto = i.id_producto
        JOIN categoria c ON c.id_categoria = p.id_categoria
    """)


@st.cache_data(ttl=300)
def cargar_actividad_clientes() -> pd.DataFrame:
    return query_df("""
        SELECT cedula_cliente,
               COUNT(DISTINCT id_venta) AS compras,
               MAX(fecha_venta)::date AS ultima_compra,
               SUM(total) AS monto_total
        FROM venta
        WHERE total IS NOT NULL AND cedula_cliente <> :consumer
        GROUP BY cedula_cliente
    """, {"consumer": CONSUMER})


@st.cache_data(ttl=300)
def cargar_ventas_mensuales() -> pd.DataFrame:
    return query_df("""
        SELECT DATE_TRUNC('month', fecha_venta)::date AS mes,
               EXTRACT(YEAR FROM fecha_venta)::int AS anio,
               EXTRACT(MONTH FROM fecha_venta)::int AS numero_mes,
               SUM(total) AS ingresos,
               COUNT(*) AS ventas
        FROM venta WHERE total IS NOT NULL AND fecha_venta IS NOT NULL
        GROUP BY 1, 2, 3 ORDER BY 1
    """)


@st.cache_data(ttl=300)
def cargar_top_productos() -> pd.DataFrame:
    return query_df("""
        SELECT p.nombre AS producto, c.nombre AS categoria,
               SUM(dv.cantidad) AS unidades_vendidas,
               SUM(dv.cantidad * p.precio) AS ingresos_generados
        FROM detalle_venta dv
        JOIN producto p ON p.id_producto = dv.id_producto
        JOIN categoria c ON c.id_categoria = p.id_categoria
        GROUP BY p.nombre, c.nombre
        ORDER BY unidades_vendidas DESC
    """)


# ═══ MOTOR DE RECOMENDACIONES ═══════════════════════════════════════════════════

def generar_recomendaciones(inv: pd.DataFrame, act: pd.DataFrame, mensual: pd.DataFrame) -> list[dict]:
    """Genera recomendaciones priorizadas a partir de datos reales."""
    recs = []

    # ─── INVENTARIO ───
    if not inv.empty:
        inv["stock_actual"] = pd.to_numeric(inv["stock_actual"], errors="coerce").fillna(0)
        inv["punto_reorden"] = pd.to_numeric(inv["punto_reorden"], errors="coerce").fillna(0)
        inv["stock_minimo"] = pd.to_numeric(inv["stock_minimo"], errors="coerce").fillna(0)

        sin_stock = inv[inv["stock_actual"] == 0]
        bajo_reorden = inv[(inv["stock_actual"] > 0) & (inv["stock_actual"] <= inv["punto_reorden"])]
        bajo_minimo = inv[(inv["stock_actual"] > 0) & (inv["stock_actual"] <= inv["stock_minimo"])]

        if len(sin_stock) > 0:
            productos_lista = ", ".join(sin_stock["producto"].head(5).tolist())
            recs.append({
                "prioridad": "alta",
                "area": "📦 Inventario",
                "titulo": f"{len(sin_stock)} productos sin stock",
                "descripcion": f"Estos productos están agotados y no pueden venderse. Ejemplos: {productos_lista}.",
                "accion": "Realizar orden de compra inmediata para los productos sin stock.",
            })

        if len(bajo_reorden) > 0:
            recs.append({
                "prioridad": "media",
                "area": "📦 Inventario",
                "titulo": f"{len(bajo_reorden)} productos bajo punto de reorden",
                "descripcion": "Estos productos están por debajo de su punto de reorden y podrían agotarse pronto.",
                "accion": "Planificar reposición antes de que lleguen a stock crítico.",
            })

        if len(bajo_minimo) > 0:
            recs.append({
                "prioridad": "alta",
                "area": "📦 Inventario",
                "titulo": f"{len(bajo_minimo)} productos bajo stock mínimo",
                "descripcion": "Productos que ya están por debajo del límite mínimo aceptable.",
                "accion": "Priorizar la reposición urgente de estos productos.",
            })

    # ─── CLIENTES ───
    if not act.empty:
        act["ultima_compra"] = pd.to_datetime(act["ultima_compra"], errors="coerce")
        hoy = act["ultima_compra"].max()
        act["dias_sin_compra"] = (hoy - act["ultima_compra"]).dt.days

        en_riesgo = act[act["dias_sin_compra"] > 120]
        dormidos = act[act["dias_sin_compra"] > 180]
        una_compra = act[act["compras"] == 1]

        total_clientes = len(act)
        pct_riesgo = len(en_riesgo) / total_clientes if total_clientes > 0 else 0

        if pct_riesgo > 0.4:
            recs.append({
                "prioridad": "alta",
                "area": "👥 Clientes",
                "titulo": f"{len(en_riesgo)} clientes en riesgo de abandono ({pct_riesgo:.0%})",
                "descripcion": f"Más del 40% de los clientes llevan más de 120 días sin comprar.",
                "accion": "Implementar campaña de reactivación con descuentos o contacto directo.",
            })
        elif len(en_riesgo) > 0:
            recs.append({
                "prioridad": "media",
                "area": "👥 Clientes",
                "titulo": f"{len(en_riesgo)} clientes sin comprar en 120+ días",
                "descripcion": "Estos clientes muestran señales de abandono.",
                "accion": "Realizar seguimiento personalizado para recuperar su interés.",
            })

        if len(una_compra) > total_clientes * 0.5 and total_clientes > 5:
            recs.append({
                "prioridad": "media",
                "area": "👥 Clientes",
                "titulo": f"{len(una_compra)} clientes con una sola compra ({len(una_compra)/total_clientes:.0%})",
                "descripcion": "Una gran proporción de clientes no ha regresado después de su primera compra.",
                "accion": "Crear estrategia de segunda compra: seguimiento post-venta, ofertas personalizadas.",
            })

        if len(dormidos) > 0:
            recs.append({
                "prioridad": "baja",
                "area": "👥 Clientes",
                "titulo": f"{len(dormidos)} clientes dormidos (180+ días)",
                "descripcion": "Clientes que llevan más de 6 meses sin comprar.",
                "accion": "Evaluar si conviene intentar recuperarlos o enfocar esfuerzos en clientes activos.",
            })

    # ─── VENTAS ───
    if not mensual.empty:
        mensual["ingresos"] = pd.to_numeric(mensual["ingresos"], errors="coerce")
        if len(mensual) >= 3:
            ultimo = mensual["ingresos"].iloc[-1]
            penultimo = mensual["ingresos"].iloc[-2]
            promedio = mensual["ingresos"].iloc[:-1].mean()

            if ultimo < penultimo * 0.8:
                caida = (penultimo - ultimo) / penultimo
                recs.append({
                    "prioridad": "alta",
                    "area": "📈 Ventas",
                    "titulo": f"Caída del {caida:.0%} en ventas del último mes",
                    "descripcion": f"El último mes registró ${ultimo:,.0f} vs ${penultimo:,.0f} del mes anterior.",
                    "accion": "Analizar causas de la caída y activar promociones para recuperar volumen.",
                })
            elif ultimo < promedio * 0.9:
                recs.append({
                    "prioridad": "media",
                    "area": "📈 Ventas",
                    "titulo": "Ventas por debajo del promedio histórico",
                    "descripcion": f"Último mes: ${ultimo:,.0f}. Promedio histórico: ${promedio:,.0f}.",
                    "accion": "Revisar estacionalidad y considerar acciones comerciales.",
                })
            elif ultimo > promedio * 1.2:
                recs.append({
                    "prioridad": "baja",
                    "area": "📈 Ventas",
                    "titulo": "Ventas por encima del promedio — buen momento",
                    "descripcion": f"Último mes: ${ultimo:,.0f} vs promedio ${promedio:,.0f}.",
                    "accion": "Aprovechar el impulso para fidelizar clientes nuevos y reforzar stock.",
                })

    # Si no hay recomendaciones
    if not recs:
        recs.append({
            "prioridad": "baja",
            "area": "✅ General",
            "titulo": "Todo en orden",
            "descripcion": "No se detectaron situaciones críticas en este momento.",
            "accion": "Continuar monitoreando los indicadores periódicamente.",
        })

    return recs


def render_recomendacion(rec: dict) -> None:
    """Renderiza una tarjeta de recomendación."""
    pill_class = {"alta": "pill-high", "media": "pill-medium", "baja": "pill-low"}
    pill_text = {"alta": "🔴 PRIORIDAD ALTA", "media": "🟡 PRIORIDAD MEDIA", "baja": "🟢 PRIORIDAD BAJA"}
    st.markdown(f"""
    <div class="rec-card">
        <span class="pill {pill_class[rec['prioridad']]}">{pill_text[rec['prioridad']]}</span>
        <span style="color:{MUTED};font-size:.82rem;margin-left:8px;">{rec['area']}</span>
        <h4>{rec['titulo']}</h4>
        <p>{rec['descripcion']}</p>
        <p style="margin-top:10px;"><strong style="color:{GOLD_LIGHT}">💡 Acción sugerida:</strong> {rec['accion']}</p>
    </div>
    """, unsafe_allow_html=True)


# ═══ EJECUCIÓN PRINCIPAL ══════════════════════════════════════════════════════════

try:
    inv = cargar_inventario()
    act = cargar_actividad_clientes()
    mensual = cargar_ventas_mensuales()
    top_prod = cargar_top_productos()

    # ─── Tarjetas de contexto ───
    c1, c2, c3, c4 = st.columns(4)
    total_ingresos = mensual["ingresos"].sum() if not mensual.empty else 0
    sin_stock = len(inv[inv["stock_actual"] == 0]) if not inv.empty else 0
    with c1: kpi_counter("👥", "Clientes activos", len(act), "", STEEL_LIGHT)
    with c2: kpi_counter("📦", "Productos en inventario", len(inv), "", TEAL)
    with c3: kpi_counter("💰", "Ingresos totales", total_ingresos, "", GOLD_LIGHT, prefix="$")
    with c4: kpi_counter("⚠️", "Sin stock", sin_stock, "", RED)

    st.markdown("---")

    # ─── SIDEBAR: Filtros ───
    with st.sidebar:
        st.markdown("### 🎯 Filtros")
        filtro_area = st.multiselect(
            "Área",
            ["📦 Inventario", "👥 Clientes", "📈 Ventas", "✅ General"],
            default=["📦 Inventario", "👥 Clientes", "📈 Ventas", "✅ General"],
        )
        filtro_prioridad = st.multiselect(
            "Prioridad",
            ["alta", "media", "baja"],
            default=["alta", "media", "baja"],
            format_func=lambda x: {"🔴 Alta": "alta", "🟡 Media": "media", "🟢 Baja": "baja"}.get(x, x.title()),
        )

    # ─── Generar recomendaciones ───
    recs = generar_recomendaciones(inv, act, mensual)

    # Filtrar
    recs_filtradas = [r for r in recs if r["area"] in filtro_area and r["prioridad"] in filtro_prioridad]

    # ─── TABS ───
    tab_recs, tab_detalle, tab_tendencia = st.tabs(["💡 Recomendaciones", "📊 Detalle de Datos", "📈 Tendencia de Ventas"])

    # ================================================================
    # TAB 1: RECOMENDACIONES
    # ================================================================
    with tab_recs:
        st.markdown("## 💡 Acciones Recomendadas")
        st.caption("Estas recomendaciones se generan automáticamente a partir del estado actual del negocio.")

        # Resumen de prioridades
        n_alta = sum(1 for r in recs if r["prioridad"] == "alta")
        n_media = sum(1 for r in recs if r["prioridad"] == "media")
        n_baja = sum(1 for r in recs if r["prioridad"] == "baja")

        m1, m2, m3 = st.columns(3)
        with m1: kpi_counter("🔴", "Alta prioridad", n_alta, "", RED)
        with m2: kpi_counter("🟡", "Media prioridad", n_media, "", GOLD_LIGHT)
        with m3: kpi_counter("🟢", "Baja prioridad", n_baja, "", GREEN)

        st.markdown("---")

        if not recs_filtradas:
            st.info("No hay recomendaciones que coincidan con los filtros seleccionados.")
        else:
            for rec in sorted(recs_filtradas, key=lambda r: {"alta": 0, "media": 1, "baja": 2}[r["prioridad"]]):
                render_recomendacion(rec)

    # ================================================================
    # TAB 2: DETALLE DE DATOS
    # ================================================================
    with tab_detalle:
        st.markdown("## 📊 Detalle de los Indicadores")

        col_inv, col_cli = st.columns(2)

        with col_inv:
            st.markdown("### 📦 Estado del Inventario")
            if not inv.empty:
                inv["estado"] = inv.apply(
                    lambda r: "🔴 Sin stock" if r["stock_actual"] == 0
                    else "🟡 Bajo reorden" if r["stock_actual"] <= r["punto_reorden"]
                    else "🟢 OK", axis=1
                )
                resumen_inv = inv["estado"].value_counts().reset_index()
                resumen_inv.columns = ["Estado", "Productos"]

                top_inv = resumen_inv.loc[resumen_inv["Productos"].idxmax(), "Estado"]
                pulls_inv = [0.08 if e == top_inv else 0 for e in resumen_inv["Estado"]]
                fig_inv = px.pie(resumen_inv, names="Estado", values="Productos", hole=0.5, title="Estado del Inventario",
                    color_discrete_sequence=[RED, GOLD_LIGHT, GREEN])
                fig_inv.update_traces(marker_line=dict(color=PANEL_SOLID, width=3), pull=pulls_inv,
                    textinfo="percent", textfont=dict(size=13, color="#0A0B0F"),
                    hovertemplate="<b>%{label}</b><br>%{value} productos (%{percent})<extra></extra>")
                fig_inv.add_annotation(text=f"<b>{int(resumen_inv['Productos'].sum())}</b><br><span style='font-size:10px;color:{MUTED}'>Total</span>",
                    x=0.5, y=0.5, showarrow=False, font=dict(size=17, color=GOLD_LIGHT, family="Playfair Display"))
                fig_inv.update_layout(height=300, **PLOTLY_LAYOUT)
                with st.container(border=True):
                    st.plotly_chart(fig_inv, use_container_width=True)

                # Productos críticos
                criticos = inv[inv["stock_actual"] <= inv["punto_reorden"]].sort_values("stock_actual")
                if not criticos.empty:
                    with st.expander(f"📄 Ver {len(criticos)} productos que necesitan reposición", expanded=False):
                        st.dataframe(
                            criticos[["producto", "categoria", "stock_actual", "punto_reorden", "stock_minimo"]].head(15).rename(columns={
                                "producto": "Producto", "categoria": "Categoría",
                                "stock_actual": "Stock Actual", "punto_reorden": "Pto. Reorden", "stock_minimo": "Stock Mín."
                            }),
                            hide_index=True, use_container_width=True
                        )
            else:
                st.info("No hay datos de inventario disponibles.")

        with col_cli:
            st.markdown("### 👥 Actividad de Clientes")
            if not act.empty:
                act["ultima_compra"] = pd.to_datetime(act["ultima_compra"], errors="coerce")
                hoy = act["ultima_compra"].max()
                act["dias_sin_compra"] = (hoy - act["ultima_compra"]).dt.days
                act["estado_cliente"] = act["dias_sin_compra"].apply(
                    lambda d: "🟢 Activo" if d <= 60 else "🟡 Tibio" if d <= 120 else "🔴 En riesgo"
                )
                resumen_cli = act["estado_cliente"].value_counts().reset_index()
                resumen_cli.columns = ["Estado", "Clientes"]

                # Gráfico de distribución
                top_estado = resumen_cli.loc[resumen_cli["Clientes"].idxmax(), "Estado"]
                pulls = [0.08 if e == top_estado else 0 for e in resumen_cli["Estado"]]
                fig_cli = px.pie(resumen_cli, names="Estado", values="Clientes", hole=0.5, title="Distribución de Clientes",
                    color_discrete_sequence=[GREEN, GOLD_LIGHT, RED])
                fig_cli.update_traces(marker_line=dict(color=PANEL_SOLID, width=3), pull=pulls,
                    textinfo="percent", textfont=dict(size=13, color="#0A0B0F"),
                    hovertemplate="<b>%{label}</b><br>%{value} clientes (%{percent})<extra></extra>")
                fig_cli.add_annotation(text=f"<b>{int(resumen_cli['Clientes'].sum())}</b><br><span style='font-size:10px;color:{MUTED}'>Total</span>",
                    x=0.5, y=0.5, showarrow=False, font=dict(size=17, color=GOLD_LIGHT, family="Playfair Display"))
                fig_cli.update_layout(height=300, **PLOTLY_LAYOUT)
                with st.container(border=True):
                    st.plotly_chart(fig_cli, use_container_width=True)
                with st.expander("📄 Ver tabla de estados", expanded=False):
                    st.dataframe(resumen_cli, hide_index=True, use_container_width=True)
            else:
                st.info("No hay datos de actividad de clientes.")

        # Top productos
        if not top_prod.empty:
            st.markdown("### 🏆 Top 10 Productos Más Vendidos")
            top10 = top_prod.head(10)
            fig_top = px.bar(
                top10, x="unidades_vendidas", y="producto", orientation="h",
                color="categoria", text="unidades_vendidas",
                labels={"unidades_vendidas": "Unidades", "producto": "", "categoria": "Categoría"},
                color_discrete_sequence=PALETTE,
            )
            fig_top.update_layout(height=400, **PLOTLY_LAYOUT)
            fig_top.update_layout(yaxis={"categoryorder": "total ascending"})
            fig_top.update_traces(textposition="outside", marker_line_width=1.5, marker_line_color=PANEL_SOLID,
                hovertemplate="<b>%{y}</b><br>Unidades: %{x}<extra></extra>")
            with st.container(border=True):
                st.plotly_chart(fig_top, use_container_width=True)

    # ================================================================
    # TAB 3: TENDENCIA DE VENTAS
    # ================================================================
    with tab_tendencia:
        st.markdown("## 📈 Evolución de Ventas")
        st.caption("Selecciona un mes para comparar su comportamiento en todos los años disponibles.")

        if not mensual.empty:
            mensual["mes"] = pd.to_datetime(mensual["mes"])
            mensual["anio"] = pd.to_numeric(mensual["anio"], errors="coerce").astype(int)
            mensual["numero_mes"] = pd.to_numeric(mensual["numero_mes"], errors="coerce").astype(int)
            mensual["ingresos"] = pd.to_numeric(mensual["ingresos"], errors="coerce").fillna(0)
            mensual["ventas"] = pd.to_numeric(mensual["ventas"], errors="coerce").fillna(0)

            nombres_meses = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}
            meses_disponibles = sorted(mensual["numero_mes"].unique().tolist())
            mes_elegido = st.selectbox(
                "📅 Selecciona un mes",
                meses_disponibles,
                format_func=lambda n: nombres_meses.get(n, str(n)),
                index=meses_disponibles.index(11) if 11 in meses_disponibles else 0,
                key="mes_comparativo",
            )
            datos_mes = mensual[mensual["numero_mes"] == mes_elegido].sort_values("anio").copy()
            nombre_mes = nombres_meses.get(mes_elegido, str(mes_elegido))

            st.markdown(f"### 📊 Resumen de {nombre_mes} por año")
            total_mes = datos_mes["ingresos"].sum()
            promedio_mes = datos_mes["ingresos"].mean()
            mejor = datos_mes.loc[datos_mes["ingresos"].idxmax()] if not datos_mes.empty else None
            m1, m2, m3 = st.columns(3)
            with m1: kpi_counter("💰", f"Ingresos en {nombre_mes}", total_mes, "Acumulado en todos los años", GOLD_LIGHT, prefix="$")
            with m2: kpi_counter("📊", "Promedio por año", promedio_mes, "", STEEL_LIGHT, prefix="$")
            with m3: kpi_counter("🏆", "Mejor año", int(mejor['anio']) if mejor is not None else 0, "Mayor ingreso registrado", GOLD)

            fig_ing = px.bar(
                datos_mes, x="anio", y="ingresos", text="ingresos",
                title=f"Ingresos de {nombre_mes} por año", color="ingresos",
                color_continuous_scale=[(0, STEEL), (0.5, TEAL), (1, GOLD_LIGHT)],
                labels={"anio": "Año", "ingresos": "Ingresos ($)"},
            )
            fig_ing.update_traces(texttemplate="$%{text:,.0f}", textposition="outside",
                marker_line_width=1.5, marker_line_color=PANEL_SOLID,
                hovertemplate="<b>Año %{x}</b><br>Ingresos: $%{y:,.2f}<extra></extra>")
            fig_ing.add_hline(y=promedio_mes, line_dash="dash", line_color=MUTED, line_width=1.5,
                annotation_text=f"Promedio: ${promedio_mes:,.0f}", annotation_font_color=MUTED, annotation_position="top left")
            fig_ing.update_layout(height=400, coloraxis_showscale=False, **PLOTLY_LAYOUT)
            fig_ing.update_layout(xaxis={"dtick": 1})
            with st.container(border=True):
                st.plotly_chart(fig_ing, use_container_width=True)

            promedio_ventas = datos_mes["ventas"].mean()
            fig_tx = px.area(
                datos_mes, x="anio", y="ventas", markers=True, text="ventas",
                title=f"Transacciones de {nombre_mes} por año",
                labels={"anio": "Año", "ventas": "Transacciones"},
            )
            fig_tx.update_traces(line={"color": STEEL_LIGHT, "width": 4}, textposition="top center",
                marker=dict(size=10, color=GOLD_LIGHT, line=dict(width=2, color=PANEL_SOLID)),
                fill="tozeroy", fillcolor="rgba(156,201,236,.22)",
                hovertemplate="<b>Año %{x}</b><br>Transacciones: %{y}<extra></extra>")
            fig_tx.add_hline(y=promedio_ventas, line_dash="dash", line_color=MUTED, line_width=1.5,
                annotation_text=f"Promedio: {promedio_ventas:,.0f}", annotation_font_color=MUTED, annotation_position="top left")
            fig_tx.update_layout(height=350, **PLOTLY_LAYOUT)
            fig_tx.update_layout(xaxis={"dtick": 1})
            with st.container(border=True):
                st.plotly_chart(fig_tx, use_container_width=True)

            with st.expander("📄 Ver tabla completa por año", expanded=False):
                tabla = datos_mes[["anio", "ingresos", "ventas"]].rename(columns={"anio": "Año", "ingresos": "Ingresos ($)", "ventas": "Transacciones"})
                tabla["Ingresos ($)"] = tabla["Ingresos ($)"].round(2)
                st.dataframe(tabla, hide_index=True, use_container_width=True)

            st.markdown("### 🔎 Explorar el año")
            anios = datos_mes["anio"].tolist()
            anio_elegido = st.selectbox("Selecciona un año para ver el detalle del mes", anios, key="anio_mes_detalle")
            detalle = datos_mes[datos_mes["anio"] == anio_elegido].iloc[0]
            d1, d2, d3 = st.columns(3)
            with d1: kpi_counter("📅", "Periodo", int(anio_elegido), nombre_mes, TEAL)
            with d2: kpi_counter("💰", "Ingresos", float(detalle['ingresos']), "", GOLD_LIGHT, prefix="$")
            with d3: kpi_counter("🧾", "Transacciones", int(detalle['ventas']), "", STEEL_LIGHT)
        else:
            st.info("No hay datos de ventas mensuales disponibles.")

except Exception as e:
    st.error("No fue posible cargar el Motor de Recomendaciones. Revisa la conexión a la base de datos.")
    with st.expander("Detalle técnico"):
        import traceback
        st.code(traceback.format_exc())

# Pie de página (autoría), agregado automáticamente
show_footer()