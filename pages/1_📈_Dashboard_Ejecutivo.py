"""Dashboard Ejecutivo: conserva la lógica analítica original, adaptada a la nueva BD."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from utils.database import query_df
from utils.footer import show_footer

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
MUTED = "#98A4B2"
GREEN = "#2ED18C"
RED = "#E5615B"
RED_LIGHT = "#F2A29E"

st.set_page_config(page_title="LubriInsight | Dashboard", page_icon="📈", layout="wide")
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
.block-container{{max-width:1450px;padding:2rem 4rem 4rem}}
h1,h2,h3{{color:{TEXT};letter-spacing:-.03em;font-family:'Playfair Display',serif}}
p, span, div, label{{color:{TEXT}}}

.hero{{background:linear-gradient(160deg,#12141B 0%,#0A0B0F 70%);border:1px solid rgba(217,169,76,.25);
    border-radius:20px;padding:26px 32px;margin-bottom:22px;box-shadow:0 18px 46px rgba(0,0,0,.55)}}
.hero h1{{margin:0 0 7px;font-size:2.5rem;background:linear-gradient(90deg,{GOLD_LIGHT},{STEEL_LIGHT});
    -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
.hero p{{color:{MUTED};margin:0;max-width:70ch}}
.eyebrow{{text-transform:uppercase;letter-spacing:.1em;font-size:.72rem;font-weight:800;color:{GOLD};margin-bottom:10px}}

[data-testid="stMetric"]{{background:{PANEL};border:1px solid {BORDER};border-radius:15px;padding:16px;
    box-shadow:0 8px 22px rgba(0,0,0,.35);backdrop-filter:blur(6px)}}
[data-testid="stMetricValue"]{{color:{GOLD_LIGHT};font-variant-numeric:tabular-nums}}
[data-testid="stMetricLabel"]{{color:{STEEL_LIGHT} !important}}

.insight{{background:linear-gradient(160deg,rgba(227,167,62,.10),rgba(255,255,255,.015));
    border:1px solid rgba(227,167,62,.28);border-radius:15px;padding:18px 20px;margin:18px 0;
    box-shadow:0 10px 26px rgba(0,0,0,.35)}}
.insight small{{color:{GOLD_LIGHT};font-weight:900;letter-spacing:.1em}}
.insight strong{{display:block;font-size:1.15rem;margin:7px 0 3px;color:{TEXT};font-family:'Playfair Display',serif}}
.insight span{{color:{MUTED}}}

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

/* Tarjeta destacada para gráficos */
[data-testid="stVerticalBlockBorderWrapper"]{{background:linear-gradient(160deg,rgba(227,167,62,.06),rgba(255,255,255,.01));
    border:1px solid rgba(227,167,62,.25) !important;border-radius:16px !important;
    box-shadow:0 14px 32px rgba(0,0,0,.45);padding:6px}}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="hero"><div class="eyebrow">LAVADORA S.A. · VISTA EJECUTIVA</div><h1>Dashboard Ejecutivo</h1><p>Qué está pasando actualmente en el negocio. Este panel describe la operación; las acciones viven en el Motor de Recomendaciones.</p></div>', unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=TEXT,
    title_font=dict(size=18, color=GOLD_LIGHT, family='Playfair Display'),
    xaxis=dict(gridcolor='rgba(255,255,255,.10)'), yaxis=dict(gridcolor='rgba(255,255,255,.10)'),
    legend=dict(font=dict(color=TEXT)), hoverlabel=dict(bgcolor=PANEL_SOLID, font_color=TEXT, bordercolor=BORDER))


def try_chart(render):
    """Ejecuta una sección de gráfico de forma aislada: si una tabla/columna no coincide
    con tu esquema real, esa tarjeta muestra un aviso en vez de tumbar todo el dashboard."""
    try:
        render()
    except Exception as exc:
        st.info("No se pudo cargar esta vista. Verifica los nombres de tabla/columna relacionados.")
        with st.expander("Detalle técnico"):
            st.exception(exc)


def layout_with(**overrides):
    """Combina PLOTLY_LAYOUT con overrides puntuales, fusionando xaxis/yaxis en vez de
    duplicarlos (pasar xaxis=... junto con **PLOTLY_LAYOUT, que ya trae xaxis, revienta
    con 'got multiple values for keyword argument' — por eso este helper)."""
    merged = dict(PLOTLY_LAYOUT)
    for key in ("xaxis", "yaxis"):
        if key in overrides:
            merged[key] = {**merged.get(key, {}), **overrides.pop(key)}
    merged.update(overrides)
    return merged


_kpi_id = [0]
def kpi_counter(icon, label, value, subtext, accent, decimals=0, prefix="", suffix="", delta=None):
    """Tarjeta KPI profesional: número que cuenta en vivo desde 0, con delta opcional (verde/rojo)."""
    _kpi_id[0] += 1
    uid = f"kpi{_kpi_id[0]}"
    if delta is not None:
        d_color = GREEN if delta >= 0 else RED
        d_arrow = "▲" if delta >= 0 else "▼"
        sub_html = f'<div class="kpi-delta" style="color:{d_color};">{d_arrow} {abs(delta):.1f}% vs. período anterior</div>'
    else:
        sub_html = f'<div class="kpi-sub">{subtext}</div>'
    html = f'''
    <style>
      html, body {{ margin:0; padding:0; background:transparent; font-family:'Inter',sans-serif; }}
      .kpi-card {{ background:{PANEL}; border:1px solid {BORDER}; border-radius:15px; padding:16px 16px 16px;
        box-shadow:0 8px 22px rgba(0,0,0,.35); border-top:3px solid {accent}; box-sizing:border-box; min-height:118px; }}
      .kpi-badge {{ width:34px; height:34px; border-radius:50%; display:flex; align-items:center;
        justify-content:center; font-size:1rem; margin-bottom:8px;
        background:radial-gradient(circle,{accent}55,{accent}22); }}
      .kpi-label {{ text-transform:uppercase; letter-spacing:.1em; font-weight:800; font-size:.68rem;
        margin-bottom:6px; color:{accent}; }}
      .kpi-value {{ font-size:1.55rem; font-weight:800; color:{TEXT}; font-variant-numeric:tabular-nums; }}
      .kpi-sub {{ color:{MUTED}; font-size:.72rem; margin-top:5px; line-height:1.3; }}
      .kpi-delta {{ font-size:.72rem; margin-top:5px; font-weight:700; line-height:1.3; white-space:nowrap; }}
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
      const start = performance.now(); const duration = 1400;
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

try:
    dates = query_df("SELECT MIN(fecha_venta)::date minimo, MAX(fecha_venta)::date maximo FROM venta").iloc[0]
    if pd.isna(dates.minimo): st.warning("No existen ventas disponibles."); st.stop()
    min_date, max_date = pd.Timestamp(dates.minimo), pd.Timestamp(dates.maximo)
    with st.sidebar:
        st.markdown("### Filtros del panel")
        period = st.selectbox("Período de análisis", ["Últimos 30 días", "Últimos 90 días", "Todo el historial"])
        top_n = st.slider("Productos y categorías", 5, 15, 8)
        st.caption(f"Datos disponibles: {min_date:%d/%m/%Y} a {max_date:%d/%m/%Y}")
    days = {"Últimos 30 días":30, "Últimos 90 días":90, "Todo el historial":None}[period]
    start = max_date - pd.Timedelta(days=days) if days else min_date
    params = {"start": start.date(), "end": max_date.date()}
    sales = query_df("""SELECT id_venta,cedula_cliente,fecha_venta::date fecha_venta,total FROM venta
                       WHERE fecha_venta::date BETWEEN :start AND :end AND total IS NOT NULL""", params)
    if sales.empty: st.warning("No hay ventas en el período seleccionado."); st.stop()
    sales["fecha_venta"] = pd.to_datetime(sales["fecha_venta"]); sales["total"] = pd.to_numeric(sales["total"], errors="coerce").fillna(0)
    inventory = query_df("SELECT p.nombre producto,i.stock_actual,i.punto_reorden,i.estado_stock FROM inventario i JOIN producto p ON p.id_producto=i.id_producto")
    if not inventory.empty:
        inventory["stock_actual"] = pd.to_numeric(inventory["stock_actual"], errors="coerce").fillna(0)
        inventory["punto_reorden"] = pd.to_numeric(inventory["punto_reorden"], errors="coerce")
        inventory["estado_stock"] = inventory["estado_stock"].astype(str).str.upper().str.strip()
        inventory["critico"] = inventory["estado_stock"].eq("SIN STOCK")
        # Un producto también necesita atención si tiene punto de reorden configurado
        # y el stock ya cayó a ese nivel o por debajo, aunque no esté en "SIN STOCK".
        inventory["bajo_reorden"] = inventory["punto_reorden"].notna() & (inventory["stock_actual"] <= inventory["punto_reorden"])
        inventory["necesita_atencion"] = inventory["critico"] | inventory["bajo_reorden"]
    else:
        inventory["critico"] = False
        inventory["necesita_atencion"] = False
    current_income = float(sales.total.sum()); total_sales = int(sales.id_venta.nunique()); clients = int(sales.cedula_cliente.nunique())
    freq = sales[sales.cedula_cliente != "9999999999999"].groupby("cedula_cliente").id_venta.nunique()
    recurrence = float((freq >= 2).mean() * 100) if len(freq) else 0
    critical = int(inventory.critico.sum()) if not inventory.empty else 0
    previous_start = start - pd.Timedelta(days=days) if days else None
    previous = query_df("""SELECT COALESCE(SUM(total),0) ingresos FROM venta WHERE fecha_venta::date BETWEEN :start AND :end AND total IS NOT NULL""", {"start": previous_start.date(), "end": (start-pd.Timedelta(days=1)).date()}) if previous_start else pd.DataFrame()
    previous_income = float(previous.iloc[0].ingresos) if not previous.empty else 0
    variation = ((current_income-previous_income)/previous_income*100) if previous_income else None
    st.caption(f"Período activo: {start:%d/%m/%Y} a {max_date:%d/%m/%Y}")
    k = st.columns(5)
    with k[0]: kpi_counter("💵", "Ingresos", current_income, "", GOLD_LIGHT, decimals=2, prefix="$", delta=variation)
    with k[1]: kpi_counter("🧾", "Ventas", total_sales, "Transacciones", STEEL_LIGHT)
    with k[2]: kpi_counter("👥", "Clientes", clients, "Atendidos en el período", "#3FA6A6")
    with k[3]: kpi_counter("🔄", "Recurrencia", recurrence, "Dos o más compras", GOLD, decimals=1, suffix="%")
    with k[4]: kpi_counter("⚠️", "Stock crítico", critical, f"de {len(inventory):,} productos", RED)
    if variation is None or abs(variation) < 5: headline="La actividad comercial se mantiene relativamente estable."
    elif variation > 0: headline="La actividad comercial muestra una tendencia favorable."
    else: headline="La actividad comercial presenta una señal de atención."
    monthly = sales.assign(mes=sales.fecha_venta.dt.to_period("M").dt.to_timestamp()).groupby("mes",as_index=False).agg(ingresos=("total","sum"),ventas=("id_venta","nunique"))
    # Rentabilidad real (no solo ingresos): producto.costo permite ver si el negocio
    # está ganando margen o simplemente moviendo volumen sin rentabilidad.
    margin_monthly = query_df("""SELECT date_trunc('month', v.fecha_venta)::date mes,
                SUM(dv.cantidad*COALESCE(p.precio,0)) ingresos,
                SUM(dv.cantidad*COALESCE(p.costo,0)) costo
            FROM detalle_venta dv JOIN venta v ON v.id_venta=dv.id_venta JOIN producto p ON p.id_producto=dv.id_producto
            WHERE v.fecha_venta::date BETWEEN :start AND :end GROUP BY 1 ORDER BY 1""", params)
    margin_monthly["mes"] = pd.to_datetime(margin_monthly["mes"])
    margin_monthly["margen"] = margin_monthly["ingresos"] - margin_monthly["costo"]
    margin_monthly["margen_pct"] = (margin_monthly["margen"] / margin_monthly["ingresos"] * 100).where(margin_monthly["ingresos"] > 0)
    avg_margin_pct = float(margin_monthly["margen_pct"].mean()) if not margin_monthly.empty and margin_monthly["margen_pct"].notna().any() else None
    margin_note = f" El margen bruto promedio del período es {avg_margin_pct:.1f}%." if avg_margin_pct is not None else ""
    st.markdown(f'<div class="insight"><small>LECTURA EJECUTIVA</small><strong>{headline}</strong><span>El inventario registra {critical:,} productos sin stock de un total de {len(inventory):,}. La recurrencia observada en el período es {recurrence:.1f}%.{margin_note}</span></div>', unsafe_allow_html=True)
    st.subheader("Desempeño comercial")
    cat = query_df("""SELECT COALESCE(c.nombre,'Sin categoría') categoria, SUM(dv.cantidad*COALESCE(p.precio,0)) ingresos
                      FROM detalle_venta dv JOIN venta v ON v.id_venta=dv.id_venta JOIN producto p ON p.id_producto=dv.id_producto
                      LEFT JOIN categoria c ON c.id_categoria=p.id_categoria WHERE v.fecha_venta::date BETWEEN :start AND :end
                      GROUP BY 1 ORDER BY 2 DESC LIMIT :limit""", {**params,"limit":top_n})
    a,b=st.columns([3,2])
    with a:
        def _render_margin():
            # Un solo eje (dinero): la barra dorada es ingresos, la azul es costo.
            # El margen no necesita un eje aparte — se escribe como etiqueta arriba
            # de cada mes, que es lo único que un ejecutivo necesita leer de un vistazo.
            fig = go.Figure()
            fig.add_trace(go.Bar(x=margin_monthly.mes, y=margin_monthly.ingresos, name="Ingresos",
                marker=dict(color=GOLD_LIGHT),
                hovertemplate="<b>%{x|%b %Y}</b><br>Ingresos: $%{y:,.2f}<extra></extra>"))
            fig.add_trace(go.Bar(x=margin_monthly.mes, y=margin_monthly.costo, name="Costo",
                marker=dict(color=STEEL),
                hovertemplate="<b>%{x|%b %Y}</b><br>Costo: $%{y:,.2f}<extra></extra>"))
            top_y = pd.concat([margin_monthly.ingresos, margin_monthly.costo]).max()
            for _, row in margin_monthly.iterrows():
                if pd.notna(row.margen_pct):
                    fig.add_annotation(x=row.mes, y=max(row.ingresos, row.costo) + top_y * 0.06,
                        text=f"<b>{row.margen_pct:.0f}%</b>", showarrow=False,
                        font=dict(color=TEAL, size=12), yanchor="bottom")
            fig.update_layout(
                barmode="group", height=370, title="Ingresos vs. costo por mes (el % arriba es el margen)",
                margin=dict(l=10, r=10, t=45, b=10),
                **layout_with(yaxis=dict(title="$", range=[0, top_y * 1.22]), xaxis=dict(title="")))
            fig.update_layout(legend=dict(font=dict(color=TEXT), orientation="h", y=-0.15))
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)

        try_chart(_render_margin)
    with b:
        def _render_categories():
            # Un pastel con porciones de menos del ~3% es ilegible (etiquetas encimadas,
            # colores que no se distinguen). Se agrupan las categorías chicas en "Otros"
            # para que el gráfico siempre muestre máximo 4 porciones + Otros, sin importar
            # cuántas categorías tenga el catálogo real.
            cat_sorted = cat.sort_values("ingresos", ascending=False).reset_index(drop=True)
            TOP_CATS = 4
            if len(cat_sorted) > TOP_CATS:
                otros_total = cat_sorted.iloc[TOP_CATS:]["ingresos"].sum()
                cat_pie = pd.concat([
                    cat_sorted.iloc[:TOP_CATS],
                    pd.DataFrame([{"categoria": "Otros", "ingresos": otros_total}]),
                ], ignore_index=True)
            else:
                cat_pie = cat_sorted
            pulls = [0.08 if i == cat_pie.ingresos.idxmax() else 0 for i in cat_pie.index]
            fig = go.Figure(go.Pie(labels=cat_pie.categoria, values=cat_pie.ingresos, hole=.62, pull=pulls,
                marker_colors=[GOLD_LIGHT, STEEL_LIGHT, TEAL, GOLD, STEEL],
                marker_line=dict(color=PANEL_SOLID, width=3),
                textinfo="percent", textfont=dict(size=13, color="#0A0B0F", family="Inter"),
                hovertemplate="<b>%{label}</b><br>$%{value:,.2f} (%{percent})<extra></extra>"))
            fig.add_annotation(text=f"<b>${cat.ingresos.sum():,.0f}</b><br><span style='font-size:11px;color:{MUTED}'>Total</span>",
                x=0.5, y=0.5, showarrow=False, font=dict(size=20, color=GOLD_LIGHT, family="Playfair Display"))
            fig.update_layout(height=370, margin=dict(l=10, r=10, t=45, b=10), title="Participación por categoría",
                showlegend=True, **PLOTLY_LAYOUT)
            fig.update_layout(legend=dict(font=dict(color=TEXT), orientation="h", y=-0.1))
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)
                top_cat = cat_sorted.iloc[0]
                share = top_cat.ingresos / cat_sorted.ingresos.sum() * 100 if cat_sorted.ingresos.sum() else 0
                st.caption(f"'{top_cat.categoria}' concentra el {share:.0f}% de los ingresos por categoría.")

        try_chart(_render_categories)
    st.subheader("Productos")
    top=query_df("""SELECT p.nombre producto,SUM(dv.cantidad) unidades,SUM(dv.cantidad*COALESCE(p.precio,0)) ingresos
                    FROM detalle_venta dv JOIN venta v ON v.id_venta=dv.id_venta JOIN producto p ON p.id_producto=dv.id_producto
                    WHERE v.fecha_venta::date BETWEEN :start AND :end GROUP BY 1 ORDER BY 3 DESC LIMIT :limit""",{**params,"limit":top_n})
    a,b=st.columns([3,2])
    with a:
        fig=px.bar(top.sort_values("ingresos"),x="ingresos",y="producto",orientation="h",text_auto=".2s",
            color="ingresos",color_continuous_scale=[(0,STEEL),(0.5,"#3FA6A6"),(1,GOLD_LIGHT)])
        fig.update_traces(marker_line_width=1,marker_line_color=PANEL_SOLID,
            hovertemplate="<b>%{y}</b><br>$%{x:,.2f}<extra></extra>")
        fig.update_layout(height=420,title=f"Top {top_n} productos por ingresos",margin=dict(l=10,r=10,t=50,b=10),
            coloraxis_showscale=False,**PLOTLY_LAYOUT)
        with st.container(border=True):
            st.plotly_chart(fig,use_container_width=True)
    with b:
        st.markdown("#### ⚠️ Productos que requieren atención")

        def _render_critical():
            critical_view = (inventory[inventory["necesita_atencion"]]
                              .sort_values(["critico", "stock_actual"], ascending=[False, True])
                              .head(10)
                              .copy())
            if critical_view.empty:
                st.success("No se detectaron productos por debajo del punto de reorden.")
                return

            # Lista tipo semáforo en vez de gráfico de barras: cuando la mayoría de
            # productos tiene 0 en stock, una barra de largo cero no comunica nada.
            # Aquí cada fila se lee sola, sin ejes ni escalas que interpretar.
            rows_html = ""
            for _, row in critical_view.iterrows():
                color = RED if row["critico"] else GOLD
                badge = "SIN STOCK" if row["critico"] else "STOCK BAJO"
                reorden = "no definido" if pd.isna(row["punto_reorden"]) else f"{row['punto_reorden']:.0f}"
                rows_html += f'''
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;
                    padding:11px 14px;border-bottom:1px solid {BORDER};">
                  <div style="display:flex;align-items:center;gap:10px;min-width:0;">
                    <span style="width:9px;height:9px;min-width:9px;border-radius:50%;background:{color};"></span>
                    <span style="color:{TEXT};font-size:.86rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{row['producto']}</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:12px;flex-shrink:0;">
                    <span style="color:{MUTED};font-size:.72rem;white-space:nowrap;">Stock: {int(row['stock_actual'])} · Reorden: {reorden}</span>
                    <span style="background:{color}22;color:{color};border:1px solid {color}66;border-radius:20px;
                        padding:2px 10px;font-size:.65rem;font-weight:800;letter-spacing:.03em;white-space:nowrap;">{badge}</span>
                  </div>
                </div>'''
            list_html = f'<div style="background:{PANEL_SOLID};border:1px solid {BORDER};border-radius:12px;overflow:hidden;">{rows_html}</div>'
            with st.container(border=True):
                st.markdown("**Productos que requieren atención (10 más urgentes)**")
                st.markdown(list_html, unsafe_allow_html=True)
                st.caption("🔴 Sin stock — reponer de inmediato.  🟡 Por debajo del punto de reorden — programar compra.")

        try_chart(_render_critical)
    with st.expander("Ver datos agregados del período"):
        st.dataframe(monthly,use_container_width=True,hide_index=True)

    # -----------------------------------------------------------------
    # Clientes más valiosos y rotación de inventario: dos preguntas que
    # las tarjetas anteriores no responden — quién sostiene el ingreso,
    # y qué capital está inmovilizado en productos que no se mueven.
    # -----------------------------------------------------------------
    st.subheader("Clientes y rotación de inventario")
    a, b = st.columns(2)

    with a:
        def _render_top_clients():
            top_clients = query_df("""SELECT c.nombre || ' ' || c.apellido cliente,
                        SUM(v.total) ingresos, COUNT(v.id_venta) compras
                    FROM venta v JOIN cliente c ON c.cedula = v.cedula_cliente
                    WHERE v.fecha_venta::date BETWEEN :start AND :end
                      AND v.cedula_cliente <> '9999999999999'
                    GROUP BY 1 ORDER BY 2 DESC LIMIT :limit""", {**params, "limit": top_n})
            if top_clients.empty:
                st.info("Sin clientes identificados en el período (¿ventas registradas como consumidor final?)."); return
            fig = px.bar(top_clients.sort_values("ingresos"), x="ingresos", y="cliente", orientation="h",
                text_auto=".2s", color="compras", color_continuous_scale=[(0, STEEL), (1, GOLD_LIGHT)])
            fig.update_traces(marker_line_width=1, marker_line_color=PANEL_SOLID,
                hovertemplate="<b>%{y}</b><br>Ingresos: $%{x:,.2f}<br>Compras: %{marker.color}<extra></extra>")
            fig.update_layout(height=400, title=f"Top {top_n} clientes por ingresos", margin=dict(l=10, r=10, t=45, b=10),
                coloraxis_colorbar=dict(title="Compras", tickfont=dict(color=TEXT)), **PLOTLY_LAYOUT)
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)
                st.caption("El color indica cuántas compras hizo cada cliente en el período: más oscuro = compra ocasional, dorado = cliente recurrente.")

        try_chart(_render_top_clients)

    with b:
        def _render_rotation():
            rot = query_df("""SELECT p.nombre producto, i.stock_actual,
                        COALESCE(SUM(dv.cantidad), 0) unidades_vendidas,
                        i.stock_actual * COALESCE(p.costo, 0) valor_inmovilizado
                    FROM inventario i
                    JOIN producto p ON p.id_producto = i.id_producto
                    LEFT JOIN detalle_venta dv ON dv.id_producto = p.id_producto
                    LEFT JOIN venta v ON v.id_venta = dv.id_venta AND v.fecha_venta::date BETWEEN :start AND :end
                    GROUP BY p.nombre, i.stock_actual, p.costo""", params)
            if rot.empty:
                st.info("Sin datos de inventario para calcular rotación."); return
            # En vez de un cuadrante con dos ejes y anotaciones a interpretar: una sola
            # barra con la pregunta directa que le importa al negocio — "¿en qué producto
            # tengo plata parada que no se está vendiendo?".
            dead = (rot[(rot.unidades_vendidas == 0) & (rot.stock_actual > 0)]
                    .sort_values("valor_inmovilizado", ascending=False).head(10))
            if dead.empty:
                st.success("Todos los productos con stock tuvieron al menos una venta en el período.")
                return
            fig = px.bar(dead.sort_values("valor_inmovilizado"), x="valor_inmovilizado", y="producto",
                orientation="h", text_auto=".2s", color_discrete_sequence=[RED])
            fig.update_traces(marker_line=dict(color=PANEL_SOLID, width=1),
                textposition="outside", textfont=dict(color=TEXT, size=11),
                hovertemplate="<b>%{y}</b><br>Capital inmovilizado: $%{x:,.2f}<extra></extra>")
            fig.update_layout(height=400, title="Productos sin ninguna venta en el período (capital parado)",
                margin=dict(l=10, r=30, t=45, b=10),
                **layout_with(yaxis=dict(title="", automargin=True), xaxis=dict(title="$ inmovilizado en stock")))
            with st.container(border=True):
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Son productos con stock disponible que no tuvieron ni una venta en el período. Cuanto más larga la barra, más dinero está parado ahí.")

        try_chart(_render_rotation)

    # -----------------------------------------------------------------
    # Ritmo del negocio: cuándo llegan realmente los clientes.
    # Se adapta sola al dato disponible: si fecha_venta trae hora real
    # (más de un valor distinto de hora en el período), arma el heatmap
    # día×hora, que es el gráfico más rico. Si todas las ventas quedaron
    # registradas a la misma hora (por ejemplo 00:00 al importar datos),
    # ese heatmap sale como bandas planas e ilegibles — así que en ese
    # caso cae de forma automática a un gráfico por día de la semana,
    # que siempre es legible y sigue respondiendo "qué días conviene
    # reforzar personal".
    # -----------------------------------------------------------------
    st.subheader("Ritmo del negocio")

    def _render_ritmo():
        raw = query_df(
            "SELECT fecha_venta FROM venta WHERE fecha_venta::date BETWEEN :start AND :end AND total IS NOT NULL",
            params,
        )
        raw["fecha_venta"] = pd.to_datetime(raw["fecha_venta"])
        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        raw["dia"] = raw.fecha_venta.dt.dayofweek.map(dict(enumerate(dias_es)))
        raw["hora"] = raw.fecha_venta.dt.hour
        hay_hora_real = raw["hora"].nunique() > 1

        if hay_hora_real:
            pivot = (raw.groupby(["dia", "hora"]).size().reset_index(name="ventas")
                        .pivot(index="dia", columns="hora", values="ventas")
                        .reindex(dias_es).fillna(0))
            fig = go.Figure(go.Heatmap(
                z=pivot.values, x=pivot.columns, y=pivot.index,
                colorscale=[(0, "#161821"), (0.5, STEEL), (1, GOLD_LIGHT)],
                hovertemplate="%{y}, %{x}:00h<br><b>%{z:.0f} ventas</b><extra></extra>",
                colorbar=dict(title="Ventas", tickfont=dict(color=TEXT))))
            fig.update_layout(height=340, title="Ventas por día y hora — dónde concentrar al equipo",
                margin=dict(l=10, r=10, t=50, b=10),
                **layout_with(xaxis=dict(title="Hora del día", dtick=1), yaxis=dict(title="")))
            caption = "Cada celda es el número de ventas en ese día y hora. Más clara = más movimiento; ahí conviene tener más personal en turno."
        else:
            agg = (raw.groupby("dia").size().reindex(dias_es).fillna(0).reset_index(name="ventas"))
            fig = px.bar(agg, x="dia", y="ventas", text_auto=True,
                color="ventas", color_continuous_scale=[(0, STEEL), (0.5, TEAL), (1, GOLD_LIGHT)])
            fig.update_traces(marker_line_width=1, marker_line_color=PANEL_SOLID,
                hovertemplate="<b>%{x}</b><br>Ventas: %{y}<extra></extra>")
            fig.update_layout(height=340, title="Ventas por día de la semana — dónde concentrar al equipo",
                margin=dict(l=10, r=10, t=50, b=10), coloraxis_showscale=False,
                **layout_with(xaxis=dict(title=""), yaxis=dict(title="Ventas")))
            dia_top = agg.loc[agg.ventas.idxmax(), "dia"] if agg.ventas.sum() else None
            caption = (f"'{dia_top}' es el día con más ventas del período — ese es el que más personal necesita."
                       if dia_top else "Aún no hay suficientes ventas para identificar un patrón por día.")

        with st.container(border=True):
            st.plotly_chart(fig, use_container_width=True)
            st.caption(caption)

    try_chart(_render_ritmo)

except Exception as error:
    st.error("No fue posible cargar el Dashboard. Verifica la conexión y las tablas de venta, detalle_venta, producto e inventario.")
    with st.expander("Detalle técnico"):
        st.exception(error)

# Pie de página (autoría), agregado automáticamente
show_footer()