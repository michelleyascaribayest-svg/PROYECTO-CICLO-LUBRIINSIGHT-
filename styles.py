"""Identidad visual centralizada de INSIGHT LUB."""
# --- Agregar en styles.py (junto a COLORS, debajo de él) ---

import base64
from pathlib import Path

SIDEBAR_ICON_PATH = "assets/diagramas/logo.png"


@st.cache_data(show_spinner=False)
def _sidebar_icon_b64() -> str | None:
    try:
        return base64.b64encode(Path(SIDEBAR_ICON_PATH).read_bytes()).decode()
    except FileNotFoundError:
        return None


def apply_sidebar_nav_style() -> None:
    """CSS del menú lateral (fuente Playfair, ícono, estados) — llamar en TODAS las páginas."""
    icon_b64 = _sidebar_icon_b64() or ""
    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');

          [data-testid="stSidebar"] {{ background:#07080B; border-right:1px solid rgba(255,255,255,.08); }}
          [data-testid="stSidebar"] * {{ color:#EDEFF2 !important; }}

          [data-testid="stSidebarNav"] {{ padding-top:95px !important; position:relative; }}
          [data-testid="stSidebarNav"]::before {{
              content:""; position:absolute; top:14px; left:0; right:0; height:64px;
              background-image:url(data:image/png;base64,{icon_b64});
              background-repeat:no-repeat; background-position:top center; background-size:contain;
          }}

          [data-testid="stSidebarNav"] a {{
              border-radius:10px; margin:2px 8px; padding:10px 12px !important;
              transition:background .15s ease;
          }}
          [data-testid="stSidebarNav"] span {{
              font-family:'Playfair Display',serif; font-weight:600;
              font-size:.95rem; letter-spacing:.01em; white-space:normal !important;
          }}
          [data-testid="stSidebarNav"] a:hover {{ background:rgba(227,167,62,.14) !important; }}
          [data-testid="stSidebarNav"] a[aria-current="page"] {{
              background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
              border-left:3px solid #F5CF7A;
          }}
          [data-testid="stSidebarNav"] a[aria-current="page"] span {{ color:#F5CF7A !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
import streamlit as st

COLORS = {
    "navy": "#0B2D4D",
    "blue": "#0F4C81",
    "sky": "#2E86C1",
    "gold": "#D4A017",
    "green": "#1FA971",
    "red": "#D9544D",
    "ink": "#17212B",
    "muted": "#627180",
    "surface": "#FFFFFF",
    "background": "#F4F7FA",
    "border": "#E2E8F0",
}
# --- Agregar en styles.py (junto a COLORS, debajo de él) ---

import base64
from pathlib import Path

SIDEBAR_ICON_PATH = "assets/diagramas/logo.png"


@st.cache_data(show_spinner=False)
def _sidebar_icon_b64() -> str | None:
    try:
        return base64.b64encode(Path(SIDEBAR_ICON_PATH).read_bytes()).decode()
    except FileNotFoundError:
        return None


def apply_sidebar_nav_style() -> None:
    """CSS del menú lateral (fuente Playfair, ícono, estados) — llamar en TODAS las páginas."""
    icon_b64 = _sidebar_icon_b64() or ""
    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');

          [data-testid="stSidebar"] {{ background:#07080B; border-right:1px solid rgba(255,255,255,.08); }}
          [data-testid="stSidebar"] * {{ color:#EDEFF2 !important; }}

          [data-testid="stSidebarNav"] {{ padding-top:95px !important; position:relative; }}
          [data-testid="stSidebarNav"]::before {{
              content:""; position:absolute; top:14px; left:0; right:0; height:64px;
              background-image:url(data:image/png;base64,{icon_b64});
              background-repeat:no-repeat; background-position:top center; background-size:contain;
          }}

          [data-testid="stSidebarNav"] a {{
              border-radius:10px; margin:2px 8px; padding:10px 12px !important;
              transition:background .15s ease;
          }}
          [data-testid="stSidebarNav"] span {{
              font-family:'Playfair Display',serif; font-weight:600;
              font-size:.95rem; letter-spacing:.01em; white-space:normal !important;
          }}
          [data-testid="stSidebarNav"] a:hover {{ background:rgba(227,167,62,.14) !important; }}
          [data-testid="stSidebarNav"] a[aria-current="page"] {{
              background:linear-gradient(135deg,rgba(227,167,62,.22),rgba(79,143,196,.14)) !important;
              border-left:3px solid #F5CF7A;
          }}
          [data-testid="stSidebarNav"] a[aria-current="page"] span {{ color:#F5CF7A !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

