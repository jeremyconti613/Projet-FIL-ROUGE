# ui_theme.py
# Module partagé de présentation pour le thème "The Binding of Isaac".
# Importé par toutes les pages Streamlit.

import streamlit as st
import pandas as pd
from pathlib import Path

# ── Noms d'étages Isaac ────────────────────────────────────────────────────────
# Étages principaux (Isaac/Afterbirth/Repentance), par numéro d'étage (1-based).
# Chaque "monde" dure 2 niveaux (ex. Basement I + Basement II = étages 1 et 2).
FLOOR_NAMES = {
    1:  "Basement I",
    2:  "Basement II",
    3:  "Caves I",
    4:  "Caves II",
    5:  "Depths I",
    6:  "Depths II",
    7:  "Womb I",
    8:  "Womb II",
    9:  "Sheol / Cathedral",
    10: "Dark Room / Chest",
    11: "The Void",
    12: "Home",
    13: "???",
}

# Icône Unicode ou emoji par "monde"
FLOOR_ICONS = {
    1: "🪨", 2: "🪨",
    3: "🕳️", 4: "🕳️",
    5: "💀", 6: "💀",
    7: "🫀", 8: "🫀",
    9: "😈",
    10: "🚪",
    11: "🌀",
    12: "🏠",
    13: "❓",
}

MAX_FLOOR = 13


def floor_name(n: int) -> str:
    """Retourne le nom de l'étage n (1-based). Fallback sur 'Étage N'."""
    return FLOOR_NAMES.get(n, f"Étage {n}")


def floor_icon(n: int) -> str:
    return FLOOR_ICONS.get(n, "🔒")


# ── Chargement des données ────────────────────────────────────────────────────

@st.cache_data
def load_scores() -> pd.DataFrame | None:
    """Charge data/run_scores.csv avec cache Streamlit. Retourne None si absent."""
    path = Path("data/run_scores.csv")
    if not path.exists():
        return None
    return pd.read_csv(path)


# ── Thème / CSS ───────────────────────────────────────────────────────────────

_ISAAC_CSS = """
<style>
/* ── Import police pixel ── */
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Press+Start+2P&display=swap');

/* ── Corps global ── */
html, body, [data-testid="stApp"] {
    background-color: #141010;
    color: #e8dcc8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #1c1414 !important;
    border-right: 2px solid #b51919;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #e8dcc8 !important;
}

/* ── Titres ── */
h1 {
    font-family: 'VT323', monospace !important;
    font-size: 3rem !important;
    color: #b51919 !important;
    text-shadow: 2px 2px 0px #5c0a0a, 0 0 20px #b5191966 !important;
    letter-spacing: 2px;
    margin-bottom: 0.2rem;
}
h2 {
    font-family: 'VT323', monospace !important;
    font-size: 2rem !important;
    color: #c9362e !important;
    text-shadow: 1px 1px 0px #5c0a0a;
    border-bottom: 1px solid #b5191944;
    padding-bottom: 4px;
}
h3 {
    font-family: 'VT323', monospace !important;
    font-size: 1.5rem !important;
    color: #d97b52 !important;
}

/* ── Métriques ── */
[data-testid="stMetric"] {
    background: #241a17;
    border: 1px solid #b5191955;
    border-left: 3px solid #b51919;
    border-radius: 4px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] {
    color: #a08c7a !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #e8dcc8 !important;
    font-size: 1.8rem !important;
    font-family: 'VT323', monospace !important;
}
[data-testid="stMetricDelta"] {
    color: #b51919 !important;
}

/* ── Boutons ── */
.stButton > button {
    background: linear-gradient(180deg, #8c1a1a 0%, #5c0a0a 100%) !important;
    color: #e8dcc8 !important;
    border: 2px solid #b51919 !important;
    border-bottom: 3px solid #3a0505 !important;
    border-radius: 2px !important;
    font-family: 'VT323', monospace !important;
    font-size: 1.1rem !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 6px 24px !important;
    transition: all 0.1s;
}
.stButton > button:hover {
    background: linear-gradient(180deg, #b51919 0%, #8c1a1a 100%) !important;
    box-shadow: 0 0 12px #b5191988 !important;
    transform: translateY(-1px);
}
.stButton > button:active {
    transform: translateY(1px);
    border-bottom: 1px solid #3a0505 !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    color: #a08c7a !important;
    font-family: 'VT323', monospace !important;
    font-size: 1.1rem !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #b51919 !important;
    border-bottom: 2px solid #b51919 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] {
    border: 1px solid #b5191933;
}

/* ── Info / Warning / Success ── */
[data-testid="stAlert"] {
    border-left: 4px solid #b51919;
    background: #241a17;
}

/* ── Barre de progression ── */
[data-testid="stProgress"] > div > div {
    background: #b51919 !important;
}

/* ── Séparateur ── */
hr {
    border-color: #b5191944 !important;
    margin: 1rem 0;
}

/* ── Selectbox / number_input ── */
[data-testid="stNumberInput"] input,
[data-baseweb="select"] {
    background: #241a17 !important;
    border-color: #b5191977 !important;
    color: #e8dcc8 !important;
}

/* ── Carte décorative (classe custom .isaac-card) ── */
.isaac-card {
    background: #1c1414;
    border: 1px solid #b5191955;
    border-top: 2px solid #b51919;
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 12px;
}

/* ── Badge étage ── */
.floor-badge {
    display: inline-block;
    background: #b51919;
    color: #e8dcc8;
    font-family: 'VT323', monospace;
    font-size: 1.2rem;
    padding: 2px 12px;
    border-radius: 2px;
    margin: 0 4px;
}

/* ── Classe placeholder warning ── */
.placeholder-banner {
    background: #2a1a0a;
    border: 1px solid #c17c2a;
    border-left: 4px solid #c17c2a;
    border-radius: 4px;
    padding: 10px 16px;
    color: #d4a96a;
    font-size: 0.9rem;
    margin-bottom: 16px;
}
</style>
"""


def apply_isaac_theme() -> None:
    """
    Injecte le CSS du thème Binding of Isaac dans la page courante.
    À appeler **après** st.set_page_config(), en haut de chaque page.
    """
    st.markdown(_ISAAC_CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str = "") -> None:
    """
    Affiche un bandeau d'accueil thématisé avec le logo et un titre pixel.
    À utiliser uniquement sur la page d'accueil.
    """
    logo_path = Path("assets/images/logo.png")
    col_logo, col_text = st.columns([1, 3])
    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
    with col_text:
        st.markdown(f"# {title}")
        if subtitle:
            st.markdown(f"<p style='color:#a08c7a; font-size:1.1rem'>{subtitle}</p>",
                        unsafe_allow_html=True)
    st.markdown("---")


def section(title: str, icon: str = "🩸") -> None:
    """En-tête de section stylé (remplace st.markdown('---') + emoji)."""
    st.markdown(f"## {icon} {title}")
