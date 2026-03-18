import streamlit as st
import os
import base64

# 1. Konfiguration
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

def get_all_songs(directory):
    song_list = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".md"):
                    song_list.append({"title": clean_title(f), "path": os.path.join(root, f)})
    return sorted(song_list, key=lambda x: x["title"])

# --- CSS (DEN SVÄVANDE LISTAN) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* STÄDA BORT STREAMLIT-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* DEN SVÄVANDE LISTAN (HEADER) */
    .floating-header {{
        position: fixed !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 85px;
        background-color: rgba(255, 255, 255, 0.95);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center; /* Centrerar rullistan */
        padding: 0 20px;
    }}

    /* LOGGAN TILL VÄNSTER (KLICKBAR AREA) */
    .clickable-logo {{
        position: absolute !important;
        left: 15px !important;
        top: 15px !important;
        width: 90px !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
        z-index: 1000001 !important;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.15));
    }}

    /* RULLLISTAN I MITTEN */
    .center-nav {{
        width: 55% !important;
        max-width: 400px;
        margin-top: 5px;
    }}

    /* STYLING AV SELECTBOX */
    div[data-testid="stSelectbox"] > div {{
        border: 2px solid #000 !important;
        border-radius: 12px !important;
        height: 48px !important;
    }}

    /* LÄSRUTAN (SPIKRAKA TABS) */
    .song-reader-atom {{
        margin-top: 95px; /* Skapar plats för den svävande listan */
        height: 88vh !important;
        width: 100%;
        overflow-y: auto;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.15 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        padding-bottom: 100px;
    }}

    /* FIX FÖR ATT GÖRA LOGGAN KLICKBAR VIA STREAMLIT */
    .invisible-home-btn button {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 90px !important;
        height: 60px !important;
        opacity: 0 !important; /* Helt osynlig men ligger ÖVER loggan */
        z-index: 1000002 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION & LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# --- RENDERA HEADERN ---

# 1. Den osynliga knappen som ligger exakt på loggan för att göra den klickbar
st.markdown('<div class="invisible-home-btn">', unsafe_allow_html=True)
if st.button(" ", key="hidden_home_trigger"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 2. Den visuella headern
st.markdown('<div class="floating-header">', unsafe_allow_html=True)

# Loggan till vänster
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="clickable-logo">', unsafe_allow_html=True)

# Rullistan i mitten
st.markdown('<div class="center-nav">', unsafe_allow_html=True)
song_titles = [s["title"] for s in all_songs]
try:
    current_idx = next(i for i, s in enumerate(all_songs) if s["path"] == st.session_state.song_path)
except:
    current_idx = 0

selected_song = st.selectbox("", options=song_titles, index=current_idx, label_visibility="collapsed", key="global_selector")

if all_songs:
    new_path = next(s["path"] for s in all_songs if s["title"] == selected_song)
    if new_path != st.session_state.song_path:
        st.session_state.song_path = new_path
        st.session_state.view = "song"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Stäng floating-header

# --- RENDERA INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.subheader("Mina Låtar")
    cols = st.columns(2)
    for i, song in enumerate(all_songs):
        with cols[i % 2]:
            if st.button(song["title"], key=f"list_{song['path']}"):
                st.session_state.song_path = song["path"]
                st.session_state.view = "song"
                st.rerun()
else:
    if os.path.exists(st.session_state.song_path):
        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-reader-atom">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
