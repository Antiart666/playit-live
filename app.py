import streamlit as st
import os
import base64
from pathlib import Path

# --- 1. CONFIG (MASTERPROMPT 1.0) ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hämta vald låt från URL för att undvika widget-kaos
query_params = st.query_params
active_song = query_params.get("song", None)

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

# --- 2. CSS: RIGID STAGE LAYOUT ---
st.markdown(f"""
    <style>
    /* Scen-bakgrund */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* HEADER-PLATTA (Låst vit box överst) */
    .header-box {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 155px;
        background: #ffffff;
        z-index: 999;
        border-bottom: 2px solid #f0f0f0;
    }}

    /* LOGO (VÄNSTER) */
    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 10px;
        height: 90px;
        z-index: 1000;
        transform: rotate(-5deg);
    }}

    /* START-KNAPP (UPPE HÖGER) */
    .start-link {{
        position: fixed;
        top: 25px;
        right: 20px;
        background: #000;
        color: #fff !important;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 900;
        text-decoration: none !important;
        z-index: 1001;
        text-transform: uppercase;
        font-size: 14px;
        display: inline-block;
    }}

    /* LÅT-RADEN (HORISONTELL SWIPE) */
    .song-nav {{
        position: fixed;
        top: 105px;
        left: 0;
        width: 100%;
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px 15px;
        z-index: 1002;
        background: #ffffff;
        -webkit-overflow-scrolling: touch;
        display: block;
    }}

    .song-link {{
        display: inline-block;
        color: #000 !important;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 14px;
        padding: 8px 15px;
        margin-right: 10px;
        border: 1px solid #ddd;
        border-radius: 8px;
        background: #f9f9f9;
        text-transform: uppercase;
    }}

    /* Markera vald låt tydligt */
    .song-link.active {{
        background: #ff0000 !important;
        color: #fff !important;
        border-color: #ff0000;
    }}

    /* LÅT-TEXTEN (ACKORDEN) */
    .song-content {{
        margin-top: 175px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 85vh;
        width: 100%;
    }}
    
    /* TOTAL FÖRBUD MOT TANGENTBORD */
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDER UI ---

# Rita den fasta bakgrunden för headern
st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)

# 1. Logga
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:15px; top:25px; font-weight:900; font-size:30px; z-index:1000;">PLAYIT</div>', unsafe_allow_html=True)

# 2. START-knapp (Rensar URL för att nollställa låtvalet)
st.markdown('<a href="/" target="_self" class="start-link">START</a>', unsafe_allow_html=True)

# 3. LÅT-MENY (Horisontell swajp-rad)
songs = get_songs()
song_links_html = ""
for display_name, file_stem in songs.items():
    active_class = "active" if active_song == file_stem else ""
    song_links_html += f'<a href="?song={file_stem}" target="_self" class="song-link {active_class}">{display_name.upper()}</a>'

st.markdown(f'<div class="song-nav">{song_links_html}</div>', unsafe_allow_html=True)

# --- 4. DISPLAY CONTENT ---
if active_song:
    song_file = LIB_DIR / f"{active_song}.md"
    if song_file.exists():
        with open(song_file, "r", encoding="utf-8") as f:
            lyrics = f.read()
        st.markdown(f'<div class="song-content">{lyrics}</div>', unsafe_allow_html=True)

# Nollställ scroll till toppen när en låt laddas
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
