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

# --- 2. CSS & ANTI-KEYBOARD JAVASCRIPT ---
st.markdown(f"""
    <style>
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

    /* LOGO (EXTRA STOR) */
    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 5px;
        height: 150px; 
        width: auto;
        transform: rotate(-6deg);
        z-index: 1000005 !important;
    }}

    /* RULLIST (30% BREDD + CENTER) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 30% !important;
        z-index: 1000010 !important;
    }}

    /* TANGENTBORDS-STOPP (CSS-DEL) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
        touch-action: none !important;
    }}

    /* START-KNAPP (ERSÄTTER EXIT) */
    .start-anchor {{
        position: fixed;
        top: 25px;
        right: 25px;
        background: #000000;
        color: #ffffff !important;
        padding: 12px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 16px;
        text-decoration: none !important;
        z-index: 1000010 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* SONG DISPLAY */
    .song-area {{
        margin-top: 180px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    </style>

    <script>
    // DETTA STOPPAR TANGENTBORDET GENOM ATT TA BORT FOKUS OMEDELBART
    setInterval(function() {{
        var inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(function(input) {{
            input.setAttribute('readonly', 'true');
            if (window.parent.document.activeElement === input) {{
                input.blur();
            }}
        }});
    }}, 100);
    </script>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

# Bakgrund & Logo
logo_b64 = get_logo_b64()
st.markdown('<div class="header-anchor"></div>', unsafe_allow_html=True)

if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:30px; font-weight:900; font-size:40px; z-index:1000005;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp (Länk till startsidan)
st.markdown('<a href="/" target="_self" class="start-anchor">START</a>', unsafe_allow_html=True)

# Låtlista
song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

# Selectbox
selected = st.selectbox(
    "Välj låt",
    options=options,
    index=options.index(st.session_state.active_song) if st.session_state.active_song in options else 0,
    label_visibility="collapsed"
)

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
        # Lägg till 60 tomma rader enligt spec
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)
else:
    st.empty()

# Scroll-fix
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
