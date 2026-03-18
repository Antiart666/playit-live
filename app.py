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

# --- CSS (TOTAL ISOLATION - NO KEYBOARD, NO GHOST ELEMENTS) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Roboto+Mono&display=swap');

    /* DÖLJ STREAMLIT-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    [data-testid="stHeader"] {{ display: none !important; }}
    
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* FIXED HEADER RAD */
    .custom-nav {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 65px;
        background: #ffffff;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding-left: 10px;
    }}

    /* LOGGAN (HEM-LÄNK) */
    .nav-logo {{
        width: 85px;
        transform: rotate(-8deg);
        cursor: pointer;
        margin-right: 15px;
        filter: drop-shadow(2px 2px 3px rgba(0,0,0,0.1));
        transition: transform 0.2s;
    }}
    .nav-logo:active {{ transform: scale(0.95) rotate(-8deg); }}

    /* HTML DROPDOWN (LJUS & TANGENTBORDSFRI) */
    .native-drop {{
        background-color: #f2f2f2 !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 8px;
        padding: 8px 12px;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        width: 200px;
        outline: none;
        -webkit-appearance: none; /* Tar bort mobilens standard-styling */
    }}

    /* LÄSRUTA (SPIKRAKA TABS) */
    .song-stage {{
        margin-top: 75px;
        padding: 10px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }}
    
    /* GÖM STREAMLITS EGNA ELEMENT HELT */
    div[data-testid="stVerticalBlock"] > div:first-child {{
        margin-top: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

# Hantera URL-parametrar för att byta låt utan att trigga tangentbord via Streamlit-widgets
query_params = st.query_params
if "song" in query_params:
    st.session_state.song_path = urllib.parse.unquote(query_params["song"])
    st.session_state.view = "song"

if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""

# --- RENDERA HEADERN MED REN HTML ---
options_html = "".join([f'<option value="{urllib.parse.quote(s["path"])}" {"selected" if s["path"] == st.session_state.song_path else ""}>{s["title"]}</option>' for s in all_songs])

header_html = f"""
<div class="custom-nav">
    <a href="/?view=list" target="_self">
        <img src="data:image/png;base64,{logo_b64 if logo_b64 else ''}" class="nav-logo">
    </a>
    <select class="native-drop" onchange="window.location.href='/?song=' + this.value">
        <option value="" disabled {"selected" if not st.session_state.song_path else ""}>Välj låt...</option>
        {options_html}
    </select>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Hem-logik via URL
if query_params.get("view") == "list":
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.query_params.clear()
    st.rerun()

# --- INNEHÅLL ---
if st.session_state.view == "list":
    st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
    st.subheader("Mina Låtar")
    if all_songs:
        cols = st.columns(2)
        for i, song in enumerate(all_songs):
            with cols[i % 2]:
                # Vi använder vanliga länkar här med för att vara konsekventa
                url = f"/?song={urllib.parse.quote(song['path'])}"
                st.markdown(f'<a href="{url}" target="_self" style="text-decoration:none;"><div style="border:1px solid #eee; padding:15px; border-radius:10px; text-align:center; color:black; font-weight:bold; margin-bottom:10px; background:#f9f9f9;">{song["title"]}</div></a>', unsafe_allow_html=True)
else:
    if os.path.exists(st.session_state.song_path):
        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-stage">{content + ("\n"*60)}</div>', unsafe_allow_html=True)
