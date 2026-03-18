import streamlit as st
import os
import base64
import urllib.parse

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
    path = "library"
    if os.path.exists(path):
        for f in os.listdir(path):
            if f.endswith(".md"):
                title = f.replace(".md", "").replace("_", " ").strip().capitalize()
                songs.append({"title": title, "filename": f})
    return sorted(songs, key=lambda x: x["title"])

# --- SESSION STATE & URL LOGIK ---
songs = get_all_songs()
query_params = st.query_params
current_song_file = query_params.get("s", "")

# --- CSS (TOTAL KONTROLL) ---
logo_data = get_image_base64("logo.png")

st.markdown(f"""
<style>
    /* Dölj allt Streamlit-standard */
    [data-testid="stHeader"], header, footer, #MainMenu {{ display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* FAST NAVIGERINGSRAD */
    .custom-header {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 70px;
        background: #ffffff;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 10px;
        z-index: 1000000;
        border-bottom: 2px solid #f0f0f0;
        box-sizing: border-box;
    }}

    .nav-left {{ display: flex; align-items: center; }}
    
    .logo-img {{
        width: 70px;
        transform: rotate(-8deg);
        margin-right: 10px;
    }}

    /* HTML DROPDOWN (Tangentbordssäkert) */
    .native-drop {{
        background-color: #1a1a1a;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        width: 160px;
        outline: none;
    }}

    /* EXIT KNAPP */
    .exit-btn {{
        background-color: #ff4b4b;
        color: white !important;
        padding: 10px 15px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 14px;
    }}

    /* LÅT-TEXT */
    .lyrics-container {{
        margin-top: 85px;
        padding: 20px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px;
        line-height: 1.2;
        white-space: pre;
        overflow-x: auto;
        color: #000;
        background-color: #fff;
    }}

    /* ARKIV-KNAPPAR */
    .archive-list {{
        margin-top: 90px;
        padding: 20px;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }}
    .song-card {{
        background: #f8f8f8;
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        text-decoration: none;
        color: black;
        font-weight: bold;
        font-family: sans-serif;
    }}
</style>
""", unsafe_allow_html=True)

# --- RENDERA HEADER (REN HTML) ---
options_html = "".join([f'<option value="{s["filename"]}" {"selected" if s["filename"] == current_song_file else ""}>{s["title"]}</option>' for s in songs])

header_html = f"""
<div class="custom-header">
    <div class="nav-left">
        <a href="/" target="_self">
            <img src="data:image/png;base64,{logo_data}" class="logo-img">
        </a>
        <select class="native-drop" onchange="window.location.href='/?s=' + this.value">
            <option value="" {"selected" if not current_song_file else ""}>Välj låt...</option>
            {options_html}
        </select>
    </div>
    <a href="/" target="_self" class="exit-btn">EXIT</a>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# --- INNEHÅLL ---
if current_song_file:
    # VISA LÅT
    file_path = os.path.join("library", current_song_file)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="lyrics-container">{content}{chr(10)*60}</div>', unsafe_allow_html=True)
    else:
        st.error("Filen saknas.")
else:
    # VISA ARKIV
    st.markdown('<div class="archive-list">', unsafe_allow_html=True)
    for s in songs:
        st.markdown(f'<a href="/?s={s["filename"]}" target="_self" class="song-card">{s["title"]}</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
