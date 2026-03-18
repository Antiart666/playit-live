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

# --- CSS (ATOMKRAFT-LAYOUT) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* DÖLJ STANDARD-ELEMENT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* MASTER HEADER CONTAINER */
    .master-header {{
        position: fixed !important;
        top: 0;
        left: 0;
        width: 100%;
        height: 80px;
        background-color: #ffffff;
        z-index: 1000000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        border-bottom: 1px solid #eee;
    }}

    /* LOGGAN (VÄNSTER + KLICKBAR) */
    .logo-container {{
        width: 80px;
        cursor: pointer;
        transform: rotate(-8deg);
        filter: drop-shadow(2px 2px 3px rgba(0,0,0,0.1));
    }}
    .logo-container img {{
        width: 70px !important; /* Spikar storleken här */
        height: auto;
    }}

    /* RULLLISTAN (MITTEN) */
    .dropdown-container {{
        flex-grow: 1;
        max-width: 50%;
        margin: 0 10px;
    }}

    /* STYLING FÖR STREAMLIT SELECTBOX */
    div[data-testid="stSelectbox"] > div {{
        border: 2px solid #000 !important;
        border-radius: 12px !important;
        background: white !important;
        height: 45px !important;
    }}

    /* OSYNLIG PUNKT (HÖGER) FÖR BALANS */
    .right-balance {{
        width: 80px;
    }}

    /* LÄSRUTAN (TABS-SÄKER OCH GRÄNSLÖS) */
    .song-area-pro {{
        margin-top: 90px;
        height: 88vh !important;
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        padding: 10px 5px !important;
        border: none !important;
        
        /* Monospace garanterar spikraka tabs */
        font-family: 'Roboto Mono', 'Courier New', monospace !important;
        font-size: 14px !important; 
        line-height: 1.2 !important;
        
        /* Förbjuder radbrytning */
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
    }}

    /* LISTVYN KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION & LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# --- RENDERA DEN NYA HEADERN ---
st.markdown('<div class="master-header">', unsafe_allow_html=True)

# 1. Logga (Hemknapp)
col_l, col_c, col_r = st.columns([1, 4, 1])

with col_l:
    if st.button("🏠", key="home_btn", help="Gå hem"):
        st.session_state.view = "list"
        st.session_state.song_path = ""
        st.rerun()
    if logo_b64:
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_b64}"></div>', unsafe_allow_html=True)

# 2. Rulllista (Mitten)
with col_c:
    song_titles = [s["title"] for s in all_songs]
    try:
        current_idx = next(i for i, s in enumerate(all_songs) if s["path"] == st.session_state.song_path)
    except:
        current_idx = 0
    
    selected_song = st.selectbox("", options=song_titles, index=current_idx, label_visibility="collapsed", key="main_selector")
    
    # Logik för byte av låt
    if all_songs:
        new_path = next(s["path"] for s in all_songs if s["title"] == selected_song)
        if new_path != st.session_state.song_path:
            st.session_state.song_path = new_path
            st.session_state.view = "song"
            st.rerun()

# 3. Höger sida (Tom för balans)
with col_r:
    st.write("")

st.markdown('</div>', unsafe_allow_html=True)

# --- RENDERA INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.subheader("Mina Låtar")
    if not all_songs:
        st.warning("Inga låtar hittades i mappen 'library'.")
    else:
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
        # Visar låten med extra scroll-utrymme i botten
        st.markdown(f'<div class="song-area-pro">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
