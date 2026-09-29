"""Front-end layer for StudyBot: themes, CSS loading and HTML components.

All styling lives in static/style.css. This module only supplies the theme
colors (as CSS variables) and small HTML snippets, so app.py stays logic-only.
"""
from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).parent / "static" / "style.css"

THEMES = {
    "Dark Mode": {
        "app_bg": "#0B1220",
        "sidebar_bg": "#0A1122",
        "card_bg": "#16223B",
        "card_border": "#263556",
        "text_main": "#F1F5F9",
        "text_sub": "#9FB0D0",
        "input_bg": "#1C2A4D",
        "input_border": "#33466F",
        "input_text": "#FFFFFF",
        "popover_bg": "#1C2A4D",
        "popover_hover": "#2A3B66",
        "chart_text": "#F1F5F9",
        "grid": "#263556",
        "plotly_template": "plotly_dark",
        "chart_colors": ["#3B6CF2", "#0EA5A4", "#8B5CF6", "#F59E0B", "#EC6A8E"],
    },
    "Light Mode": {
        "app_bg": "#F4F6FB",
        "sidebar_bg": "#111C36",
        "card_bg": "#FFFFFF",
        "card_border": "#E2E8F0",
        "text_main": "#0F172A",
        "text_sub": "#5B6778",
        "input_bg": "#FFFFFF",
        "input_border": "#CBD5E1",
        "input_text": "#0F172A",
        "popover_bg": "#FFFFFF",
        "popover_hover": "#EEF2FF",
        "chart_text": "#0F172A",
        "grid": "#E2E8F0",
        "plotly_template": "plotly_white",
        "chart_colors": ["#3B6CF2", "#0EA5A4", "#8B5CF6", "#F59E0B", "#EC6A8E"],
    },
}


def get_theme(name):
    return THEMES.get(name, THEMES["Light Mode"])


def _compact(text):
    """Remove blank lines / indentation so Markdown never treats HTML as a code block."""
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def inject_css(t):
    """Load static/style.css and inject the active theme as CSS variables."""
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        st.warning(f"Stylesheet not found: {CSS_PATH}")
        css = ""

    variables = (
        ":root{"
        f"--app-bg:{t['app_bg']};--sidebar-bg:{t['sidebar_bg']};"
        f"--card-bg:{t['card_bg']};--card-border:{t['card_border']};"
        f"--text-main:{t['text_main']};--text-sub:{t['text_sub']};"
        f"--input-bg:{t['input_bg']};--input-border:{t['input_border']};"
        f"--input-text:{t['input_text']};"
        f"--popover-bg:{t['popover_bg']};--popover-hover:{t['popover_hover']};"
        "}"
    )
    # @import must come first, so the stylesheet goes before the variables
    st.markdown(f"<style>{_compact(css)}\n{variables}</style>", unsafe_allow_html=True)


def render_header():
    st.markdown(
        _compact(
            """
            <div class="executive-header">
                <div>
                    <div class="title">StudyBot AI & Review Analytics</div>
                    <div class="subtitle">Enterprise Executive Dashboard • Student Feedback & Course Performance Intelligence</div>
                </div>
                <div class="badge">ENTERPRISE EDITION</div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_kpis(total_reviews, avg_rating_val, low_ratings_count):
    low_color = "#E5484D" if low_ratings_count > 0 else "#3B6CF2"
    low_text = "#C62828" if low_ratings_count > 0 else "var(--text-main)"
    st.markdown(
        _compact(
            f"""
            <div class="kpi-container">
                <div class="kpi-card" style="border-left-color: #3B6CF2;">
                    <div class="kpi-label">Total Filtered Reviews</div>
                    <div class="kpi-value">{total_reviews}</div>
                </div>
                <div class="kpi-card" style="border-left-color: #0EA5A4;">
                    <div class="kpi-label">Average View Rating</div>
                    <div class="kpi-value">{avg_rating_val} <span class="kpi-unit">/ 5.0</span></div>
                </div>
                <div class="kpi-card" style="border-left-color: {low_color};">
                    <div class="kpi-label">Critical Complaints (1-2★)</div>
                    <div class="kpi-value" style="color: {low_text};">{low_ratings_count}</div>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def render_comment_card(subj, cat, rat, cmnt):
    """Feedback card: green = good, amber = medium, red = complaint."""
    try:
        rat_num = float(rat)
    except (TypeError, ValueError):
        rat_num = None

    if rat_num is None:
        border, pill_bg, pill_text = "#3B6CF2", "#E0E9FF", "#1E3A8A"
    elif rat_num <= 2:
        border, pill_bg, pill_text = "#E5484D", "#FEE2E2", "#991B1B"
    elif rat_num < 4:
        border, pill_bg, pill_text = "#F59E0B", "#FEF3C7", "#92400E"
    else:
        border, pill_bg, pill_text = "#16A34A", "#DCFCE7", "#166534"

    st.markdown(
        _compact(
            f"""
            <div class="comment-card-pro" style="border-left: 5px solid {border};">
                <div class="comment-tags">
                    <span class="tag tag-subject">{subj}</span>
                    <span class="tag tag-category">{cat}</span>
                    <span class="tag" style="background:{pill_bg}; color:{pill_text}; font-weight:700;">★ {rat}/5</span>
                </div>
                <p class="comment-text">"{cmnt}"</p>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )