import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from utils.database import query_df
from utils.footer import show_footer

# ------------------------------------------------------------------
# Paleta unificada
# ------------------------------------------------------------------
BG = '#0A0B0F'
PANEL = 'rgba(255,255,255,0.045)'
PANEL_SOLID = '#12141B'
BORDER = 'rgba(255,255,255,0.10)'
GOLD = '#E3A73E'
GOLD_LIGHT = '#F5CF7A'
STEEL = '#4F8FC4'
STEEL_LIGHT = '#9CC9EC'
TEXT = '#EDEFF2'
MUTED = '#98A4B2'
GREEN = '#2ED18C'
RED = '#E5615B'
CHART_GOLD = GOLD_LIGHT
CHART_BLUE = STEEL_LIGHT
CHART_TEAL = '#3FA6A6'

PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    title_font=dict(size=19, color=GOLD_LIGHT, family='Playfair Display'),
    xaxis=dict(gridcolor='rgba(255,255,255,.08)', zerolinecolor='rgba(255,255,255,.10)',
               showspikes=True, spikethickness=1, spikedash='dot', spikecolor=GOLD_LIGHT),
    yaxis=dict(gridcolor='rgba(255,255,255,.08)', zerolinecolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT), bgcolor='rgba(0,0,0,0)'),
    hoverlabel=dict(bgcolor='#171A22', font_color=TEXT, bordercolor=GOLD_LIGHT, font_size=13),
    hovermode='x unified',
    margin=dict(t=60, l=10, r=10, b=10),
    transition=dict(duration=650, easing='cubic-in-out'),
)

st.set_page_config(page_title='LubriInsight | Procesamiento', page_icon='🔄', layout='wide')

