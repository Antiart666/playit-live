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
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return ""
    return ""

def get_all_songs():
    songs = []
    if os.path.exists("library"):
        for f in os.listdir("library"):
            if f.endswith(".md"):
                title = f.replace(".md", "").replace("_", " ").strip().capitalize()
                songs.append({"title": title, "path": os.path.join("library", f)})
    return sorted(songs, key=lambda x: x["title"])

# --- SESSION STATE ---
if "active_song" not in st.session_state:
    st.session_state.active_song = None

# --- CSS (DEN OPTIMERADE COMMAND-CENTRALEN) ---
logo_data = get_image_base64("logo.png")

st.markdown(f"""
<style>
    /* Dölj Streamlit standard-element */
    [data-testid="stHeader"], header, footer, #MainMenu {{ display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* Behållaren för hela sidan */
    .block-container {{
        padding-top: 20px !important;
        max-width: 100% !important;
    }}

    /* LOGGAN - Fast position men med marginal */
    .fixed-logo {{
        position: fixed;
        top: 25px;
        left: 15px;
        width: 85px;
        transform: rotate(-8deg);
        z-index: 1000001;
        cursor: pointer;
    }}

    /* RULLLISTA - Mörk och Keyboard-safe */
    div[data-testid="stSelectbox"] {{
        position: fixed !important;
        top: 25px !important;
        left: 115px !important;
        width: 200px !important;
        z-index: 1000000 !important;
    }}

    /* Stylar själva boxen till mörkgrå/svart */
    div[data-testid="stSelectbox"] > div {{
        background-color: #1a1a1a !important;
        color: white !important;
        border: 2px solid #333 !important;
        border-radius: 8px !important;
    }}

    /* Tvingar all text i rullistan till vit */
    div[data-testid="stSelectbox"] * {{
        color: white !important;
    }}

    /* STOPPAR TANGENTBORDET */
    div[data-testid="stSelectbox"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* LÄSYTA */
    .lyrics-view {{
        margin-top: 100px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 15px !important;
        line-height: 1.25 !important;
        white-space: pre !important; 
        color: #000;
    }}

    /* STORA LIST-KNAPPAR */
    .stButton > button {{
        width: 100% !important;
        height: 55px !important;
        background-color: #f9f9f9 !important;
        border: 1px solid #ddd !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION & LOGGA ---
songs = get_all_songs()
song_titles = [s["title"] for s in songs]

# Loggan (Hemknapp)
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="fixed-logo">', unsafe_allow_html=True)

# Osynlig hem-trigger ovanpå loggan
if st.button(" ", key="home_trigger", help="Hem"):
    st.session_state.active_song = None
    st.rerun()

# --- RULLLISTAN ---
# Vi lägger till en tom sträng först för att inte välja något direkt
current_idx = 0
if st.session_state.active_song:
    try:
        current_idx = song_titles.index(st.session_state.active_song["title"]) + 1
    except: current_idx = 0

selected_nav = st.selectbox(
    "",
    options=["Välj låt..."] + song_titles,
    index=current_idx,
    label_visibility="collapsed"
)

# Om användaren väljer i rullistan
if selected_nav != "Välj låt...":
    new_song = next(s for s in songs if s["title"] == selected_nav)
    if st.session_state.active_song != new_song:
        st.session_state.active_song = new_song
        st.rerun()

# --- RENDERING AV INNEHÅLL ---
if st.session_state.active_song:
    # VISA LÅTEN
    path = st.session_state.active_song["path"]
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="lyrics-view">{content}{chr(10)*60}</div>', unsafe_allow_html=True)
else:
    # VISA LISTAN (ARKIVET)
    st.markdown('<div style="height:90px;"></div>', unsafe_allow_html=True)
    st.subheader("Låtarkiv")
    cols = st.columns(2)
    for i, song in enumerate(songs):
        with cols[i % 2]:
            if st.button(song["title"], key=f"btn_{i}"):
                st.session_state.active_song = song
                st.rerun()
