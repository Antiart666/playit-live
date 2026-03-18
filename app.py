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

# --- CSS (RENODLAD HEADER & INGET KLADD) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    /* Dölj Streamlits standard-UI */
    header, footer, #MainMenu, [data-testid="stHeader"] {{ 
        display: none !important; 
    }}
    
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* HEADER-RADEN */
    .nav-wrapper {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        background: white;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding-left: 10px;
        border-bottom: 1px solid #f0f0f0;
    }}

    /* LOGGAN */
    .logo-btn {{
        width: 80px;
        transform: rotate(-8deg);
        cursor: pointer;
        margin-right: 15px;
        display: block;
    }}

    /* NATIV DROPDOWN (Ljusgrå, Ingen keyboard) */
    .select-style {{
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 16px;
        width: 200px;
        outline: none;
        font-family: sans-serif;
        -webkit-appearance: none; /* Fixar mobil-look */
    }}

    /* LÄSYTA */
    .song-box {{
        margin-top: 70px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.15 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)
params = st.query_params
current_s = params.get("s", "")

# --- RENDERA HEADERN ---
options_html = f'<option value="" {"selected" if not current_s else ""}>Välj låt...</option>'
for s in all_songs:
    sel = 'selected' if s["path"] == current_s else ''
    options_html += f'<option value="{s["path"]}" {sel}>{s["title"]}</option>'

st.markdown(f"""
<div class="nav-wrapper">
    <a href="/" target="_self">
        <img src="data:image/png;base64,{logo_b64 if logo_b64 else ''}" class="logo-btn">
    </a>
    <select class="select-style" onchange="window.location.href='/?s=' + this.value">
        {options_html}
    </select>
</div>
""", unsafe_allow_html=True)

# --- RENDERA INNEHÅLL ---
if current_s:
    full_path = os.path.join(songs_dir, current_s)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.markdown(f'<div class="song-box">{content + ("\n" * 55)}</div>', unsafe_allow_html=True)
    else:
        st.error("Filen hittades inte.")
else:
    # Startsidan är nu helt ren förutom headern
    st.markdown('<div style="margin-top:100px; text-align:center; color:#ccc;">Välj en låt i menyn ovan för att börja</div>', unsafe_allow_html=True)
