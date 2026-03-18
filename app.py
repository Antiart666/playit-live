import streamlit as st
import os
import base64
import html

# 1. Grundkonfiguration
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
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return ""
    return ""

@st.cache_data
def get_all_songs(directory):
    song_list = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.endswith(".md"):
                    rel_path = os.path.relpath(os.path.join(root, f), directory)
                    title = f.replace(".md", "").replace("_", " ").strip().capitalize()
                    song_list.append({"title": title, "path": rel_path})
    return sorted(song_list, key=lambda x: x["title"])

# --- CSS & JAVASCRIPT ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
<style>
    /* Dölj Streamlit standard */
    header, footer, #MainMenu, [data-testid="stHeader"] {{ display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    .block-container {{ padding: 0 !important; max-width: 100% !important; }}

    /* NAVBAR */
    .nav-bar {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 60px;
        background: white; z-index: 999999;
        display: flex; align-items: center; padding-left: 10px;
        border-bottom: 1px solid #eee;
    }}

    .logo-img {{
        width: 80px; transform: rotate(-8deg);
        cursor: pointer; margin-right: 15px;
    }}

    /* DROPDOWN (Native HTML - Triggerar mobilens rullhjul) */
    .song-select {{
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        border: 1px solid #ccc !important;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 16px;
        width: 200px;
        outline: none;
        -webkit-appearance: menulist; /* Tvingar fram dropdown-pilen */
    }}

    /* LÄSRUTA */
    .song-display {{
        margin-top: 70px;
        padding: 15px;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
        color: #000 !important;
    }}
</style>

<script>
    // Funktion för att byta låt och tvinga omladdning
    function changeSong(path) {{
        if (path) {{
            const url = new URL(window.location.href);
            url.searchParams.set('s', path);
            window.location.href = url.href;
        }} else {{
            window.location.href = '/';
        }}
    }}
</script>
""", unsafe_allow_html=True)

# --- LOGIK ---
songs_dir = "library"
all_songs = get_all_songs(songs_dir)
valid_paths = {s["path"] for s in all_songs}

params = st.query_params
current_s = params.get("s", "")

# --- RENDER HEADER ---
options_html = f'<option value="" {"selected" if not current_s else ""}>Välj låt...</option>'
for s in all_songs:
    is_sel = 'selected' if s["path"] == current_s else ''
    options_html += f'<option value="{html.escape(s["path"])}" {is_sel}>{html.escape(s["title"])}</option>'

st.markdown(f"""
<div class="nav-bar">
    <a href="/" target="_self">
        <img src="data:image/png;base64,{logo_b64}" class="logo-img">
    </a>
    <select class="song-select" onchange="changeSong(this.value)">
        {options_html}
    </select>
</div>
""", unsafe_allow_html=True)

# --- RENDER INNEHÅLL ---
if current_s and current_s in valid_paths:
    full_path = os.path.join(songs_dir, current_s)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        safe_content = html.escape(content)
        st.markdown(f'<div class="song-display">{safe_content + ("\\n" * 60)}</div>', unsafe_allow_html=True)
    except:
        st.error("Kunde inte ladda låten.")
else:
    st.markdown('<div style="margin-top:100px; text-align:center; color:#ccc; font-family:sans-serif;">Välj en låt i menyn ovan</div>', unsafe_allow_html=True)
