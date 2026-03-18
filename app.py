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

# --- 2. THE TOTAL LOCKDOWN UI (CSS & JS) ---
st.markdown(f"""
    <style>
    /* Scen-läge */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* HEADER-BAR */
    .header-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 150px;
        background: #ffffff;
        z-index: 999990;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (MASSIV 150px) */
    .stage-logo {{
        position: fixed;
        left: 10px;
        top: 5px;
        height: 150px;
        width: auto;
        transform: rotate(-6deg);
        z-index: 1000005 !important;
    }}

    /* RULLIST (35% BREDD + CENTER) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 25px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 35% !important;
        z-index: 1000010 !important;
    }}

    /* TANGENTBORDS-DÖDARE (HÄNGSLEN) */
    div[data-baseweb="select"] input {{
        caret-color: transparent !important;
        pointer-events: none !important;
        user-select: none !important;
    }}
    
    /* DEN OSYNLIGA SKÖLDEN (LIVREM) */
    /* Denna ligger ovanpå rullistan så att fingret aldrig nuddar textfältet */
    .selectbox-shield {{
        position: fixed;
        top: 25px;
        left: 50%;
        transform: translateX(-50%);
        width: 35%;
        height: 45px;
        z-index: 1000011;
        background: rgba(255,255,255,0); /* Helt osynlig */
        cursor: pointer;
    }}

    /* START-KNAPP (HTML-LÄNK) */
    .start-link {{
        position: fixed;
        top: 25px;
        right: 15px;
        background-color: #000000;
        color: #ffffff !important;
        padding: 12px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 15px;
        text-decoration: none !important;
        z-index: 1000015 !important;
        text-transform: uppercase;
    }}

    /* SONG DISPLAY */
    .song-area {{
        margin-top: 170px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    </style>

    <script>
    // JAVASCRIPT LOCKDOWN (NUCLEAR OPTION)
    function forceNoKeyboard() {{
        const inputs = window.parent.document.querySelectorAll('input');
        inputs.forEach(input => {{
            // 1. Gör fältet oredigerbart
            input.setAttribute('readonly', 'true');
            // 2. Berätta för mobilen att inget tangentbord behövs
            input.setAttribute('inputmode', 'none');
            // 3. Om fältet ändå får fokus, kasta ut det direkt
            if (window.parent.document.activeElement === input) {{
                input.blur();
            }}
        }});
    }}
    // Körs 20 gånger i sekunden
    setInterval(forceNoKeyboard, 50);
    </script>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

st.markdown('<div class="header-bar"></div>', unsafe_allow_html=True)
# Lägg till den osynliga skölden för att skydda rullistan från klick-fokus
st.markdown('<div class="selectbox-shield"></div>', unsafe_allow_html=True)

logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:40px; z-index:1000005;">PLAYIT</div>', unsafe_allow_html=True)

st.markdown('<a href="/" target="_self" class="start-link">START</a>', unsafe_allow_html=True)

song_map = get_songs()
options = ["VÄLJ LÅT..."] + list(song_map.keys())

try:
    current_idx = options.index(st.session_state.active_song)
except:
    current_idx = 0

selected = st.selectbox(
    "Välj låt",
    options=options,
    index=current_idx,
    label_visibility="collapsed",
    key="song_picker_v3_1"
)

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
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)

st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