# ------------------------------------------------------------------
# CSS unificado
# ------------------------------------------------------------------
st.markdown(f'''<style>
.stApp{{background:radial-gradient(circle at 15% -10%,rgba(217,169,76,.10),transparent 45%),
        radial-gradient(circle at 90% 10%,rgba(143,180,217,.08),transparent 40%),{BG};overflow-x:hidden}}
[data-testid="stHeader"]{{background:{BG} !important}}
[data-testid="stDecoration"]{{display:none !important}}
[data-testid="stSidebar"][aria-expanded="true"]{{min-width:270px !important;max-width:270px !important}}
[data-testid="stSidebar"]{{background:#07080B;border-right:1px solid {BORDER}}}
[data-testid="stSidebar"] *{{color:{TEXT} !important}}
[data-testid="stSidebarNav"] a{{border-radius:10px;margin:2px 8px;padding:10px 12px !important;
    transition:background .15s ease}}
[data-testid="stSidebarNav"] span{{font-family:'Playfair Display',serif;font-weight:600;
    font-size:.95rem;letter-spacing:.01em;white-space:normal !important}}
[data-testid="stSidebarNav"] a:hover{{background:rgba(227,167,62,.14) !important}}
[data-testid="stSidebarNav"] a[aria-current="page"]{{
    background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
    border-left:3px solid {GOLD_LIGHT}}}
[data-testid="stSidebarNav"] a[aria-current="page"] span{{color:{GOLD_LIGHT} !important}}

.block-container{{max-width:1450px;padding:2rem 4rem 4rem}}
h1,h2,h3{{color:{TEXT};letter-spacing:-.02em;font-family:'Playfair Display',serif}}
p, span, div, label{{color:{TEXT}}}

@keyframes fadeSlideUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes softPulse{{0%,100%{{opacity:.5}}50%{{opacity:1}}}}
@keyframes ringPulse{{0%{{box-shadow:0 0 0 0 rgba(227,167,62,.45)}}70%{{box-shadow:0 0 0 10px rgba(227,167,62,0)}}100%{{box-shadow:0 0 0 0 rgba(227,167,62,0)}}}}
@keyframes drawLine{{from{{stroke-dashoffset:400}}to{{stroke-dashoffset:0}}}}
@keyframes shimmerSweep{{0%{{transform:translateX(-120%)}}100%{{transform:translateX(220%)}}}}

.hero{{position:relative;background:linear-gradient(160deg,#14161F 0%,#0A0B0F 75%);border:1px solid rgba(227,167,62,.28);
    border-radius:20px;padding:28px 34px;margin-bottom:24px;box-shadow:0 18px 46px rgba(0,0,0,.55);
    animation:fadeSlideUp .55s ease-out;overflow:hidden}}
.hero::after{{content:'';position:absolute;top:0;left:-60%;width:40%;height:100%;
    background:linear-gradient(100deg,transparent,rgba(245,207,122,.06),transparent);
    animation:heroSheen 5s ease-in-out infinite}}
@keyframes heroSheen{{0%{{left:-60%}}50%{{left:120%}}100%{{left:120%}}}}
.hero h1{{margin:0 0 7px;font-size:clamp(1.7rem,2.6vw,2.5rem);display:flex;align-items:center;gap:12px;
    background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero .hero-icon{{-webkit-text-fill-color:initial;display:inline-block;animation:softPulse 2.4s ease-in-out infinite}}
.hero p{{color:{MUTED};margin:0;max-width:70ch;line-height:1.55}}
.eyebrow{{text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:800;color:{GOLD};margin-bottom:10px;
    display:flex;align-items:center;gap:8px}}
.eyebrow .dot{{width:7px;height:7px;border-radius:50%;background:{GOLD_LIGHT};box-shadow:0 0 8px {GOLD_LIGHT};
    animation:softPulse 1.8s ease-in-out infinite}}

.section-title{{font-family:'Playfair Display',serif;font-size:1.3rem;font-weight:700;color:{TEXT};
    display:flex;align-items:center;gap:10px;margin:26px 0 14px 0}}
.section-title .bar{{width:5px;height:22px;border-radius:3px;
    background:linear-gradient(180deg,{GOLD_LIGHT},{STEEL_LIGHT});box-shadow:0 0 10px rgba(245,207,122,.5)}}
.chart-title{{font-family:'Playfair Display',serif;color:{GOLD_LIGHT};font-size:1.1rem;font-weight:700;margin:2px 0 10px 6px}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:15px;padding:16px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

[data-baseweb="tab-list"]{{border-bottom:1px solid {BORDER};gap:4px}}
[data-baseweb="tab"]{{color:{MUTED};font-weight:500;transition:color .2s ease}}
[data-baseweb="tab"]:hover{{color:{GOLD_LIGHT} !important}}
[aria-selected="true"][data-baseweb="tab"]{{color:{GOLD_LIGHT} !important}}
[data-baseweb="tab-highlight"]{{background-color:{GOLD_LIGHT} !important;box-shadow:0 0 8px {GOLD_LIGHT}}}

[data-testid="stAlert"]{{background:{PANEL};border:1px solid {BORDER};border-left:3px solid {STEEL_LIGHT};
    border-radius:12px;color:{TEXT};animation:fadeSlideUp .5s ease-out}}

[data-testid="stDataFrame"]{{border:1px solid rgba(227,167,62,.22) !important;border-radius:14px !important;
    overflow:hidden;box-shadow:0 10px 26px rgba(0,0,0,.4),0 0 0 1px rgba(227,167,62,.06) inset;
    animation:fadeSlideUp .55s ease-out}}
[data-testid="stExpander"]{{background:{PANEL};border:1px solid {BORDER};border-radius:12px}}
[data-testid="stExpander"] summary{{color:{STEEL_LIGHT} !important;font-weight:600}}

[data-testid="stDownloadButton"] button{{background:linear-gradient(135deg,{GOLD},{GOLD_LIGHT}) !important;
    color:#0A0B0F !important;font-weight:700 !important;border:none !important;border-radius:10px !important;
    box-shadow:0 6px 18px rgba(227,167,62,.30);transition:transform .2s ease,box-shadow .2s ease}}
[data-testid="stDownloadButton"] button:hover{{transform:translateY(-2px);box-shadow:0 10px 24px rgba(227,167,62,.45)}}

[data-testid="stDateInput"]{{background:{PANEL} !important;border:1px solid {BORDER} !important;
    border-radius:8px;padding:2px 6px}}
[data-testid="stDateInput"] div{{background:transparent !important}}
[data-testid="stDateInput"] input{{color:{TEXT} !important;background:transparent !important}}
[data-testid="stSelectbox"]{{background:{PANEL} !important;border:1px solid {BORDER} !important;border-radius:8px}}
[data-testid="stSelectbox"] div{{background:transparent !important}}
[data-testid="stSelectbox"] *{{color:{TEXT} !important}}
[data-baseweb="popover"],[data-baseweb="calendar"],[data-baseweb="menu"]{{background:{PANEL_SOLID} !important}}
[data-baseweb="popover"] *,[data-baseweb="calendar"] *,[data-baseweb="menu"] *{{color:{TEXT} !important}}
ul[role="listbox"]{{background:{PANEL_SOLID} !important}}
li[role="option"]{{background:{PANEL_SOLID} !important;color:{TEXT} !important}}
li[role="option"]:hover{{background:rgba(255,255,255,.08) !important}}

[data-testid="stVerticalBlockBorderWrapper"]{{background:linear-gradient(160deg,rgba(227,167,62,.07),rgba(255,255,255,.015));
    border:1px solid rgba(227,167,62,.25) !important;border-radius:16px !important;
    box-shadow:0 14px 32px rgba(0,0,0,.45);padding:8px;
    animation:fadeSlideUp .6s ease-out;transition:transform .25s ease,box-shadow .25s ease}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{transform:translateY(-3px);box-shadow:0 20px 40px rgba(0,0,0,.55)}}

.badge{{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:.78rem;font-weight:700}}
.badge-red{{background:rgba(229,97,91,.15);color:{RED};border:1px solid rgba(229,97,91,.35)}}
.badge-green{{background:rgba(46,209,140,.15);color:{GREEN};border:1px solid rgba(46,209,140,.35)}}

/* Selector superior estilizado como pestañas — reemplaza tabs anidados (que apagaban los contadores JS) */
div[role="radiogroup"]{{display:flex;gap:6px;border-bottom:1px solid {BORDER};margin-bottom:20px;padding-bottom:0}}
div[role="radiogroup"] label{{background:transparent;border:none;border-bottom:2px solid transparent;
    border-radius:0;padding:9px 4px;margin-right:26px;transition:color .2s ease,border-color .2s ease;cursor:pointer}}
div[role="radiogroup"] label:hover div{{color:{GOLD_LIGHT} !important}}
div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child{{display:none}}
div[role="radiogroup"] label div{{color:{MUTED};font-family:'Playfair Display',serif;font-weight:600;font-size:1rem}}
div[role="radiogroup"] label:has(input:checked){{border-bottom:2px solid {GOLD_LIGHT}}}
div[role="radiogroup"] label:has(input:checked) div{{color:{GOLD_LIGHT} !important}}

@media(max-width:900px){{.block-container{{padding:1.2rem}}}}
</style>''', unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><div class="eyebrow"><span class="dot"></span>LAVADORA S.A. · PIPELINE ANALÍTICO</div>'
    '<h1><span class="hero-icon">🔄</span>Procesamiento</h1>'
    '<p>De los datos crudos al dataset listo para modelar: primero exploramos qué tenemos '
    '(volumen, nulos, duplicados, comportamiento comercial) y luego mostramos cómo se resuelve cada '
    'problema, paso a paso. La fuente en PostgreSQL nunca se modifica; todo se calcula en memoria.</p></div>',
    unsafe_allow_html=True)

