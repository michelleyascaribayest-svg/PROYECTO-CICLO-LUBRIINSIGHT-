"""Pie de página en la barra lateral, compartido por todos los módulos de LubriInsight.
Edita este archivo una sola vez y el cambio se refleja en todas las páginas."""
import streamlit as st

_BORDER = "rgba(255,255,255,0.10)"
_MUTED = "#A6B2C0"

# Cambia aquí la fecha y los autores cuando haga falta
_ULTIMA_ACTUALIZACION = "02/09/2026"
_AUTORES = "Celia Ayavaca · Viviana Guambaña · Michelle Yascaribay"


def show_footer() -> None:
    """Escribe una línea de texto discreta al final de la barra lateral (dentro del flujo normal,
    no flotante, para que nunca tape contenido de la página ni del propio sidebar)."""
    with st.sidebar:
        st.markdown(
            f"""<div style='margin-top:28px;padding-top:12px;border-top:1px solid {_BORDER};
                font-size:.66rem;color:{_MUTED};text-align:center;line-height:1.7'>
                Última actualización de la web: {_ULTIMA_ACTUALIZACION}<br>
                Autores: {_AUTORES}
            </div>""",
            unsafe_allow_html=True,
        )