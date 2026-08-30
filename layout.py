"""Layout maestro compartido por todas las páginas."""

import streamlit as st


def init_page(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} · LUBRIINSIGHT", page_icon=icon, layout="wide")


def render_hero(eyebrow: str, title: str, description: str) -> None:
    st.markdown(
        f"""<section class="hero"><p class="hero-eyebrow">{eyebrow}</p>
        <h1>{title}</h1><p>{description}</p></section>""",
        unsafe_allow_html=True,
    )


def render_page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(f"<h1 class='page-title'>{icon} {title}</h1><p class='page-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = "") -> None:
    st.markdown(f"<div class='section-heading'><h2>{title}</h2><p>{subtitle}</p></div>", unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown("<div class='app-footer'>LUBRIINSIGHT · Sistema Inteligente para Lavadora y Lubricadora de Vehículos</div>", unsafe_allow_html=True)