TABLES = ['categoria', 'cliente', 'compra', 'detalle_compra', 'detalle_servicio', 'detalle_venta', 'empleado',
          'encabezado_servicio', 'historial_abono', 'inventario', 'producto', 'producto_proveedor', 'proveedor',
          'servicio', 'tipo_documento', 'tipo_pago', 'tipo_producto', 'tipo_proveedor', 'vehiculo', 'venta']


# ------------------------------------------------------------------
# Tarjeta KPI dinámica: número que cuenta en vivo, borde con brillo
# giratorio, badge de tendencia opcional y mini-sparkline opcional.
# ------------------------------------------------------------------
_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix="", trend_pct=None, spark=None):
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"

    trend_html = ""
    if trend_pct is not None:
        up = trend_pct >= 0
        tcolor = GREEN if up else RED
        tarrow = "▲" if up else "▼"
        trend_html = (f'<div class="kpi-trend" style="color:{tcolor};background:{tcolor}22;'
                      f'border:1px solid {tcolor}55">{tarrow} {abs(trend_pct):.1f}%</div>')

    spark_html = ""
    if spark and len(spark) >= 2:
        w, h, pad = 140, 34, 4
        lo, hi = min(spark), max(spark)
        span = (hi - lo) or 1
        step = (w - 2 * pad) / (len(spark) - 1)
        pts = [(pad + i * step, h - pad - ((v - lo) / span) * (h - 2 * pad)) for i, v in enumerate(spark)]
        path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        area = f"{pad},{h-pad} " + path + f" {w-pad},{h-pad}"
        spark_html = f'''
        <svg class="kpi-spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none">
          <polygon points="{area}" fill="{accent}22"></polygon>
          <polyline points="{path}" fill="none" stroke="{accent}" stroke-width="2.2"
            stroke-linecap="round" stroke-linejoin="round"
            style="stroke-dasharray:400;animation:drawLine 1.3s ease-out forwards"></polyline>
        </svg>'''

    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; overflow:visible; }}
      @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
      @property --a{{syntax:'<angle>';initial-value:0deg;inherits:false}}
      @keyframes spin{{to{{--a:360deg}}}}
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
      .kpi-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
      .kpi-badge{{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;
        justify-content:center;font-size:1.05rem;
        background:radial-gradient(circle,{accent}55,{accent}22);
        animation:ringPulse 2.6s ease-out infinite}}
      .kpi-trend{{font-size:.7rem;font-weight:800;padding:2px 8px;border-radius:999px}}
      .kpi-label{{text-transform:uppercase;letter-spacing:.1em;font-weight:800;font-size:.7rem;
        margin-bottom:6px;color:{accent}}}
      .kpi-value{{font-size:1.8rem;font-weight:800;font-variant-numeric:tabular-nums;
        background:linear-gradient(90deg,{TEXT},{accent});-webkit-background-clip:text;
        background-clip:text;-webkit-text-fill-color:transparent}}
      .kpi-sub{{color:{MUTED};font-size:.75rem;margin-top:4px}}
      .kpi-spark{{width:100%;height:34px;margin-top:10px;display:block}}
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
        {spark_html}
      </div>
    </div>
    <script>
    (function(){{
      const el = document.getElementById("{uid}");
      const end = {value}; const decimals = {decimals}; const prefix = "{prefix}";
      const start = performance.now(); const duration = 1400;
      function step(ts){{
        const p = Math.min((ts - start) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + (eased*end).toLocaleString('es-ES', {{minimumFractionDigits:decimals,maximumFractionDigits:decimals}});
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = prefix + end.toLocaleString('es-ES', {{minimumFractionDigits:decimals,maximumFractionDigits:decimals}});
      }}
      requestAnimationFrame(step);
    }})();
    </script>'''
    components.html(html, height=185 if spark_html else 150)


def section_title(text: str):
    st.markdown(f'<div class="section-title"><span class="bar"></span>{text}</div>', unsafe_allow_html=True)


def chart_title(text: str):
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# Tarjeta de "antes → después" con barra de progreso animada y
# porcentaje de cambio.
# ------------------------------------------------------------------
_counter_id = [0]
def animated_counter(icon, label, start_val, end_val, better_when='down'):
    _counter_id[0] += 1
    uid = f'cnt{_counter_id[0]}'
    delta = end_val - start_val
    improved = (delta < 0) if better_when == 'down' else (delta > 0)
    delta_color = GREEN if improved or delta == 0 else RED
    arrow = '↓' if delta < 0 else ('↑' if delta > 0 else '→')
    delta_txt = f'{arrow} {abs(delta):,} {"tratados" if better_when=="down" else "registrados"}'
    pct = (abs(delta) / start_val * 100) if start_val else 0
    end_pct = max(2, min(100, (end_val / start_val * 100) if start_val else 0))
    html = f'''
    <style>
      html,body{{margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif;overflow:visible}}
      @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}
      @keyframes fillBar{{from{{width:100%}}to{{width:{end_pct:.2f}%}}}}
      .cnt-card{{background:{PANEL};border:1px solid {BORDER};border-top:3px solid {GOLD_LIGHT};border-radius:15px;
        padding:16px 20px;box-shadow:0 8px 22px rgba(0,0,0,.35);animation:fadeIn .5s ease-out;
        transition:transform .2s ease;box-sizing:border-box}}
      .cnt-card:hover{{transform:translateY(-2px)}}
      .cnt-label{{color:{STEEL_LIGHT};font-size:.82rem;font-weight:700;margin-bottom:8px;
        text-transform:uppercase;letter-spacing:.06em;display:flex;align-items:center;
        justify-content:space-between;gap:7px}}
      .cnt-pct{{font-size:.78rem;font-weight:800;color:{delta_color};background:{delta_color}22;
        padding:2px 9px;border-radius:999px;border:1px solid {delta_color}55}}
      .cnt-row{{display:flex;align-items:baseline;gap:10px}}
      .cnt-num{{font-size:2rem;font-weight:800;color:{TEXT};font-variant-numeric:tabular-nums}}
      .cnt-num-end{{font-size:2rem;font-weight:800;color:{GOLD_LIGHT};font-variant-numeric:tabular-nums;
        text-shadow:0 2px 8px rgba(227,167,62,.30)}}
      .cnt-arrow{{color:{MUTED};font-size:1.2rem}}
      .cnt-delta{{color:{MUTED};font-size:.78rem;margin-top:8px}}
      .cnt-track{{position:relative;height:7px;border-radius:99px;background:rgba(255,255,255,.08);
        margin-top:10px;overflow:hidden}}
      .cnt-fill{{position:absolute;left:0;top:0;height:100%;border-radius:99px;
        background:linear-gradient(90deg,{STEEL_LIGHT},{GOLD_LIGHT});
        animation:fillBar 1.5s cubic-bezier(.22,1,.36,1) forwards}}
    </style>
    <div class="cnt-card">
      <div class="cnt-label">{icon} {label} <span class="cnt-pct">{pct:.1f}%</span></div>
      <div class="cnt-row">
        <span id="{uid}a" class="cnt-num">0</span>
        <span class="cnt-arrow">→</span>
        <span id="{uid}b" class="cnt-num-end">0</span>
      </div>
      <div class="cnt-track"><div class="cnt-fill"></div></div>
      <div class="cnt-delta">{delta_txt}</div>
    </div>
    <script>
    (function(){{
      function animate(id, end, duration){{
        const el = document.getElementById(id);
        const start = performance.now();
        function step(ts){{
          const p = Math.min((ts - start) / duration, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.floor(eased * end).toLocaleString('es-ES');
          if (p < 1) requestAnimationFrame(step); else el.textContent = end.toLocaleString('es-ES');
        }}
        requestAnimationFrame(step);
      }}
      animate("{uid}a", {start_val}, 1100);
      animate("{uid}b", {end_val}, 1400);
    }})();
    </script>'''
    components.html(html, height=155)


def tabla_iluminada(df: pd.DataFrame, col_badge: str | None = None):
    """Tabla HTML propia con franja superior dorada y resaltado de fila al pasar el mouse."""
    cols = df.columns.tolist()
    head = "".join(f'<th style="padding:11px 16px;text-align:left;color:{MUTED};font-weight:700;'
                    f'text-transform:uppercase;font-size:.72rem;letter-spacing:.06em">{c}</th>' for c in cols)
    rows_html = ""
    for _, r in df.iterrows():
        cells = ""
        for c in cols:
            val = r[c]
            if c == col_badge:
                try:
                    n = int(val)
                except Exception:
                    n = 0
                cls = "badge-green" if n == 0 else "badge-red"
                icon = "✓" if n == 0 else "⚠"
                cells += f'<td style="padding:11px 16px"><span class="badge {cls}">{icon} {val}</span></td>'
            else:
                cells += f'<td style="padding:11px 16px;color:{TEXT}">{val}</td>'
        rows_html += f'<tr class="tabla-ilum-row">{cells}</tr>'
    html = f'''
    <style>
      .tabla-ilum-row{{transition:background .15s ease}}
      .tabla-ilum-row:hover{{background:rgba(227,167,62,.08)}}
    </style>
    <div style="border:1px solid rgba(227,167,62,.22);border-radius:14px;overflow:hidden;
        box-shadow:0 10px 26px rgba(0,0,0,.4);animation:fadeSlideUp .5s ease-out">
      <table style="width:100%;border-collapse:collapse;font-size:.92rem">
        <thead><tr style="background:{PANEL_SOLID};border-bottom:1px solid rgba(227,167,62,.25)">{head}</tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>'''
    st.markdown(html, unsafe_allow_html=True)


def styled_area(df, x, y, color, title, height=390):
    """Área suavizada con gradiente, spline y hover unificado — reutilizable en ambos bloques."""
    fig = px.area(df, x=x, y=y, markers=True, color_discrete_sequence=[color])
    fig.update_traces(
        line=dict(width=4, color=color, shape='spline', smoothing=0.6),
        marker=dict(size=9, color=GOLD_LIGHT, line=dict(width=2, color=PANEL_SOLID)),
        fill='tozeroy', fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},.22)',
    )
    fig.update_layout(title=title, height=height, **PLOTLY_LAYOUT)
    return fig


def styled_bar(df, x, y, title, color_scale=None, height=None):
    """Barra horizontal con degradado por valor, esquinas redondeadas y estilo consistente."""
    if color_scale is None:
        color_scale = [STEEL, GOLD_LIGHT]
    fig = px.bar(df, x=x, y=y, orientation='h', color=x, color_continuous_scale=color_scale, title=title)
    try:
        fig.update_traces(marker=dict(cornerradius=8, line=dict(width=1, color=PANEL_SOLID)))
    except Exception:
        fig.update_traces(marker=dict(line=dict(width=1, color=PANEL_SOLID)))
    fig.update_layout(coloraxis_showscale=False, **PLOTLY_LAYOUT)
    if height:
        fig.update_layout(height=height)
    return fig


# ------------------------------------------------------------------
# Bloque 1: Exploración
# ------------------------------------------------------------------
def render_exploracion():
    try:
        dates = query_df('select min(fecha_venta)::date minimo,max(fecha_venta)::date maximo from venta').iloc[0]
        min_date, max_date = pd.Timestamp(dates.minimo), pd.Timestamp(dates.maximo)
        with st.sidebar:
            st.markdown('### Filtros · Exploración')
            period = st.date_input('Período de ventas', value=(min_date.date(), max_date.date()),
                                    min_value=min_date.date(), max_value=max_date.date(), key='explora_period')
            top_n = st.slider('Elementos visibles', 5, 20, 10, key='explora_topn')
        if len(period) != 2:
            st.info('Selecciona fecha inicial y final.')
            return
        start, end = pd.Timestamp(period[0]), pd.Timestamp(period[1])
        params = {'start': start.date(), 'end': end.date()}
        k = query_df('select count(*) registros,count(distinct cedula_cliente) clientes,coalesce(sum(total),0) ingresos,coalesce(avg(total),0) ticket from venta where fecha_venta::date between :start and :end', params).iloc[0]

        spark_df = query_df(
            "select date_trunc('week',fecha_venta)::date semana,count(*) registros,coalesce(sum(total),0) ingresos "
            "from venta where fecha_venta::date between :start and :end group by 1 order by 1", params)
        spark_reg = spark_df['registros'].tail(8).tolist()
        spark_ing = spark_df['ingresos'].tail(8).tolist()

        a, b, c, d = st.columns(4)
        with a:
            kpi_counter('🧾', 'Registros de venta', int(k.registros), 'En el período seleccionado', GOLD_LIGHT,
                        spark=spark_reg)
        with b:
            kpi_counter('👥', 'Clientes', int(k.clientes), 'Con compras en el período', STEEL_LIGHT)
        with c:
            kpi_counter('💰', 'Ingresos', float(k.ingresos), 'Total facturado', GOLD_LIGHT, decimals=2, prefix='$',
                        spark=spark_ing)
        with d:
            kpi_counter('🎟️', 'Ticket promedio', float(k.ticket), 'Por transacción', CHART_TEAL, decimals=2, prefix='$')

        sub_tabs = st.tabs(['Calidad general', 'Ventas', 'Clientes', 'Productos', 'Variables'])
        with sub_tabs[0]:
            rows = []
            for table in TABLES:
                df = query_df(f'select * from {table}')
                empty_cells = int(df.isna().sum().sum())
                empty_text = int((df.astype(str).apply(lambda col: col.str.strip().eq('').sum())).sum()) if not df.empty else 0
                rows.append({'Tabla': table, 'Registros': len(df), 'Variables': len(df.columns),
                             'Nulos': empty_cells, 'Vacíos': empty_text, 'Duplicados': int(df.duplicated().sum())})
            quality = pd.DataFrame(rows)
            with st.expander("📄 Ver tabla completa de calidad por tabla", expanded=False):
                st.dataframe(quality, use_container_width=True, hide_index=True)
            bad = quality[(quality.Nulos > 0) | (quality.Vacíos > 0) | (quality.Duplicados > 0)]
            if bad.empty:
                st.success('No se detectaron problemas de calidad en las tablas auditadas.')
            else:
                st.warning(f'Se identificaron {len(bad)} tablas con al menos un indicador de calidad para tratar.')
            st.subheader('Diagnóstico')
            st.info(f'La base contiene {int(quality.Registros.sum()):,} registros distribuidos en {len(TABLES)} tablas. El tratamiento se realiza más abajo en Preprocesamiento, sin modificar PostgreSQL.')
        with sub_tabs[1]:
            monthly = query_df("select date_trunc('month',fecha_venta)::date mes,count(*) ventas,coalesce(sum(total),0) ingresos from venta where fecha_venta::date between :start and :end group by 1 order by 1", params)
            fig = styled_area(monthly, 'mes', 'ingresos', STEEL_LIGHT, 'Evolución mensual de ingresos')
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            with st.expander("📄 Ver datos mensuales completos", expanded=False):
                st.dataframe(monthly, use_container_width=True, hide_index=True)
        with sub_tabs[2]:
            clients = query_df("select c.nombre||' '||coalesce(c.apellido,'') cliente,count(distinct v.id_venta) frecuencia,max(v.fecha_venta)::date ultima_compra,coalesce(sum(v.total),0) monto from cliente c join venta v on v.cedula_cliente=c.cedula where v.fecha_venta::date between :start and :end group by c.cedula,c.nombre,c.apellido order by monto desc", params)
            fig_c = styled_bar(clients.head(top_n).sort_values('monto'), 'monto', 'cliente',
                                f'Top {top_n} clientes por monto', color_scale=[STEEL, STEEL_LIGHT, GOLD_LIGHT])
            fig_h = px.histogram(clients, x='frecuencia', nbins=20, color_discrete_sequence=[CHART_TEAL], title='Frecuencia de compra')
            fig_h.update_traces(marker_line_width=1, marker_line_color=PANEL_SOLID)
            try:
                fig_h.update_traces(marker=dict(cornerradius=6))
            except Exception:
                pass
            fig_h.update_layout(**PLOTLY_LAYOUT)
            x, y = st.columns(2)
            with x:
                with st.container(border=True):
                    st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": False})
            with y:
                with st.container(border=True):
                    st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})
            with st.expander("📄 Ver tabla completa de clientes", expanded=False):
                st.dataframe(clients, use_container_width=True, hide_index=True)
        with sub_tabs[3]:
            products = query_df("select p.nombre producto,coalesce(c.nombre,'Sin categoría') categoria,sum(dv.cantidad) unidades,sum(dv.cantidad*coalesce(p.precio,0)) ingresos from detalle_venta dv join venta v on v.id_venta=dv.id_venta join producto p on p.id_producto=dv.id_producto left join categoria c on c.id_categoria=p.id_categoria where v.fecha_venta::date between :start and :end group by p.id_producto,p.nombre,c.nombre order by ingresos desc limit :limit", {**params, 'limit': top_n})
            fig_p = styled_bar(products.sort_values('ingresos'), 'ingresos', 'producto',
                                f'Top {top_n} productos por ingresos', color_scale=[GOLD, GOLD_LIGHT])
            with st.container(border=True):
                st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar": False})
            with st.expander("📄 Ver tabla completa de productos", expanded=False):
                st.dataframe(products, use_container_width=True, hide_index=True)
        with sub_tabs[4]:
            table = st.selectbox('Selecciona una tabla', TABLES, key='explora_tabla')
            df = query_df(f'select * from {table}')
            st.write(f'{len(df):,} registros · {len(df.columns)} variables')
            st.dataframe(pd.DataFrame({
                'Variable': df.columns, 'Tipo': df.dtypes.astype(str), 'Nulos': df.isna().sum().values,
                'Vacíos': [(df[col].astype(str).str.strip() == '').sum() for col in df.columns]
            }), use_container_width=True, hide_index=True)
    except Exception as exc:
        st.error('No fue posible cargar Exploración. Revisa la conexión a Lubricadora y las tablas reales.')
        with st.expander('Detalle técnico'):
            st.exception(exc)


# ------------------------------------------------------------------
# Bloque 2: Preprocesamiento
# ------------------------------------------------------------------
def render_preprocesamiento():
    st.info('🔒 Modo seguro: no hay UPDATE, DELETE, INSERT ni botones de persistencia. PostgreSQL solo se consulta.')
    try:
        raw = query_df('select * from venta')
        clean = raw.copy()
        clean = clean.drop_duplicates()
        clean['fecha_venta'] = pd.to_datetime(clean['fecha_venta'], errors='coerce')
        clean['total'] = pd.to_numeric(clean['total'], errors='coerce')
        clean['cedula_cliente'] = clean['cedula_cliente'].astype('string').str.strip()
        clean = clean.dropna(subset=['fecha_venta', 'total', 'cedula_cliente'])
        clean = clean[clean['cedula_cliente'] != '9999999999999']

        n1, n2 = st.columns(2)
        with n1: animated_counter('📊', 'Registros', len(raw), len(clean), better_when='down')
        with n2: animated_counter('🧩', 'Nulos', int(raw.isna().sum().sum()), int(clean.isna().sum().sum()), better_when='down')

        st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
        sub_tabs = st.tabs(['🧼 Data Cleaning', '🎯 Data Reduction', '🔄 Data Transformation', '✅ Dataset final'])

        with sub_tabs[0]:
            section_title("🧼 Problemas detectados y cómo se resolvieron")
            q = pd.DataFrame({
                'Problema': ['🔁 Duplicados', '📅 Fecha inválida o nula', '💲 Total inválido o nulo', '👤 Cliente genérico'],
                'Antes': [int(raw.duplicated().sum()),
                          int(pd.to_datetime(raw.fecha_venta, errors='coerce').isna().sum()),
                          int(pd.to_numeric(raw.total, errors='coerce').isna().sum()),
                          int(raw.cedula_cliente.astype(str).eq('9999999999999').sum())],
                'Tratamiento': ['Eliminar duplicados en memoria', 'Convertir a fecha y excluir inválidos',
                                'Convertir a numérico y excluir inválidos', 'Excluir del modelado individual'],
            })
            tabla_iluminada(q, col_badge='Antes')

        with sub_tabs[1]:
            section_title("🎯 Selección de variables")
            st.write('Para el modelado se conserva la llave técnica solo para relacionar resultados. Las variables comerciales se derivan de venta, detalle_venta, producto y cliente.')
            features = ['cedula_cliente', 'fecha_venta', 'total']
            r = pd.DataFrame({'Conservada': features, 'Motivo': ['Identificador técnico', 'Fecha temporal', 'Monto comercial']})
            tabla_iluminada(r)

        with sub_tabs[2]:
            section_title("🔄 Transformaciones aplicadas")
            st.code("fecha_venta → datetime\ntotal → numérico\ncedula_cliente → texto normalizado\ncliente genérico → excluido del modelado\ntratamiento → memoria, no PostgreSQL", language='text')
            monthly = clean.assign(mes=clean.fecha_venta.dt.to_period('M').astype(str)).groupby('mes', as_index=False).agg(registros=('id_venta', 'count'), ingresos=('total', 'sum'))
            with st.container(border=True):
                chart_title("📈 Serie resultante después de transformar")
                fig = styled_area(monthly, 'mes', 'ingresos', STEEL_LIGHT, '', height=360)
                fig.update_layout(margin=dict(t=10, b=20, l=10, r=20))
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with sub_tabs[3]:
            section_title("✅ Dataset final")
            st.markdown(
                f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px">'
                f'<span class="badge badge-green">📄 {len(clean):,} registros</span>'
                f'<span class="badge badge-green">🧬 {len(clean.columns):,} variables</span>'
                f'</div>', unsafe_allow_html=True)
            with st.expander("📄 Ver muestra del dataset final", expanded=False):
                st.dataframe(clean.head(200), use_container_width=True, hide_index=True)
            st.download_button('⬇ Descargar muestra preparada', clean.head(500).to_csv(index=False).encode('utf-8'), 'lubriinsight_muestra_preparada.csv', 'text/csv')
    except Exception as exc:
        st.error('No fue posible preparar los datos.')
        with st.expander('Detalle técnico'):
            st.exception(exc)


# ------------------------------------------------------------------
# Selector superior — una sola sección se renderiza por vez, así los
# contadores/JS de todas las tarjetas siempre se disparan correctamente.
# ------------------------------------------------------------------
seccion = st.radio(
    'Sección de procesamiento',
    ['🔎 Exploración', '🧹 Preprocesamiento'],
    horizontal=True,
    label_visibility='collapsed',
    key='procesamiento_seccion',
)

if seccion == '🔎 Exploración':
    render_exploracion()
else:
    render_preprocesamiento()

# Pie de página (autoría), agregado automáticamente
show_footer()
