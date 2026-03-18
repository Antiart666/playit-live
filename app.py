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

# --- CSS (DEN OSYNLIGA HEADERN & STABILA TABS) ---
logo_data = get_image_base64("logo.png")

st.markdown(f"""
<style>
    /* GÖR STREAMLITS HEADER GENOMSKINLIG MEN KVAR */
    [data-testid="stHeader"] {{
        background-color: rgba(0,0,0,0) !important;
        border-bottom: none !important;
        height: 70px !important;
    }}
    
    /* Dölj standard-menyer */
    footer, #MainMenu {{ display: none !important; }}
    
    .stApp {{ background-color: #ffffff !important; }}
    
    /* Behållaren för innehåll */
    .block-container {{
        padding-top: 80px !important;
        max-width: 100% !important;
    }}

    /* LOGGAN */
    .fixed-logo {{
        position: fixed;
        top: 15px;
        left: 15px;
        width: 75px;
        transform: rotate(-8deg);
        z-index: 1000001;
    }}

    /* NAVIGATIONSRADEN (I HEADERN) */
    .nav-container {{
        position: fixed;
        top: 15px;
        left: 105px;
        right: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1000002;
    }}

    /* MÖRK RULLLISTA */
    div[data-testid="stSelectbox"] {{
        flex-grow: 1 !important;
        min-width: 150px !important;
        margin-bottom: 0 !important;
    }}

    div[data-testid="stSelectbox"] > div {{
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stSelectbox"] * {{ color: white !important; }}

    /* STOPPA TANGENTBORDET */
    div[data-testid="stSelectbox"] input {{
        pointer-events: none !important;
        caret-color: transparent !important;
    }}

    /* TILLBAKA-KNAPP */
    .back-btn button {{
        background-color: #1a1a1a !important;
        color: white !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
        height: 45px !important;
        font-weight: bold !important;
    }}

    /* LÅT-TEXT (SÄKER FÖR TABS & SKROLL) */
    .song-content {{
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important; /* Gör att långa rader kan skrollas */
        color: #000;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        width: 100%;
    }}

    /* ARKIV-KNAPPAR */
    .archive-grid .stButton > button {{
        width: 100% !important;
        height: 50px !important;
        background-color: #f0f2f6 !important;
        border: none !important;
        color: #000 !important;
        border-radius: 10px !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- NAVIGATION ---
songs = get_all_songs()
song_titles = [s["title"] for s in songs]

# Logga
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="fixed-logo">', unsafe_allow_html=True)

# Övre Nav-rad
col_select, col_back = st.columns([4, 1])

with col_select:
    current_idx = 0
    if st.session_state.active_song:
        try:
            current_idx = song_titles.index(st.session_state.active_song["title"]) + 1
        except: current_idx = 0
    
    selected_nav = st.selectbox(
        "",
        options=["Välj låt..."] + song_titles,
        index=current_idx,
        label_visibility="collapsed",
        key="top_nav_select"
    )

with col_back:
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("EXIT", key="exit_btn"):
        st.session_state.active_song = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Logik för val
if selected_nav != "Välj låt...":
    new_song = next(s for s in songs if s["title"] == selected_nav)
    if st.session_state.active_song != new_song:
        st.session_state.active_song = new_song
        st.rerun()

# --- INNEHÅLL ---
if st.session_state.active_song:
    path = st.session_state.active_song["path"]
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Vi använder en <pre> tagg inuti div för maximal tab-stabilitet
        st.markdown(f'<pre class="song-content">{content}{chr(10)*50}</pre>', unsafe_allow_html=True)
else:
    # Startsidan/Arkivet
    st.subheader("Låtlista")
    st.markdown('<div class="archive-grid">', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, song in enumerate(songs):
        with cols[i % 2]:
            if st.button(song["title"], key=f"list_btn_{i}"):
                st.session_state.active_song = song
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
