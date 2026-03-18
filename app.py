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

# --- 2. CSS: THE "NO-INPUT" ARCHITECTURE ---
st.markdown(f"""
    <style>
    /* Grundtema */
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
        color: #000000 !important;
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
        z-index: 9999;
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
        z-index: 10000;
    }}

    /* START-KNAPP (TOP-RIGHT) */
    .start-link {{
        position: fixed;
        top: 25px;
        right: 20px;
        background-color: #000000;
        color: #ffffff !important;
        padding: 12px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 14px;
        text-decoration: none !important;
        z-index: 10001;
        text-transform: uppercase;
    }}

    /* CUSTOM HTML DROPDOWN (NO INPUT TAGS) */
    .custom-dropdown {{
        position: fixed;
        top: 30px;
        left: 50%;
        transform: translateX(-50%);
        width: 35%;
        z-index: 10002;
    }}

    /* Denna knapp triggar listan utan att vara ett textfält */
    .dropbtn {{
        width: 100%;
        background-color: #ffffff;
        color: #000;
        padding: 12px;
        font-size: 16px;
        font-weight: 800;
        border: 2px solid #000;
        border-radius: 10px;
        text-align: center;
        cursor: pointer;
    }}

    .dropdown-content {{
        display: none;
        position: absolute;
        background-color: #ffffff;
        width: 100%;
        max-height: 400px;
        overflow-y: auto;
        box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
        z-index: 10003;
        border-radius: 0 0 10px 10px;
        border: 2px solid #000;
        border-top: none;
    }}

    .dropdown-content a {{
        color: black;
        padding: 12px 16px;
        text-decoration: none;
        display: block;
        font-weight: 600;
        border-bottom: 1px solid #eee;
    }}

    .dropdown-content a:hover {{ background-color: #f1f1f1; }}

    /* Visa menyn vid klick/hover (mobilvänligt) */
    .custom-dropdown:active .dropdown-content, 
    .custom-dropdown:focus-within .dropdown-content {{
        display: block;
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
        width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIC & DATA ---
song_map = get_songs()
query_params = st.query_params
active_song_file = query_params.get("song", None)

# --- 4. RENDER UI ---

# Header-platta
st.markdown('<div class="header-bar"></div>', unsafe_allow_html=True)

# Logotyp
logo_b64 = get_logo_b64()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:35px; z-index:10000;">PLAYIT</div>', unsafe_allow_html=True)

# START-knapp
st.markdown('<a href="/" target="_self" class="start-link">START</a>', unsafe_allow_html=True)

# DEN NYA "TANGENTBORDSSÄKRA" MENYN
# Vi bygger en dropdown med uteslutande <a>-taggar och <div>-taggar.
current_display = format_name(active_song_file).upper() if active_song_file else "VÄLJ LÅT..."

links_html = ""
for snyggt_namn, filnamn in song_map.items():
    links_html += f'<a href="?song={filnamn}" target="_self">{snyggt_namn.upper()}</a>'

st.markdown(f"""
    <div class="custom-dropdown">
        <button class="dropbtn">{current_display}</button>
        <div class="dropdown-content">
            {links_html}
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 5. DISPLAY CONTENT ---
if active_song_file:
    path = LIB_DIR / f"{active_song_file}.md"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)

# Scroll till toppen
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
