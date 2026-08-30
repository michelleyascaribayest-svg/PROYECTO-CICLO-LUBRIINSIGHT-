"""Pie de página en la barra lateral, compartido por todos los módulos de LubriInsight.
Edita este archivo una sola vez y el cambio se refleja en todas las páginas."""
import streamlit as st

_BORDER = "rgba(255,255,255,0.10)"
_MUTED = "#A6B2C0"
_GOLD_LIGHT = "#F5CF7A"
_TEXT = "#F3F5F8"

# Cambia aquí la fecha y los autores cuando haga falta
_ULTIMA_ACTUALIZACION = "02/09/2026"
_AUTORES = ["Celia Ayavaca", "Viviana Guambaña", "Michelle Yascaribay"]

# Atribución de la fuente de datos original
_FUENTE_DATOS = (
    'Base de datos de referencia: <b style="color:{text}">Lavadora y Lubricadora "S.A."</b>, '
    'propiedad de <b style="color:{text}">Santiago Angamarca</b>. '
    "Estructura y contenido adaptados por las autoras con fines académicos."
)


def show_footer() -> None:
    """Escribe el pie de página al final de la barra lateral (dentro del flujo normal, sin caja),
    con tipografía cuidada: labels pequeños en dorado + nombres en itálica (Playfair Display)."""
    nombres_html = "<br>".join(_AUTORES)
    fuente_html = _FUENTE_DATOS.format(text=_TEXT)
    with st.sidebar:
        st.markdown(
            f"""
            <style>
            [data-testid="stVerticalBlockBorderWrapper"]:has(#li-footer-anchor) {{
                border: none !important;
                background: transparent !important;
                box-shadow: none !important;
                animation: none !important;
                padding: 0 !important;
            }}
            </style>
            <div id="li-footer-anchor" style='margin-top:30px;padding:14px 8px 6px;
                border-top:1px solid {_BORDER};text-align:center;font-family:"Inter",sans-serif'>
                <div style='font-size:.60rem;font-weight:800;letter-spacing:.12em;
                    text-transform:uppercase;color:{_GOLD_LIGHT};margin-bottom:4px'>
                    Última actualización
                </div>
                <div style='font-size:.74rem;color:{_TEXT};font-weight:600;margin-bottom:12px'>
                    {_ULTIMA_ACTUALIZACION}
                </div>
                <div style='font-size:.60rem;font-weight:800;letter-spacing:.12em;
                    text-transform:uppercase;color:{_GOLD_LIGHT};margin-bottom:5px'>
                    Autoras
                </div>
                <div style='font-family:"Playfair Display",serif;font-style:italic;
                    font-size:.78rem;color:{_MUTED};line-height:1.6;margin-bottom:12px'>
                    {nombres_html}
                </div>
                <div style='font-size:.60rem;font-weight:800;letter-spacing:.12em;
                    text-transform:uppercase;color:{_GOLD_LIGHT};margin-bottom:5px'>
                    Fuente de datos
                </div>
                <div style='font-family:"Inter",sans-serif;font-size:.66rem;
                    color:{_MUTED};line-height:1.55;padding:0 6px'>
                    {fuente_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )