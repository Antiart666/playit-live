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

# Initiera state säkert
if "selected_song" not in st.session_state:
    st.session_state.selected_song = None

LIB_DIR = Path("library")
LIB_DIR.mkdir(exist_ok=True)
LOGO_PATH = Path("logo.png")

def format_name(n):
    if not n: return ""
    return str(n).replace('_', ' ').strip().title()

def get_songs():
    # Säkerställ att vi bara får faktiska filer och sorterar dem
    try:
        files = sorted([f.stem for f in LIB_DIR.glob("*.md") if f.is_file()])
        return {format_name(f): f for f in files}
    except Exception:
        return {}

def get_logo_b64():
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    return None

# --- 2. CSS: ABSOLUT FIXERING & TANGENTBORDS-SPÄRR ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

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

    .stage-logo {{
        position: fixed;
        left: 15px;
        top: 5px;
        height: 130px;
        z-index: 1000;
        transform: rotate(-6deg);
    }}

    /* START-KNAPP */
    div.stButton > button:first-child {{
        position: fixed !important;
        top: 25px !important;
        right: 20px !important;
        background-color: #000 !important;
        color: #fff !important;
        border-radius: 50px !important;
        padding: 10px 25px !important;
        z-index: 1001 !important;
        font-weight: 900 !important;
    }}

    /* POPOVER (VÄLJ LÅT) */
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

    .song-area {{
        margin-top: 160px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 80vh;
    }}
    
    /* TOTAL TANGENTBORDS-SPÄRR */
    input {{ display: none !important; visibility: hidden !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDERING ---

st.markdown('<div class="header-bar"></div>', unsafe_allow_html=True)

# Logga
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="stage-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="position:fixed; left:20px; top:35px; font-weight:900; font-size:35px; z-index:1000;">PLAYIT</div>', unsafe_allow_html=True)

# START (Reset)
if st.button("START"):
    st.session_state.selected_song = None
    st.rerun()

# Menyn (Popover)
songs = get_songs()
current_label = format_name(st.session_state.selected_song).upper() if st.session_state.selected_song else "VÄLJ LÅT..."

with st.popover(current_label):
    if not songs:
        st.write("Inga låtar hittades i /library")
    else:
        for display_name, file_stem in songs.items():
            # Unik key baserad på filnamnet för att undvika TypeError/DuplicateKey
            if st.button(display_name.upper(), key=f"btn_{file_stem}", use_container_width=True):
                st.session_state.selected_song = file_stem
                st.rerun()

# --- 4. DISPLAY CONTENT ---
if st.session_state.selected_song:
    song_file = LIB_DIR / f"{st.session_state.selected_song}.md"
    if song_file.exists():
        try:
            with open(song_file, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(f'<div class="song-area">{content}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Kunde inte läsa filen: {e}")

# Scroll-fix
st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
