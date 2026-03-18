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

if "current_song" not in st.session_state:
    st.session_state.current_song = "VÄLJ LÅT..."

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

# --- 2. CSS: FIXED UI & ANTI-KEYBOARD ---
st.markdown(f"""
    <style>
    /* Bakgrund & Grund */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}

    /* Dölj Streamlit-menyer */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* FIXED NAVBAR */
    .nav-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 130px;
        background: #ffffff;
        border-bottom: 1px solid #eeeeee;
        z-index: 999990;
    }}

    /* LOGO (+20% STÖRRE) */
    .logo-box {{
        position: fixed;
        left: 15px;
        top: 10px;
        transform: rotate(-8deg);
        z-index: 999999;
    }}
    .logo-img {{ height: 110px; width: auto; }} /* Ökad från 80px/90px */
    .logo-fallback {{ 
        font-weight: 900; font-size: 32px; border: 4px solid #000; 
        padding: 8px 15px; border-radius: 12px; background: #fff;
    }}

    /* RULLIST (35% BREDD + TOP-ALIGNED) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 35% !important;
        z-index: 1000001 !important;
    }}

    /* TANGENTBORDS-DÖDARE (Shield Layer) */
    /* Vi blockerar alla pek-händelser på det inre textfältet */
    div[data-baseweb="select"] input {{
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
    }}
    
    /* EXIT-KNAPP (TOP-RIGHT) */
    .stButton > button {{
        position: fixed !important;
        top: 15px !important;
        right: 15px !important;
        background-color: #f8f8f8 !important;
        color: #000000 !important;
        border-radius: 15px !important;
        border: 1px solid #ddd !important;
        padding: 8px 18px !important;
        font-weight: 800 !important;
        z-index: 1000005 !important;
    }}

    /* SONG DISPLAY (DIN SPEC) */
    .song-display {{
        margin-top: 150px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        color: #000000 !important;
        padding-bottom: 80vh;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDER UI ---

# Rita Header/Logo
logo_b64 = get_logo_b64()
if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">'
else:
    logo_html = '<div class="logo-fallback">PLAYIT</div>'

st.markdown(f'<div class="nav-bar"><div class="logo-box">{logo_html}</div></div>', unsafe_allow_html=True)

# Ladda låtar
song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

# EXIT-knapp
if st.button("EXIT"):
    st.session_state.current_song = "VÄLJ LÅT..."
    st.rerun()

# Rullista (35% bredd)
selected = st.selectbox(
    "Välj låt",
    options=options,
    index=options.index(st.session_state.current_song) if st.session_state.current_song in options else 0,
    label_visibility="collapsed"
)

if selected != st.session_state.current_song:
    st.session_state.current_song = selected
    st.rerun()

# --- 4. RENDER CONTENT ---
if st.session_state.current_song != "VÄLJ LÅT...":
    file_name = song_map[st.session_state.current_song]
    path = LIB_DIR / f"{file_name}.md"
    
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-display">{content}</div>', unsafe_allow_html=True)
else:
    st.empty()

# Scroll-fix till toppen
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
