"""Inicio de LubriInsight, presentación ejecutiva sin reemplazar la lógica de datos."""
import base64
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy.exc import SQLAlchemyError
from utils.database import query_df

st.set_page_config(page_title="LubriInsight | Inicio", page_icon="🚗", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------------------------
# Paleta inspirada en el logo: negro profundo, dorado (aceite) y azul acero (agua)
# ---------------------------------------------------------------------------
BG = "#0A0B0F"
PANEL = "rgba(255,255,255,0.035)"
BORDER = "rgba(255,255,255,0.08)"
GOLD = "#E3A73E"
GOLD_LIGHT = "#F5CF7A"
STEEL = "#4F8FC4"
STEEL_LIGHT = "#9CC9EC"
TEXT = "#EDEFF2"
MUTED = "#98A4B2"
MUTED_LIGHT = "#B9C3CE"  # texto secundario con mejor contraste sobre fondo oscuro
GREEN = "#2ED18C"
RED = "#E5615B"
STEP1, STEP2, STEP3, STEP4 = "#E3A73E", "#C97B4A", "#3FA6A6", "#4F8FC4"

# Logo: ubicado dentro de assets/diagramas/ (ojo: el archivo real dice "lubrrinsight")
LOGO_PATH = "assets/diagramas/Logo lubriinsight.png"
# Ícono compacto (solo engranaje + gota) para el sidebar, evita repetir el logo completo
SIDEBAR_ICON_PATH = "assets/diagramas/logo_icono_sidebar.png"


def _b64(path) -> str | None:
    try:
        return base64.b64encode(Path(path).read_bytes()).decode()
    except FileNotFoundError:
        return None


logo_b64 = _b64(LOGO_PATH)
sidebar_icon_b64 = _b64(SIDEBAR_ICON_PATH)
logo_html = (
    f'<img src="data:image/png;base64,{logo_b64}" class="hero-logo" />' if logo_b64 else ""
)

if not logo_b64:
    st.warning(
        f"⚠️ No se encontró el logo en: `{Path(LOGO_PATH).resolve()}`. "
        "Verifica que la ruta y el nombre del archivo coincidan exactamente."
    )

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');
*{{font-family:'Inter',sans-serif}}
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(217,169,76,.10),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(143,180,217,.08),transparent 40%),{BG}}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
.block-container{{max-width:1400px;padding:2rem 3rem 4rem}}
h1,h2,h3{{color:{TEXT};letter-spacing:-.03em;font-family:'Playfair Display',serif}}
p, span, div{{color:{TEXT}}}

/* Sidebar */
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}

/* Ícono compacto arriba del menú (no el logo completo, para no repetirlo) */
[data-testid="stSidebarNav"]{{padding-top:95px !important;position:relative}}
[data-testid="stSidebarNav"]::before{{
    content:"";position:absolute;top:14px;left:0;right:0;height:64px;
    background-image:url(data:image/png;base64,{sidebar_icon_b64 or ""});
    background-repeat:no-repeat;background-position:top center;background-size:contain;
}}

/* Tipografía y estilo de los enlaces del menú */
[data-testid="stSidebarNav"] a{{border-radius:10px;margin:2px 8px;padding:10px 12px !important;
    transition:background .15s ease}}
[data-testid="stSidebarNav"] span{{font-family:'Playfair Display',serif;font-weight:600;
    font-size:.95rem;letter-spacing:.01em;white-space:normal !important}}
[data-testid="stSidebarNav"] a:hover{{background:rgba(227,167,62,.14) !important}}
[data-testid="stSidebarNav"] a[aria-current="page"]{{
    background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
    border-left:3px solid {GOLD_LIGHT}}}
[data-testid="stSidebarNav"] a[aria-current="page"] span{{color:{GOLD_LIGHT} !important}}

/* Hero */
.hero{{position:relative;background:linear-gradient(160deg,#12141B 0%,#0A0B0F 70%);
       border:1px solid rgba(217,169,76,.25);border-radius:22px;padding:30px 38px 34px;
       margin-bottom:30px;box-shadow:0 18px 46px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.02) inset;
       text-align:center;overflow:hidden}}
.hero::after{{content:"";position:absolute;inset:0;pointer-events:none;
       background:linear-gradient(120deg,transparent 40%,rgba(227,167,62,.06) 50%,transparent 60%)}}
.hero-logo{{display:block;
            width:350px;
            max-width:350px;
            height:auto;
            max-height:300px;
            object-fit:contain;
            margin:0 auto 18px;
            filter:drop-shadow(0 8px 20px rgba(217,169,76,.28))}}
