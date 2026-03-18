import streamlit as st
import os
import base64

# 1. Konfiguration - Maximerad yta
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

# --- CSS (EXAKT POSITIONERING & INGET TANGENTBORD) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* STÄDA BORT ALLT STANDARD */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* LOGGAN (UPPE TILL VÄNSTER) */
    .fixed-logo {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 85px !important;
        z-index: 1000005 !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}

    /* OSYNLIG HEM-TRIGGER */
    .home-trigger button {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 85px !important;
        height: 50px !important;
        opacity: 0 !important;
        z-index: 1000006 !important;
    }}

    /* RULLLISTAN (BREVID LOGGAN) */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 15px !important;
        left: 110px !important; /* Exakt brevid loggan */
        width: 200px !important;
        z-index: 1000005 !important;
    }}

    /* STYLING AV SELECTBOX (Ljusgrå bakgrund, ingen keyboard-fokus) */
    div[data-testid="stSelectbox"] div[role="button"] {{
        background-color: #f8f8f8 !important; /* Ljusgrå bakgrund */
        border: 1px solid #dddddd !important;
        border-radius: 8px !important;
        height: 42px !important;
        color: #000 !important;
    }}
    
    /* Förhindra tangentbord genom att dölja input-fältet som triggar det */
    div[data-testid="stSelectbox"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* LÄSRUTAN (SPIKRAKA TABS) */
    .song-reader-atomkraft {{
        margin-top: 80px;
        height: 88vh !important;
        width: 100%;
        overflow-y: auto;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.15 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        padding-bottom: 120px;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 1px solid #eee !important;
        border-radius: 8px !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION & LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# 1. Osynlig hem-trigger
st.markdown('<div class="home-trigger">', unsafe_allow_html=True)
if st.button(" ", key="hidden_home"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# 2. Rendera logga
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="fixed-logo">', unsafe_allow_html=True)

# 3. Rendera rullista (positioneras via CSS ovan)
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

# --- INNEHÅLL ---
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
        st.markdown(f'<div class="song-reader-atomkraft">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
