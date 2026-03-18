import streamlit as st
import os
import re
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
    """Snyggar till titlar för scenen."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0: return text
    def replace_chord(match):
        chord = match.group(0)
        base = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base):]
        norm = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base in norm: base = norm[base]
        if base in CHORDS:
            idx = (CHORDS.index(base) + steps) % 12
            return CHORDS[idx] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- DESIGN (Större knappar, lutande logga till höger) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-ELEMENT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 1rem !important;
        max-width: 100% !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}

    /* HEMKNAPPEN (Stor och tydlig) */
    div[data-testid="stButton"] > button[key="home_btn"] {{
        width: 140px !important;
        height: 60px !important;
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        color: #000000 !important;
        text-transform: uppercase !important;
        cursor: pointer !important;
        box-shadow: 4px 4px 0px #000000 !important; /* Ger lite 3D-känsla */
    }}

    /* LOGGAN (Lutar +8 grader åt höger) */
    .nav-logo-right {{
        width: 120px !important;
        height: auto !important;
        transform: rotate(8deg); /* Lutning åt andra hållet */
        margin-left: 20px;
        display: inline-block;
        vertical-align: middle;
    }}

    /* LÄSRUTAN (GRÄNSLÖS & TABS-VÄNLIG) */
    .song-view-pro {{
        height: 85vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 5px !important;
        border: none !important; 
        
        /* Courier för monospaced tabs */
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important; 
        line-height: 1.2 !important;
        white-space: pre !important; 
        overflow-x: auto !important;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* VERKTYGSBOX */
    .tools-tray {{
        margin-top: 30px;
        padding: 20px;
        background-color: #fcfcfc;
        border: 2px dashed #000;
        border-radius: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & STATE ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- HEADER (Knapp till vänster, Logga till höger) ---
head_col1, head_col2, head_col3 = st.columns([1.5, 2, 4])

with head_col1:
    if st.button("🏠 HEM", key="home_btn"):
        st.session_state.view = "list"
        st.session_state.song_path = ""
        st.rerun()

with head_col2:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="nav-logo-right">', unsafe_allow_html=True)
    else:
        st.markdown('<div style="margin-top:15px; font-weight:900;">PLAYIT LIVE</div>', unsafe_allow_html=True)

st.markdown("---") # Skiljelinje för att hålla ordning

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # ARKIV
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Alla Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, f in enumerate(valid_files):
                    with cols[i % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song_path = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()

        # VERKTYG
        st.markdown('<div class="tools-tray">', unsafe_allow_html=True)
        st.subheader("⚙️ Verktyg")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            if st.button("-", key="t_m"): st.session_state.transpose -= 1
            if st.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            if st.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if st.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # SCEN (Låten)
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose)
            full_text = content + ("\n" * 60)

            # Auto-scroll
            if st.session_state.scroll > 0:
                delay = (11 - st.session_state.scroll) * 45
                st.markdown(f"""
                    <script>
                    var box = window.parent.document.getElementById("song-view");
                    if (window.playitScroll) clearInterval(window.playitScroll);
                    window.playitScroll = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {delay});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-view-pro">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
