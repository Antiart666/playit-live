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
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".md"):
                song_list.append({"title": clean_title(f), "path": os.path.join(root, f)})
    return sorted(song_list, key=lambda x: x["title"])

# --- CSS (Minimalistisk Header: Klickbar logga & Osynlig högerknapp) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* 1. LOGGAN SOM HEMKNAPP (VÄNSTER) */
    .header-logo-btn {{
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        width: 75px !important; 
        z-index: 1000006 !important;
        background: none !important;
        border: none !important;
        padding: 0 !important;
        cursor: pointer !important;
        transform: rotate(-8deg) !important;
        filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.1));
    }}

    /* 2. RULLISTAN (MITTEN) */
    .header-center-dropdown {{
        position: fixed !important;
        top: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 50% !important; 
        z-index: 1000005 !important;
    }}

    /* 3. OSYNLIG KNAPP (HÖGER) - För symmetri i koden */
    .header-right-invisible {{
        position: fixed !important;
        top: 15px !important;
        right: 15px !important;
        width: 80px !important;
        height: 45px !important;
        z-index: 1000005 !important;
        opacity: 0 !important; /* Gör den helt osynlig */
        pointer-events: none !important; /* Gör den oklickbar så den inte stör */
    }}

    /* Styling för dropdown */
    div[data-testid="stSelectbox"] > div {{
        border: 2px solid #000 !important;
        border-radius: 10px !important;
        background: white !important;
    }}

    /* TABS-SÄKERHET OCH LÄSYTA */
    .song-reader-final {{
        height: 90vh !important;
        width: 100%;
        margin-top: 100px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION & LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# RENDERA LOGGA SOM HEMKNAPP (Vänster)
# Vi använder en Streamlit-knapp men gömmer den bakom loggan med CSS
st.markdown('<div class="header-logo-btn">', unsafe_allow_html=True)
if st.button(" ", key="logo_home_trigger"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" style="width:100%; pointer-events:none;">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# RENDERA RULLLISTA (Mitten)
st.markdown('<div class="header-center-dropdown">', unsafe_allow_html=True)
song_titles = [s["title"] for s in all_songs]
try:
    current_idx = next(i for i, s in enumerate(all_songs) if s["path"] == st.session_state.song_path)
except:
    current_idx = 0

selected_song_title = st.selectbox("", options=song_titles, index=current_idx, label_visibility="collapsed")
new_path = next(s["path"] for s in all_songs if s["title"] == selected_song_title)

if new_path != st.session_state.song_path:
    st.session_state.song_path = new_path
    st.session_state.view = "song"
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# RENDERA OSYNLIG FYLLNAD (Höger)
st.markdown('<div class="header-right-invisible"></div>', unsafe_allow_html=True)

# --- INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:110px;"></div>', unsafe_allow_html=True)
    st.subheader("Alla Låtar")
    # Enkel listvy som backup
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
        st.markdown(f'<div class="song-reader-final">{content + ("\n"*55)}</div>', unsafe_allow_html=True)
