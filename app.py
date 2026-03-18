import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Session State för stabil laddning
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

# --- 2. CSS & AGGRESSIVE KEYBOARD KILLER ---
st.markdown(f"""
    <style>
    /* Scen-inställningar */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* HEADER BAKGRUND */
    .header-anchor {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 140px;
        background: #ffffff;
        z-index: 999990;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (MASSIV) */
    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 5px;
        height: 130px;
        width: auto;
        transform: rotate(-6deg);
        z-index: 1000005 !important;
    }}

    /* RULLIST (35% BREDD + CENTER) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 35% !important;
        z-index: 1000010 !important;
    }}

    /* DÖDA TANGENTBORDET (CSS) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
    }}

    /* START-KNAPP (TOP-RIGHT) */
    .stButton > button {{
        position: fixed !important;
        top: 25px !important;
        right: 20px !important;
        background-color: #000000 !important;
        color: #ffffff !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 25px !important;
        font-weight: 900 !important;
        z-index: 1000015 !important;
        text-transform: uppercase;
    }}

    /* SONG DISPLAY */
    .song-area {{
        margin-top: 150px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    </style>

    <script>
    // NUCLEAR OPTION FÖR TANGENTBORD: 
    // Hindrar alla input-fält från att någonsin bli editerbara
    function disableKeyboard() {{
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {{
            input.setAttribute('readonly', 'true');
            input.setAttribute('inputmode', 'none'); // Talar om för mobilen: "Visa inget tangentbord"
            if (window.parent.document.activeElement === input) {{
                input.blur();
            }}
        }});
    }}
    setInterval(disableKeyboard, 100);
    </script>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

# Header & Logo
logo_b64 = get_logo_b64()
st.markdown('<div class="header-anchor"></div>', unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:40px; z-index:1000005;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp (Reset)
if st.button("START"):
    st.session_state.active_song = "VÄLJ LÅT..."
    st.rerun()

# Låtlista & Rullist
song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

# Hitta rätt index för att hålla kvar valet efter rerun
try:
    current_idx = options.index(st.session_state.active_song)
except ValueError:
    current_idx = 0

selected = st.selectbox(
    "Välj låt",
    options=options,
    index=current_idx,
    label_visibility="collapsed",
    key="song_picker"
)

# Vid val - uppdatera state och ladda om
if selected != st.session_state.active_song:
    st.session_state.active_song = selected
    st.rerun()

# --- 4. DISPLAY ---
if st.session_state.active_song != "VÄLJ LÅT...":
    file_name = song_map[st.session_state.active_song]
    path = LIB_DIR / f"{file_name}.md"
    
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}\n\n' + ('\n' * 60) + '</div>', unsafe_allow_html=True)

# Scroll-fix till toppen
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
