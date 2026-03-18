import streamlit as st
import os
import base64

# 1. Inställningar
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def get_all_songs():
    songs = []
    if os.path.exists("library"):
        for f in os.listdir("library"):
            if f.endswith(".md"):
                title = f.replace(".md", "").replace("_", " ").strip().capitalize()
                songs.append({"title": title, "path": f})
    return sorted(songs, key=lambda x: x["title"])

# --- SESSION STATE ---
if "active_song" not in st.session_state:
    st.session_state.active_song = ""

# Kolla om URL har ändrats (vår manuella router)
query_params = st.query_params
if "s" in query_params and query_params["s"] != st.session_state.active_song:
    st.session_state.active_song = query_params["s"]

# --- CSS & HEADER ---
logo_data = get_image_base64("logo.png")
songs = get_all_songs()

# Skapa options-sträng för HTML
options_html = "".join([f'<option value="{s["path"]}" {"selected" if s["path"] == st.session_state.active_song else ""}>{s["title"]}</option>' for s in songs])

st.markdown(f"""
<style>
    /* DÖDA ALLT STREAMLIT-UI */
    [data-testid="stHeader"], header, footer, #MainMenu {{ display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    .block-container {{ padding: 0 !important; }}

    /* FAST NAVIGERING */
    .top-nav {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 65px;
        background: white;
        display: flex; align-items: center;
        padding: 0 15px;
        z-index: 999999;
        border-bottom: 1px solid #eee;
    }}

    .logo-link {{
        width: 80px;
        transform: rotate(-8deg);
        margin-right: 20px;
        cursor: pointer;
    }}

    /* DEN RIKTIGA RULLISTAN (Svart/Vit & Keyboard-safe) */
    .song-picker {{
        background-color: #1a1a1a !important;
        color: white !important;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 16px;
        width: 220px;
        outline: none;
        -webkit-appearance: listbox; /* Tvingar fram mobilens hjul-väljare */
    }}

    /* LÄSRUTAN (TABS-SÄKER) */
    .lyrics-container {{
        margin-top: 75px;
        padding: 20px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px;
        line-height: 1.2;
        white-space: pre;
        color: #000;
        background-color: #fff;
    }}
</style>

<div class="top-nav">
    <a href="/" target="_self">
        <img src="data:image/png;base64,{logo_data}" class="logo-link">
    </a>
    <select class="song-picker" onchange="window.location.href='/?s=' + this.value">
        <option value="">Välj låt...</option>
        {options_html}
    </select>
</div>
""", unsafe_allow_html=True)

# --- INNEHÅLL ---
if st.session_state.active_song:
    path = os.path.join("library", st.session_state.active_song)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Vi lägger till massor av rader i botten för att kunna scrolla fritt
        st.markdown(f'<div class="lyrics-container">{content}{chr(10)*60}</div>', unsafe_allow_html=True)
    else:
        st.error("Låten hittades inte.")
else:
    # Startsidan - helt ren
    st.markdown('<div style="height:150px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#999; font-family:sans-serif;">Välj låt i menyn ovan för att börja giget.</div>', unsafe_allow_html=True)