.hero h1{{color:{TEXT};margin:0 0 10px;font-size:clamp(2rem,4vw,3.6rem);
          background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
          -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero p{{color:{MUTED};max-width:70ch;margin:0 auto;font-size:1.08rem;line-height:1.6}}
.eyebrow{{text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:.73rem;
          color:{GOLD};margin-bottom:14px}}
.hero-tags{{display:flex;justify-content:center;gap:10px;margin-top:18px;flex-wrap:wrap}}
.hero-tag{{border:1px solid {BORDER};border-radius:999px;padding:6px 16px;font-size:.78rem;
    font-weight:600;color:{STEEL_LIGHT};background:rgba(79,143,196,.08)}}

/* KPI cards */
[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:16px;
    padding:18px;box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}
[data-testid="stMetricDelta"]{{color:{GREEN} !important}}

.section{{margin:38px 0 18px}}.section h2{{margin-bottom:4px}}.muted{{color:{MUTED_LIGHT};max-width:80ch}}
.status{{background:rgba(46,209,140,.08);border:1px solid rgba(46,209,140,.35);border-radius:14px;
         padding:16px 18px;color:{GREEN};margin:22px 0;font-weight:700}}

/* Ocultar controles nativos de Streamlit (Deploy, menú, toolbar) */
[data-testid="stToolbar"]{{display:none !important}}
[data-testid="stToolbarActions"]{{display:none !important}}
.stDeployButton{{display:none !important}}
#MainMenu{{visibility:hidden !important}}
footer{{visibility:hidden !important}}

/* Pestañas nativas de Streamlit (st.tabs) con la misma identidad tipográfica */
[data-testid="stTabs"] button p{{font-family:'Playfair Display',serif;font-weight:600;font-size:.98rem}}
[data-testid="stTabs"] [aria-selected="true"]{{border-bottom-color:{GOLD_LIGHT} !important}}
[data-testid="stTabs"] [aria-selected="true"] p{{color:{GOLD_LIGHT} !important}}

@keyframes cardIn{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes ringSpin{{to{{transform:rotate(360deg)}}}}
@keyframes shimmerSweep{{0%{{left:-60%}}55%{{left:130%}}100%{{left:130%}}}}

/* Mapa de módulos: tarjetas vivas con borde dorado giratorio y aparición suave */
.mod-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:22px}}
.mod-card{{display:flex;align-items:center;gap:14px;border-radius:14px;position:relative;
    padding:16px 18px;background:{PANEL};overflow:hidden;isolation:isolate;
    border:1px solid {BORDER};
    transition:transform .25s ease,box-shadow .25s ease,border-color .25s ease;
    animation:cardIn .55s ease both}}
.mod-grid .mod-card:nth-child(1){{animation-delay:.02s}}
.mod-grid .mod-card:nth-child(2){{animation-delay:.09s}}
.mod-grid .mod-card:nth-child(3){{animation-delay:.16s}}
.mod-grid .mod-card:nth-child(4){{animation-delay:.23s}}
.mod-grid .mod-card:nth-child(5){{animation-delay:.30s}}
.mod-grid .mod-card:nth-child(6){{animation-delay:.37s}}
.mod-card::before{{content:"";position:absolute;inset:0;padding:1.5px;border-radius:14px;z-index:-1;
    background:conic-gradient(from 0deg,{GOLD} 0deg,transparent 55deg,transparent 305deg,{GOLD} 360deg);
    -webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
    -webkit-mask-composite:xor;mask-composite:exclude;
    opacity:0;transition:opacity .3s ease;animation:ringSpin 3.2s linear infinite}}
.mod-card::after{{content:"";position:absolute;top:0;left:-60%;width:45%;height:100%;
    background:linear-gradient(115deg,transparent,rgba(255,255,255,.10),transparent);
    transform:skewX(-18deg);animation:shimmerSweep 3.8s ease-in-out infinite;pointer-events:none}}
.mod-card:hover{{transform:translateY(-6px) scale(1.015);border-color:transparent;
    box-shadow:0 18px 36px rgba(0,0,0,.5),0 0 0 1px rgba(227,167,62,.25)}}
.mod-card:hover::before{{opacity:1}}
.mod-icon{{width:42px;height:42px;flex:0 0 42px;border-radius:12px;display:flex;align-items:center;
    justify-content:center;font-size:1.25rem;background:linear-gradient(160deg,rgba(227,167,62,.22),rgba(79,143,196,.14))}}
.mod-name{{font-family:'Playfair Display',serif;font-weight:600;font-size:1rem;color:{TEXT}}}
.mod-desc{{color:{MUTED_LIGHT};font-size:.8rem;margin-top:2px}}

.mv-grid{{display:grid;grid-template-columns:1fr 1fr;gap:0;margin-top:22px;border-radius:20px;
    overflow:hidden;border:1px solid {BORDER};box-shadow:0 14px 34px rgba(0,0,0,.4)}}
.mv-card{{padding:36px 34px;position:relative;text-align:center;transition:background .25s ease}}
.mv-card.steel{{background:linear-gradient(160deg,rgba(79,143,196,.12),rgba(255,255,255,.015))}}
.mv-card.gold{{background:linear-gradient(160deg,rgba(227,167,62,.10),rgba(255,255,255,.015));
    border-left:1px solid {BORDER}}}
.mv-badge{{width:54px;height:54px;border-radius:50%;display:flex;align-items:center;
    justify-content:center;font-size:1.6rem;margin:0 auto 18px}}
.mv-card.gold .mv-badge{{background:radial-gradient(circle,{GOLD_LIGHT},{GOLD});
    box-shadow:0 8px 20px rgba(227,167,62,.4)}}
.mv-card.steel .mv-badge{{background:radial-gradient(circle,{STEEL_LIGHT},{STEEL});
    box-shadow:0 8px 20px rgba(79,143,196,.4)}}
.mv-label{{text-transform:uppercase;letter-spacing:.14em;font-weight:800;font-size:.75rem;margin-bottom:10px}}
.mv-card.gold .mv-label{{color:{GOLD_LIGHT}}}
.mv-card.steel .mv-label{{color:{STEEL_LIGHT}}}
.mv-card p{{color:{TEXT};font-family:Georgia,'Times New Roman',serif;font-style:italic;
    line-height:1.85;font-size:1.05rem;letter-spacing:.15px;margin:0 auto;max-width:52ch;position:relative}}
.mv-card p::before{{content:"“";display:block;font-family:Georgia,serif;font-size:2.6rem;
    line-height:.5;margin:0 auto 14px;font-style:normal;text-align:center}}
.mv-card.gold p::before{{color:{GOLD}}}
.mv-card.steel p::before{{color:{STEEL}}}
@media(max-width:900px){{.mv-grid{{grid-template-columns:1fr}}.mv-card.gold{{border-left:none;
    border-top:1px solid {BORDER}}}.mod-grid{{grid-template-columns:1fr 1fr}}}}

@media(max-width:800px){{.block-container{{padding:1.2rem}}.mod-grid{{grid-template-columns:1fr}}}}
</style>""", unsafe_allow_html=True)

st.markdown(
    f'<div class="hero">{logo_html}'
    '<div class="eyebrow">LAVADORA S.A. · INTELIGENCIA COMERCIAL</div>'
    '<h1>Bienvenido a LubriInsight</h1>'
    '<p>La plataforma que convierte cada lavado, lubricación y venta de Lavadora S.A. en '
    'información clara, predicciones confiables y recomendaciones concretas — para decidir '
    'con datos, no con intuición.</p>'
    '<div class="hero-tags">'
    '<span class="hero-tag">📊 Datos en tiempo real</span>'
    '<span class="hero-tag">🤖 Predicción de recurrencia</span>'
    '<span class="hero-tag">🎯 Recomendaciones accionables</span>'
    '</div></div>',
    unsafe_allow_html=True,
)

_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix=""):
    """Tarjeta KPI profesional con número que cuenta en vivo desde 0 hasta su valor real."""
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"
    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; }}
      .kpi-card {{
        background:{PANEL}; border:1px solid {BORDER}; border-radius:16px; padding:20px 18px;
        box-shadow:0 8px 22px rgba(0,0,0,.35); position:relative; overflow:hidden;
        border-top:3px solid {accent}; box-sizing:border-box;
      }}
      .kpi-badge {{
        width:40px; height:40px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:1.15rem; margin-bottom:12px;
        background:radial-gradient(circle,{accent}55,{accent}22);
      }}
      .kpi-label {{ text-transform:uppercase; letter-spacing:.1em; font-weight:800; font-size:.72rem;
        margin-bottom:6px; color:{accent}; }}
      .kpi-value {{ font-size:2rem; font-weight:800; color:{TEXT}; font-variant-numeric:tabular-nums; line-height:1.1; }}
      .kpi-sub {{ color:{GREEN}; font-size:.8rem; margin-top:6px; font-weight:600; }}
    </style>
    <div class="kpi-card">
      <div class="kpi-badge">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value"><span id="{uid}">0</span></div>
      <div class="kpi-sub">↑ {subtext}</div>
    </div>
    <script>
    (function(){{
      const el = document.getElementById("{uid}");
      const end = {value};
      const decimals = {decimals};
      const prefix = "{prefix}";
      const start = performance.now();
      const duration = 1500;
      function step(ts){{
        const p = Math.min((ts - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const current = eased * end;
        el.textContent = prefix + current.toLocaleString('es-ES', {{minimumFractionDigits: decimals, maximumFractionDigits: decimals}});
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = prefix + end.toLocaleString('es-ES', {{minimumFractionDigits: decimals, maximumFractionDigits: decimals}});
      }}
      requestAnimationFrame(step);
    }})();
    </script>'''
    components.html(html, height=170)


try:
    kpi = query_df("""SELECT COUNT(*) AS ventas, COUNT(DISTINCT cedula_cliente) AS clientes,
        COALESCE(SUM(total),0) AS ingresos FROM venta WHERE total IS NOT NULL""").iloc[0]
    products = query_df("SELECT COUNT(*) AS productos FROM producto").iloc[0, 0]
    cards = st.columns(4)
    with cards[0]: kpi_counter("👥", "CLIENTES", int(kpi.clientes), "Clientes identificados en ventas", GOLD_LIGHT)
    with cards[1]: kpi_counter("🧾", "VENTAS", int(kpi.ventas), "Transacciones registradas", STEEL_LIGHT)
    with cards[2]: kpi_counter("📦", "PRODUCTOS", int(products), "Catálogo disponible", "#3FA6A6")
    with cards[3]: kpi_counter("💰", "INGRESOS", float(kpi.ingresos), "Facturación acumulada", GOLD_LIGHT, decimals=2, prefix="$")
    st.markdown('<div class="status">🟢 ESTADO GENERAL DEL NEGOCIO · La información comercial está disponible y conectada a PostgreSQL.</div>', unsafe_allow_html=True)

    # -----------------------------------------------------------------
    # Misión y visión (misión primero: qué hacemos hoy; visión: hacia dónde vamos)
    # -----------------------------------------------------------------
    st.markdown(
        '<div class="section"><div class="eyebrow">IDENTIDAD CORPORATIVA</div>'
        '<h2>Misión y visión</h2>'
        '<p class="muted">Los principios que guían a Lavadora S.A. en su transformación hacia un negocio impulsado por datos.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mv-grid">'
        '<div class="mv-card steel"><div class="mv-badge">🤝</div><div class="mv-label">Misión</div>'
        '<p>Ofrecer servicios de lavado, lubricación y mantenimiento automotriz básico con calidad, '
        'rapidez y trato cercano, respaldados por tecnología y análisis de datos que nos permiten '
        'conocer mejor a cada cliente y hacer crecer el negocio de forma sostenida.</p></div>'
        '<div class="mv-card gold"><div class="mv-badge">🧭</div><div class="mv-label">Visión</div>'
        '<p>Consolidarnos como la lavadora y lubricadora líder del sector automotriz, reconocida por '
        'la confianza de sus clientes y por convertir cada dato en una decisión inteligente, camino '
        'a un negocio moderno, eficiente y en constante evolución.</p></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------
    # Mapa de módulos: nomenclatura final de cada página del sistema
    # -----------------------------------------------------------------
    st.markdown(
        '<div class="section"><div class="eyebrow">MÓDULOS DISPONIBLES</div>'
        '<h2>Explora el sistema</h2>'
        '<p class="muted">Accede a cada módulo desde el menú lateral.</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('''<div class="mod-grid">
        <div class="mod-card"><div class="mod-icon">🏠</div><div>
            <div class="mod-name">Inicio</div><div class="mod-desc">Contexto general del negocio</div></div></div>
        <div class="mod-card"><div class="mod-icon">📊</div><div>
            <div class="mod-name">Dashboard Ejecutivo</div><div class="mod-desc">Indicadores clave de gestión</div></div></div>
        <div class="mod-card"><div class="mod-icon">⚙️</div><div>
            <div class="mod-name">Procesamiento</div><div class="mod-desc">Calidad y preparación de datos</div></div></div>
        <div class="mod-card"><div class="mod-icon">🤖</div><div>
            <div class="mod-name">Predicción</div><div class="mod-desc">Modelos de recurrencia y churn</div></div></div>
        <div class="mod-card"><div class="mod-icon">🏆</div><div>
            <div class="mod-name">Score Inteligente</div><div class="mod-desc">Priorización de clientes</div></div></div>
        <div class="mod-card"><div class="mod-icon">🎯</div><div>
            <div class="mod-name">Recomendaciones</div><div class="mod-desc">Próximas mejores acciones</div></div></div>
    </div>''', unsafe_allow_html=True)

except (SQLAlchemyError, Exception) as exc:
    st.error("No fue posible cargar los indicadores. Revisa que .env apunte a Lubricadora.")
    with st.expander("Detalle técnico"):
        st.exception(exc)