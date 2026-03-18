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

def get_image_base64(path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return ""
    return ""

def get_all_songs(directory):
    song_list = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".md"):
                    title = f.replace(".md", "").replace("_", " ").strip().capitalize()
                    song_list.append({"title": title, "path": os.path.join(root, f)})
    return sorted(song_list, key=lambda x: x["title"])

# --- CSS (EXPERT-STYLING FÖR MÖRK RULLISTA) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
<style>
    /* Dölj allt Streamlit-standard */
    header, footer, #MainMenu, [data-testid="stHeader"] {{ display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* HEADER */
    .nav-zone {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 70px;
        background: white; z-index: 999999;
        display: flex; align-items: center; padding-left: 10px;
        border-bottom: 1px solid #eee;
    }}

    .logo-container {{
        width: 85px; transform: rotate(-8deg);
        margin-right: 15px; cursor: pointer;
    }}

    /* POSITIONERING AV RULLLISTA */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 15px !important;
        left: 110px !important;
        width: 220px !important;
        z-index: 1000000 !important;
    }}

    /* MÖRK RULLLISTA MED VIT TEXT */
    div[data-testid="stSelectbox"] > div {{
        background-color: #1e1e1e !important; /* Mörk bakgrund */
        color: white !important;
        border: 2px solid #333 !important;
        border-radius: 10px !important;
    }}

    /* Tvinga all text inuti rullistan att vara vit */
    div[data-testid="stSelectbox"] * {{
        color: white !important;
    }}

    /* BLOCKERA TANGENTBORD: Gör input-fältet oklickbart */
    div[data-testid="stSelectbox"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* LÄSYTA */
    .song-view {{
        margin-top: 80px;
        padding: 20px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
    }}

    /* Knappar i listan */
    div[data-testid="stButton"] > button {{
        width: 100% !important;
        background-color: #f8f8f8 !important;
        border: 1px solid #ddd !important;
        color: black !important;
        padding: 15px !important;
        font-weight: bold !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- NAVIGATIONSLOGIK ---
if "current_song" not in st.session_state:
    st.session_state.current_song = None

songs_dir = "library"
all_songs = get_all_songs(songs_dir)
titles = [s["title"] for s in all_songs]

# --- HEADER ELEMENT ---
st.markdown('<div class="nav-zone">', unsafe_allow_html=True)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img" style="width:85px; transform:rotate(-8deg);">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Osynlig knapp ovanpå loggan för att gå hem
st.markdown('<div style="position:fixed; top:10px; left:10px; width:85px; height:50px; z-index:1000001; cursor:pointer;">', unsafe_allow_html=True)
if st.button(" ", key="home_btn", help="Hem"):
    st.session_state.current_song = None
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- RULLLISTAN (Streamlit Native men stylad mörk) ---
selected_title = st.selectbox(
    "",
    options=["Välj låt..."] + titles,
    index=0 if st.session_state.current_song is None else titles.index(st.session_state.current_song["title"]) + 1,
    label_visibility="collapsed"
)

if selected_title != "Välj låt...":
    song_obj = next(s for s in all_songs if s["title"] == selected_title)
    if st.session_state.current_song != song_obj:
        st.session_state.current_song = song_obj
        st.rerun()

# --- INNEHÅLL ---
if st.session_state.current_song:
    path = st.session_state.current_song["path"]
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-view">{content + ("\n" * 60)}</div>', unsafe_allow_html=True)
else:
    # Startvy: Arkiv med knappar
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, song in enumerate(all_songs):
        with cols[i % 2]:
            if st.button(song["title"], key=f"list_{i}"):
                st.session_state.current_song = song
                st.rerun()
