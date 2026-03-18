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

# --- CSS (STRIP-DOWN & FORCE LIGHT) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    /* Dölj Streamlits standard-UI helt */
    header, footer, #MainMenu, [data-testid="stHeader"] {{ 
        display: none !important; 
    }}
    
    .stApp {{ background-color: #ffffff !important; }}
    
    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    /* FIXED TOP NAV */
    .nav-bar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 65px;
        background: white;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 10px;
        border-bottom: 1px solid #ddd;
    }}

    /* LOGGA SOM HEMKNAPP */
    .logo-anchor {{
        display: block;
        width: 85px;
        transform: rotate(-8deg);
        cursor: pointer;
        margin-right: 15px;
        -webkit-tap-highlight-color: transparent;
    }}

    /* NATIV DROPDOWN (Ingen keyboard-trig, ljus färg) */
    .native-select {{
        background-color: #eeeeee !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 16px;
        width: 200px;
        outline: none;
        font-family: sans-serif;
    }}

    /* LÄSRUTA */
    .song-viewer-final {{
        margin-top: 75px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
        background-color: #ffffff !important;
    }}

    /* ARKIV-LAYOUT */
    .grid-container {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        padding: 85px 15px 30px 15px;
    }}
    .song-link {{
        background: #f5f5f5;
        border: 1px solid #ddd;
        padding: 20px 10px;
        border-radius: 12px;
        text-align: center;
        text-decoration: none;
        color: black !important;
        font-weight: 900;
        font-family: 'Inter', sans-serif;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK OCH NAVIGATION ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)

# Vi använder query_params för att styra appen helt
params = st.query_params
current_song_file = params.get("s", "")

# --- RENDERA HEADERN ---
# Skapa options för rullistan
options_html = '<option value="" disabled {}>Välj låt...</option>'.format('selected' if not current_song_file else '')
for s in all_songs:
    is_selected = 'selected' if s["path"] == current_song_file else ''
    options_html += f'<option value="{s["path"]}" {is_selected}>{s["title"]}</option>'

# Renderar hela nav-raden i ett svep
st.markdown(f"""
<div class="nav-bar">
    <a href="/" target="_self" class="logo-anchor">
        <img src="data:image/png;base64,{logo_b64 if logo_b64 else ''}" style="width:100%;">
    </a>
    <select class="native-select" onchange="window.location.href='/?s=' + this.value">
        {options_html}
    </select>
</div>
""", unsafe_allow_html=True)

# --- RENDERA INNEHÅLL ---
if not current_song_file:
    # --- VY: ARKIV ---
    st.markdown('<div class="grid-container">', unsafe_allow_html=True)
    if all_songs:
        for song in all_songs:
            # Vi skapar en ren länk som laddar om sidan med parametern 's'
            st.markdown(f'<a href="/?s={song["path"]}" target="_self" class="song-link">{song["title"]}</a>', unsafe_allow_html=True)
    else:
        st.write("Inga filer hittades i mappen 'library'.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- VY: LÅT ---
    full_path = os.path.join(songs_dir, current_song_file)
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Lägger till extra rader i botten för att kunna scrolla förbi rullistan
            st.markdown(f'<div class="song-viewer-final">{content + ("\n" * 50)}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Kunde inte läsa filen: {e}")
    else:
        st.error("Låten hittades inte.")
