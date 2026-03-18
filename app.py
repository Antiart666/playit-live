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

# Session State för blixtsnabb växling utan sidomladdning
if "selected_song" not in st.session_state:
    st.session_state.selected_song = None

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

# --- 2. CSS: SPEED & NO-KEYBOARD ---
st.markdown(f"""
    <style>
    /* Grundtema */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* FIXED HEADER */
    .header-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 140px;
        background: #ffffff;
        z-index: 999;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (MASSIV) */
    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 5px;
        height: 130px;
        z-index: 1000;
        transform: rotate(-6deg);
    }}

    /* START-KNAPP (TOP-RIGHT) */
    .stButton > button[kind="secondary"] {{
        position: fixed !important;
        top: 25px !important;
        right: 20px !important;
        background-color: #000 !important;
        color: #fff !important;
        border-radius: 50px !important;
        padding: 10px 20px !important;
        z-index: 1001 !important;
        border: none !important;
    }}

    /* CENTER MENU (POPOVER) */
    /* Vi använder Streamlits popover för att slippa input-fält helt */
    div[data-testid="stPopover"] {{
        position: fixed !important;
        top: 30px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 1001 !important;
        width: 35% !important;
    }}
    
    div[data-testid="stPopover"] > button {{
        width: 100% !important;
        border: 2px solid #000 !important;
        font-weight: 800 !important;
        color: #000 !important;
        background: #fff !important;
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
    
    /* Göm alla input-fält som Streamlit kan tänkas skapa i bakgrunden */
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDER UI ---

# Header & Logo
logo_b64 = get_logo_b64()
st.markdown('<div class="header-bar"></div>', unsafe_allow_html=True)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:35px; z-index:1000;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp (Reset)
if st.button("START", kind="secondary"):
    st.session_state.selected_song = None
    st.rerun()

# DEN NYA MENYN (Popover = Inget tangentbord)
song_map = get_songs()
current_label = format_name(st.session_state.selected_song).upper() if st.session_state.selected_song else "VÄLJ LÅT..."

with st.popover(current_label):
    st.markdown("### Välj låt")
    for snyggt_namn, filnamn in song_map.items():
        # När du klickar här laddas låten omedelbart utan full sidomladdning
        if st.button(snyggt_namn.upper(), key=filnamn, use_container_width=True):
            st.session_state.selected_song = filnamn
            st.rerun()

# --- 4. DISPLAY CONTENT ---
if st.session_state.selected_song:
    path = LIB_DIR / f"{st.session_state.selected_song}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)

# Scroll-fix
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
