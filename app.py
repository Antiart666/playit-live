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

# State för att hantera låtbyten utan "hacks"
if "active_song_content" not in st.session_state:
    st.session_state.active_song_content = ""
if "current_song_name" not in st.session_state:
    st.session_state.current_song_name = ""

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {f.replace('_', ' ').strip().title(): f for f in files}

def get_logo_b64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. THE RIGID CSS (Masterprompt 1.0 Base) ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* HEADER */
    .header-box {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: #ffffff;
        z-index: 999;
        border-bottom: 2px solid #f0f0f0;
    }}

    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 10px;
        height: 80px;
        z-index: 1000;
        transform: rotate(-5deg);
    }}

    /* START-KNAPP (TOP RIGHT) */
    .start-trigger {{
        position: fixed;
        top: 25px;
        right: 15px;
        background: #000;
        color: #fff !important;
        padding: 10px 20px;
        border-radius: 50px;
        font-weight: 900;
        z-index: 1001;
        text-transform: uppercase;
        font-size: 14px;
        cursor: pointer;
        border: none;
    }}

    /* LÅT-RADEN (HORISONTELL SWIPE) */
    .song-nav-container {{
        position: fixed;
        top: 100px;
        left: 0;
        width: 100%;
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 15px;
        z-index: 1002;
        background: #fff;
        display: block; /* Tvingar rad-format */
        -webkit-overflow-scrolling: touch;
    }}

    /* Låt-brickorna */
    .song-item {{
        display: inline-block;
        color: #000 !important;
        background: #f0f0f0;
        padding: 8px 15px;
        margin-right: 10px;
        border-radius: 8px;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 14px;
        border: 1px solid #ddd;
    }}

    /* LÅT-TEXT */
    .song-content {{
        margin-top: 170px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDER UI ---

st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)

# Logga
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:15px; top:20px; font-weight:900; font-size:30px; z-index:1000;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp (Vi använder st.button men stylar den som en länk för att undvika "svarta rutan")
if st.button("START", key="reset_v8"):
    st.session_state.active_song_content = ""
    st.session_state.current_song_name = ""
    st.rerun()

# LÅT-RADEN (Byggd med HTML för att garantera swajp)
songs = get_songs()
st.markdown('<div class="song-nav-container">', unsafe_allow_html=True)
# Vi skapar en rad knappar. När man trycker på en knapp, triggas Streamlit-logik blixtsnabbt.
cols = st.columns(len(songs) if songs else 1)
for i, (display_name, file_stem) in enumerate(songs.items()):
    with cols[i]:
        if st.button(display_name.upper(), key=f"s_{file_stem}"):
            song_path = LIB_DIR / f"{file_stem}.md"
            if song_path.exists():
                with open(song_path, "r", encoding="utf-8") as f:
                    st.session_state.active_song_content = f.read()
                    st.session_state.current_song_name = display_name
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. DISPLAY CONTENT ---
if st.session_state.active_song_content:
    st.markdown(f'<div class="song-content">{st.session_state.active_song_content}</div>', unsafe_allow_html=True)

# Scroll till toppen
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
