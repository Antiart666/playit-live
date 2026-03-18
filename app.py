import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CONFIG & SETUP ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# State för att hålla koll på vald låt
if "active_song" not in st.session_state:
    st.session_state.active_song = "VÄLJ LÅT..."

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_name(n):
    return n.replace('_', ' ').strip().title()

def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md")])
    return {format_name(f): f for f in files}

def get_logo_b64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. CSS: ABSOLUTE POSITIONING & NO-KEYBOARD ---
st.markdown(f"""
    <style>
    /* Grundinställningar */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* FIXED HEADER CONTAINER */
    .header-anchor {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: #ffffff;
        z-index: 999990;
        border-bottom: 1px solid #f0f0f0;
    }}

    /* LOGO (MASSIV + 20% till) */
    .stage-logo {{
        position: fixed;
        left: 10px;
        top: 5px;
        height: 140px; /* Rejäl storlek */
        width: auto;
        transform: rotate(-7deg);
        z-index: 1000005 !important;
    }}
    
    .logo-fallback {{
        position: fixed;
        left: 10px;
        top: 20px;
        font-weight: 900;
        font-size: 40px;
        border: 5px solid #000;
        padding: 10px;
        z-index: 1000005;
        background: white;
    }}

    /* RULLIST (35% & TOP) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 10px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 35% !important;
        z-index: 1000010 !important;
    }}

    /* TANGENTBORDS-SPÄRR */
    div[data-baseweb="select"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* EXIT-KNAPP (HTML-LÄNK ISTÄLLET FÖR ST-BUTTON) */
    .exit-anchor {{
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f0f0f0;
        color: #000 !important;
        padding: 10px 15px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 14px;
        text-decoration: none !important;
        border: 1px solid #ddd;
        z-index: 1000010 !important;
        text-transform: uppercase;
    }}

    /* SONG DISPLAY */
    .song-area {{
        margin-top: 160px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

# Rita den fasta bakgrunden och loggan
logo_b64 = get_logo_b64()
st.markdown('<div class="header-anchor"></div>', unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div class="logo-fallback">PLAYIT</div>', unsafe_allow_html=True)

# Rita EXIT-knappen som en ren HTML-länk (tvingar omladdning till startsidan)
st.markdown('<a href="/" target="_self" class="exit-anchor">EXIT</a>', unsafe_allow_html=True)

# Ladda låtarna
song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

# Rullistan
selected = st.selectbox(
    "Välj låt",
    options=options,
    index=options.index(st.session_state.active_song) if st.session_state.active_song in options else 0,
    label_visibility="collapsed"
)

# Vid val av låt
if selected != st.session_state.active_song:
    st.session_state.active_song = selected
    st.rerun()

# --- 4. DISPLAY CONTENT ---
if st.session_state.active_song != "VÄLJ LÅT...":
    file_name = song_map[st.session_state.active_song]
    path = LIB_DIR / f"{file_name}.md"
    
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)
else:
    st.empty()

# Scroll till toppen
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
