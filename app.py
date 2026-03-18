import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CORE SETUP ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Bibliotek och Logga
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

# --- 2. THE STAGE-READY UI (TOTAL LOCKDOWN) ---
st.markdown(f"""
    <style>
    /* Bakgrund & Clean UI */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* FIXED HEADER */
    .header-anchor {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 160px;
        background: #ffffff;
        z-index: 999990;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (MASSIV) */
    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 5px;
        height: 160px; /* Ännu lite större */
        width: auto;
        transform: rotate(-6deg);
        z-index: 1000005 !important;
    }}

    /* HTML NATIVE SELECT (Tangbordssäkert på riktigt) */
    .native-nav-container {{
        position: fixed;
        top: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 30%;
        z-index: 1000010;
    }}

    .pure-select {{
        width: 100%;
        height: 50px;
        background: #ffffff;
        border: 2px solid #000;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 700;
        padding: 0 10px;
        appearance: none;
        -webkit-appearance: none;
        cursor: pointer;
        outline: none;
        text-align: center;
    }}

    /* START-KNAPP (Pillerformad) */
    .start-anchor {{
        position: fixed;
        top: 30px;
        right: 20px;
        background: #000000;
        color: #ffffff !important;
        padding: 12px 30px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 16px;
        text-decoration: none !important;
        z-index: 1000010 !important;
        text-transform: uppercase;
    }}

    /* SONG DISPLAY */
    .song-area {{
        margin-top: 180px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 85vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
song_map = get_songs()
# Hämta vald låt från URL-parameter (robustaste sättet för HTML-select)
query_params = st.query_params
active_song_file = query_params.get("song", None)

# --- 4. RENDER UI ---

# Header & Logo
logo_b64 = get_logo_b64()
st.markdown('<div class="header-anchor"></div>', unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:45px; z-index:1000005;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp
st.markdown('<a href="/" target="_self" class="start-anchor">START</a>', unsafe_allow_html=True)

# BYGG DEN "TANGENTBORDSSÄKRA" RULLISTEN
# Vi bygger den i ren HTML för att slippa Streamlits <input>-taggar
options_html = '<option value="">VÄLJ LÅT...</option>'
for snyggt_namn, filnamn in song_map.items():
    selected = 'selected' if active_song_file == filnamn else ''
    options_html += f'<option value="{filnamn}" {selected}>{snyggt_namn.upper()}</option>'

st.markdown(f"""
    <div class="native-nav-container">
        <select class="pure-select" onchange="window.location.href='?song=' + encodeURIComponent(this.value)">
            {options_html}
        </select>
    </div>
""", unsafe_allow_html=True)

# --- 5. DISPLAY CONTENT ---
if active_song_file and active_song_file in [f.stem for f in LIB_DIR.glob("*.md")]:
    path = LIB_DIR / f"{active_song_file}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)
else:
    st.empty()

# Scroll till toppen vid omladdning
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
