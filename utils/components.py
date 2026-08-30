"""Componentes visuales reutilizables."""

import streamlit as st


def metric_card(icon: str, label: str, value: str, detail: str) -> None:
    st.markdown(
        f"""<div class="metric-card"><div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div><div class="metric-value">{value}</div>
        <div class="metric-detail">{detail}</div></div>""",
        unsafe_allow_html=True,
    )


def status_badge(label: str, state: str) -> None:
    st.markdown(f"<span class='status status-{state}'>● {label}</span>", unsafe_allow_html=True)
