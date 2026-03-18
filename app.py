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

# --- CSS (DEN ULTIMATA SCEN-LAYOUTEN) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* RIV NER STREAMLIT-STANDARD */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* LOGGAN (HEM-KNAPP) */
    .fixed-logo-top {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 90px !important;
        z-index: 1000005 !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}

    /* OSYNLIG HEM-KNAPP */
    .home-hitbox button {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 90px !important;
        height: 55px !important;
        opacity: 0 !important;
        z-index: 1000006 !important;
    }}

    /* RULLLISTAN (POSITION OCH STIL) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 15px !important;
        left: 115px !important;
        width: 220px !important;
        z-index: 1000005 !important;
    }}

    /* TVINGA LJUS LOOK & INGET TANGENTBORD */
    div[data-testid="stSelectbox"] > div {{
        background-color: #f2f2f2 !important;
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
    }}
    
    /* DÖDA TANGENTBORDET */
    div[data-testid="stSelectbox"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    div[data-testid="stSelectbox"] * {{
        color: #000000 !important;
    }}

    /* LÄSRUTAN (SPIKRAKA TABS) */
    .song-display {{
        margin-top: 85px;
        height: 85vh !important;
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
    .archive-btn button {{
        background-color: #f9f9f9 !important;
        border: 1px solid #eee !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-weight: 800 !important;
        color: black !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# 1. Osynlig hem-trigger
st.markdown('<div class="home-hitbox">', unsafe_allow_html=True)
if st.button(" ", key="home_trigger"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 2. Loggan
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="fixed-logo-top">', unsafe_allow_html=True)

# 3. Rullistan (bredvid loggan)
song_titles = [s["title"] for s in all_songs]
try:
    current_idx = next(i for i, s in enumerate(all_songs) if s["path"] == st.session_state.song_path)
except:
    current_idx = 0

selected_title = st.selectbox("", options=song_titles, index=current_idx, label_visibility="collapsed", key="global_nav")

if all_songs:
    new_path = next(s["path"] for s in all_songs if s["title"] == selected_title)
    if new_path != st.session_state.song_path:
        st.session_state.song_path = new_path
        st.session_state.view = "song"
        st.rerun()

# --- INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:90px;"></div>', unsafe_allow_html=True)
    st.subheader("Välj låt")
    if all_songs:
        cols = st.columns(2)
        for i, song in enumerate(all_songs):
            with cols[i % 2]:
                st.markdown('<div class="archive-btn">', unsafe_allow_html=True)
                if st.button(song["title"], key=f"btn_{song['path']}"):
                    st.session_state.song_path = song["path"]
                    st.session_state.view = "song"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
else:
    if os.path.exists(st.session_state.song_path):
        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-display">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
