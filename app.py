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

# --- CSS (EXAKT POSITIONERING & TANGENTBORDS-STOPP) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* DÖLJ ALLT STANDARD */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER */
    .nav-container {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background: white;
        z-index: 1000000;
        display: flex;
        align-items: center;
        padding-left: 10px;
    }}

    /* LOGGAN */
    .logo-img {{
        width: 85px;
        transform: rotate(-8deg);
        cursor: pointer;
        filter: drop-shadow(2px 2px 3px rgba(0,0,0,0.1));
    }}

    /* DEN NYA DROPDOWNEN (Garanterat ljus & inget tangentbord) */
    .ultra-clean-select {{
        margin-left: 15px;
        background-color: #f2f2f2 !important; /* Ljusgrå bakgrund */
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 8px;
        padding: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        width: 180px;
        outline: none;
    }}

    /* LÄSRUTA (SPIKRAKA TABS) */
    .song-content {{
        margin-top: 80px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }}

    /* STORA KNAPPAR I ARKIVET */
    .big-btn button {{
        height: 60px !important;
        background-color: #f8f8f8 !important;
        border: 1px solid #eee !important;
        font-weight: bold !important;
        color: black !important;
        width: 100% !important;
        border-radius: 12px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# --- RENDERA HEADERN (HTML-METOD) ---
# Vi använder en osynlig Streamlit-knapp för loggan och en selectbox som döljs och styrs via HTML
if logo_b64:
    # Skapa en rad med logga och selectbox
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    
    # Logga som knapp (vi använder st.button med osynlig CSS-placering)
    if st.button(" ", key="home_trigger_final"):
        st.session_state.view = "list"
        st.session_state.song_path = ""
        st.rerun()
    
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img" style="position:absolute; left:10px; top:10px;">', unsafe_allow_html=True)
    
    # Rullistan
    song_titles = ["Välj låt..."] + [s["title"] for s in all_songs]
    # Vi mappar titlar till stigar
    title_to_path = {s["title"]: s["path"] for s in all_songs}
    
    # Här placerar vi Streamlits selectbox men vi har tvingat dess färger i CSS:en ovan
    selected = st.selectbox("", options=song_titles, label_visibility="collapsed")
    
    if selected != "Välj låt...":
        new_path = title_to_path[selected]
        if new_path != st.session_state.song_path:
            st.session_state.song_path = new_path
            st.session_state.view = "song"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:90px;"></div>', unsafe_allow_html=True)
    st.subheader("Arkiv")
    cols = st.columns(2)
    for i, song in enumerate(all_songs):
        with cols[i % 2]:
            st.markdown('<div class="big-btn">', unsafe_allow_html=True)
            if st.button(song["title"], key=f"arch_{song['path']}"):
                st.session_state.song_path = song["path"]
                st.session_state.view = "song"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
else:
    if os.path.exists(st.session_state.song_path):
        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-content">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
