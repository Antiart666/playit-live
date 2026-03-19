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

if "selected_song" not in st.session_state:
    st.session_state.selected_song = None

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_name(n):
    return str(n).replace('_', ' ').strip().title()

def get_songs():
    files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
    return {format_name(f): f for f in files}

def get_logo_b64():
    if LOGO_PATH.exists():
        with open(LOGO_PATH, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. CSS: HORIZONTAL SCROLL & NO-OVERLAY ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* FIXED HEADER BASE */
    .header-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 160px;
        background: #ffffff;
        z-index: 999;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (VÄNSTER) */
    .stage-logo {{
        position: fixed;
        left: 10px;
        top: 5px;
        height: 100px;
        z-index: 1000;
        transform: rotate(-5deg);
    }}

    /* START-KNAPP (HÖGER) */
    .start-btn-container {{
        position: fixed;
        top: 20px;
        right: 15px;
        z-index: 1001;
    }}

    /* HORISONTELL LÅT-LISTA (CENTRAL) */
    /* Denna ersätter rullisten för att inte täcka skärmen */
    .song-slider {{
        position: fixed;
        top: 110px;
        left: 0;
        width: 100%;
        height: 50px;
        overflow-x: auto;
        white-space: nowrap;
        background: #ffffff;
        padding: 5px 10px;
        z-index: 1002;
        border-top: 1px solid #eee;
        display: flex;
        gap: 10px;
        -webkit-overflow-scrolling: touch;
    }}

    /* Styla Streamlit-knapparna inuti slidern */
    div[data-testid="column"] {{
        min-width: 150px !important;
    }}

    .song-area {{
        margin-top: 170px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}

    /* Göm alla input-fält för att säkra mot tangentbord */
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

st.markdown('<div class="header-bar"></div>', unsafe_allow_html=True)

# 1. Logga
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:15px; top:20px; font-weight:900; font-size:30px; z-index:1000;">PLAYIT</div>', unsafe_allow_html=True)

# 2. START-knapp
with st.container():
    st.markdown('<div class="start-btn-container">', unsafe_allow_html=True)
    if st.button("START", key="reset_btn"):
        st.session_state.selected_song = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# 3. HORISONTELL MENY (Istället för rullista)
songs = get_songs()
st.markdown('<div style="height: 110px;"></div>', unsafe_allow_html=True) # Spacer

# Vi skapar en rad med knappar som man kan swipa i
cols = st.columns(len(songs) if songs else 1)
for i, (display_name, file_stem) in enumerate(songs.items()):
    with cols[i]:
        # Markera vald låt med färg
        is_active = st.session_state.selected_song == file_stem
        btn_type = "primary" if is_active else "secondary"
        if st.button(display_name.upper(), key=f"s_{file_stem}", type=btn_type):
            st.session_state.selected_song = file_stem
            st.rerun()

# --- 4. DISPLAY CONTENT ---
if st.session_state.selected_song:
    song_file = LIB_DIR / f"{st.session_state.selected_song}.md"
    if song_file.exists():
        with open(song_file, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)

# Scroll-fix
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
