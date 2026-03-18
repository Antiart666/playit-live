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

# --- CSS (ULTRA-CLEAN TOP-LEFT LAYOUT) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* DÖLJ ALLT ONÖDIGT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* TOP-LEFT NAV BAR */
    .top-left-nav {{
        position: fixed !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #ffffff;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding-left: 10px;
    }}

    /* LOGGAN (90px, klickbar, överst till vänster) */
    .logo-home {{
        width: 90px !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
        margin-right: 15px;
        filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.05));
    }}

    /* RULLLISTAN (Ljusgrå kant, bredvid loggan) */
    .dropdown-box {{
        width: 180px !important; /* Diskret bredd */
    }}

    /* STYLING AV SELECTBOX - Ljus och ren */
    div[data-testid="stSelectbox"] > div {{
        border: 1px solid #eeeeee !important; /* Ljusgrå kant som begärt */
        border-radius: 8px !important;
        background: #ffffff !important;
        height: 40px !important;
        font-size: 14px !important;
    }}

    /* OSYNLIG HEM-TRIGGER PÅ LOGGAN */
    .home-trigger button {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 90px !important;
        height: 50px !important;
        opacity: 0 !important;
        z-index: 1000001 !important;
    }}

    /* LÄSRUTAN (TABS-SÄKER) */
    .song-reader-clean {{
        margin-top: 80px;
        height: 88vh !important;
        width: 100%;
        overflow-y: auto;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        padding-bottom: 100px;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 1px solid #eee !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION & LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# 1. Osynlig hemknapp på loggan
st.markdown('<div class="home-trigger">', unsafe_allow_html=True)
if st.button(" ", key="hidden_home"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 2. Rendera den rena toppen
st.markdown('<div class="top-left-nav">', unsafe_allow_html=True)

# Logga
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-home">', unsafe_allow_html=True)

# Rulllista direkt bredvid
st.markdown('<div class="dropdown-box">', unsafe_allow_html=True)
song_titles = [s["title"] for s in all_songs]
try:
    current_idx = next(i for i, s in enumerate(all_songs) if s["path"] == st.session_state.song_path)
except:
    current_idx = 0

selected_song = st.selectbox("", options=song_titles, index=current_idx, label_visibility="collapsed", key="nav_select")

if all_songs:
    new_path = next(s["path"] for s in all_songs if s["title"] == selected_song)
    if new_path != st.session_state.song_path:
        st.session_state.song_path = new_path
        st.session_state.view = "song"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:90px;"></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="song-reader-clean">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
