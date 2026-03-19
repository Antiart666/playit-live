import streamlit as st
import os
import base64
import time
from pathlib import Path

# --- 1. CONFIG ---
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initiera state för smidiga byten och scroll
if "selected_song" not in st.session_state:
    st.session_state.selected_song = None
if "scrolling" not in st.session_state:
    st.session_state.scrolling = False

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

# --- 2. CSS: OPTIMERAD LAYOUT & INGET HACK ---
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"], .stApp {{
        background-color: #ffffff !important;
    }}
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {{
        display: none !important;
    }}

    /* HEADER-BAR */
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
        left: 10px;
        top: 5px;
        height: 90px;
        z-index: 1000;
        transform: rotate(-5deg);
    }}

    /* TOP-CENTER & RIGHT KNAPPAR */
    /* Vi tvingar Streamlits knappar att ligga på rad i headern */
    .top-buttons {{
        position: fixed;
        top: 25px;
        right: 15px;
        z-index: 1001;
        display: flex;
        gap: 10px;
        align-items: center;
    }}

    /* LÅT-NAVIGERING (SWIPE) */
    .song-nav {{
        position: fixed;
        top: 100px;
        left: 0;
        width: 100%;
        overflow-x: auto;
        white-space: nowrap;
        padding: 10px;
        z-index: 1002;
        background: #fff;
        display: flex;
        gap: 10px;
        border-top: 1px solid #eee;
    }}

    /* LÅT-TEXT */
    .song-content {{
        margin-top: 175px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.2 !important;
        white-space: pre-wrap !important;
        color: #000 !important;
        padding-bottom: 90vh;
    }}

    /* Snyggare knappar för swajp-listan */
    .stButton > button {{
        border-radius: 8px !important;
        text-transform: uppercase !important;
        font-weight: 800 !important;
    }}

    /* Göm tangentbord */
    input {{ display: none !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. RENDER UI ---

st.markdown('<div class="header-box"></div>', unsafe_allow_html=True)

# Logga
logo_data = get_logo_b64()
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="stage-logo">', unsafe_allow_html=True)

# Topp-knappar (Scroll & Start)
col_top1, col_top2 = st.columns([7, 3]) # Dummy för att positionera

# Vi placerar knapparna manuellt via CSS men använder ST-logik för snabbhet
with st.container():
    # START och SCROLL knappar
    c1, c2, c3 = st.columns([5, 3, 2])
    with c3: # Längst till höger
        if st.button("START", key="reset"):
            st.session_state.selected_song = None
            st.session_state.scrolling = False
            st.rerun()
    with c2: # Mitten
        scroll_label = "STOPP" if st.session_state.scrolling else "SCROLL"
        if st.button(scroll_label, key="scroll_toggle"):
            st.session_state.scrolling = not st.session_state.scrolling
            st.rerun()

# LÅT-MENY (Horisontell swajp)
songs = get_songs()
if songs:
    # Vi skapar en rad med små knappar som inte triggar omladdning av hela sidan
    song_cols = st.columns(len(songs))
    for i, (name, stem) in enumerate(songs.items()):
        with song_cols[i]:
            if st.button(name.upper(), key=f"btn_{stem}", use_container_width=True):
                st.session_state.selected_song = stem
                st.session_state.scrolling = False # Stoppa scroll vid byte
                st.rerun()

# --- 4. DISPLAY CONTENT ---
if st.session_state.selected_song:
    song_file = LIB_DIR / f"{st.session_state.selected_song}.md"
    if song_file.exists():
        with open(song_file, "r", encoding="utf-8") as f:
            lyrics = f.read()
        st.markdown(f'<div class="song-content" id="lyrics-area">{lyrics}</div>', unsafe_allow_html=True)

# --- 5. JAVASCRIPT: AUTOSCROLL & RESET ---
if st.session_state.scrolling:
    # Detta skript rullar sidan sakta nedåt
    st.markdown("""
        <script>
        var scrollInterval = setInterval(function() {
            window.scrollBy(0, 1);
        }, 50); // Justera hastighet här (högre siffra = långsammare)
        window.scrollInterval = scrollInterval;
        </script>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <script>
        clearInterval(window.scrollInterval);
        </script>
    """, unsafe_allow_html=True)

# Scroll till toppen vid ny låt (om inte scroll är på)
if not st.session_state.scrolling:
    st.markdown("<script>window.parent.document.querySelector('.main').scrollTop = 0;</script>", unsafe_allow_html=True)
