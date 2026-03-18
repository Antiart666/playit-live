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
                    song_list.append({"title": clean_title(f), "path": f})
    return sorted(song_list, key=lambda x: x["title"])

# --- CSS (HARDCORE CLEANUP) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    /* DÖLJ ALLT FRÅN STREAMLIT */
    header, footer, #MainMenu, [data-testid="stHeader"] {{ 
        display: none !important; 
        visibility: hidden !important; 
    }}
    
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* DEN RIKTIGA HEADERN */
    .custom-header {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: white;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 10px;
        border-bottom: 1px solid #eee;
    }}

    /* LOGGAN SOM LÄNK */
    .logo-link {{
        width: 80px;
        transform: rotate(-8deg);
        cursor: pointer;
        margin-right: 15px;
    }}

    /* HTML-DROPDOWN (INGET TANGENTBORD, LJUS FÄRG) */
    .html-select {{
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 16px;
        width: 180px;
        outline: none;
        -webkit-appearance: none; /* Viktigt för iPhone/Android */
    }}

    /* LÄSRUTAN */
    .song-viewer {{
        margin-top: 70px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }}

    /* ARKIVVYN */
    .archive-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        padding: 80px 10px 20px 10px;
    }}
    .song-card {{
        background: #f8f8f8;
        border: 1px solid #eee;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        text-decoration: none;
        color: black;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

# Hantera val via URL-parameter (för att slippa Streamlit-widgets i toppen)
params = st.query_params
current_song = params.get("song", "")

# --- RENDERA HEADERN (REN HTML) ---
options = "".join([f'<option value="{s["path"]}" {"selected" if s["path"] == current_song else ""}>{s["title"]}</option>' for s in all_songs])

header_code = f"""
<div class="custom-header">
    <a href="/?song=" target="_self">
        <img src="data:image/png;base64,{logo_b64 if logo_b64 else ''}" class="logo-link">
    </a>
    <select class="html-select" onchange="window.location.href='/?song=' + this.value">
        <option value="" { 'selected' if not current_song else '' }>Välj låt...</option>
        {options}
    </select>
</div>
"""
st.markdown(header_code, unsafe_allow_html=True)

# --- INNEHÅLL ---
if not current_song:
    # Visa Arkivet
    st.markdown('<div class="archive-grid">', unsafe_allow_html=True)
    for song in all_songs:
        link = f"/?song={song['path']}"
        st.markdown(f'<a href="{link}" target="_self" class="song-card">{song["title"]}</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Visa Låten
    song_full_path = os.path.join(songs_dir, current_song)
    if os.path.exists(song_full_path):
        with open(song_full_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-viewer">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
