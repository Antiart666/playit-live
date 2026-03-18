import streamlit as st
import os
import base64
import html

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
        except Exception as e:
            print(f"Image load error: {e}")
    return ""

@st.cache_data
def get_all_songs(directory):
    song_list = []

    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".md"):
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, directory)

                    song_list.append({
                        "title": clean_title(f),
                        "path": rel_path
                    })

    return sorted(song_list, key=lambda x: x["title"])

# --- CSS ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
<style>
header, footer, #MainMenu, [data-testid="stHeader"] {{ 
    display: none !important; 
}}

.stApp {{ background-color: #ffffff !important; }}

.block-container {{
    padding: 0 !important;
    max-width: 100% !important;
}}

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

.logo-btn {{
    width: 80px;
    transform: rotate(-8deg);
    cursor: pointer;
    margin-right: 15px;
}}

.select-style {{
    background-color: #eeeeee !important;
    color: #000000 !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 16px;
    width: 220px;
    outline: none;
    font-family: sans-serif;
    -webkit-appearance: none;
}}

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

# 🔒 Whitelist för säkerhet
valid_paths = {s["path"] for s in all_songs}

params = st.query_params
current_s = params.get("s", "")

# --- HEADER ---
options_html = '<option value="">Välj låt...</option>'

for s in all_songs:
    selected = "selected" if s["path"] == current_s else ""
    options_html += f'<option value="{html.escape(s["path"])}" {selected}>{html.escape(s["title"])}</option>'

st.markdown(f"""
<div class="nav-wrapper">
    <a href="/" target="_self">
        <img src="data:image/png;base64,{logo_b64}" class="logo-btn">
    </a>
    <select class="select-style" onchange="window.location.href='/?s=' + this.value">
        {options_html}
    </select>
</div>
""", unsafe_allow_html=True)

# --- INNEHÅLL ---
if current_s and current_s in valid_paths:

    full_path = os.path.join(songs_dir, current_s)

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 🔒 XSS-skydd
        safe_content = html.escape(content)

        st.markdown(
            f'<div class="song-box">{safe_content + ("\\n" * 50)}</div>',
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error("Kunde inte läsa filen.")
        print(f"File read error: {e}")

elif current_s:
    st.error("Ogiltig filväg.")

else:
    st.markdown(
        '<div style="margin-top:100px; text-align:center; color:#ccc;">Välj en låt i menyn ovan för att börja</div>',
        unsafe_allow_html=True
    )
