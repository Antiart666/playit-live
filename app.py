import streamlit as st
import os
import re
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

# --- CSS (Den heliga graalen för layouten) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT STANDARD-SKRÄP */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* FIXA TEXTEN */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
    }}

    /* LOGGAN SOM EN RIKTIG KNAPP */
    /* Vi siktar på knappen med key='home_logo' */
    div[data-testid="stButton"] > button[key="home_logo"] {{
        position: fixed !important;
        top: 15px !important;
        left: 20px !important;
        width: 110px !important;
        height: 70px !important;
        z-index: 999999 !important;
        
        background-image: url("data:image/png;base64,{logo_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        
        border: none !important;
        color: transparent !important;
        font-size: 0px !important;
        box-shadow: none !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
        transition: transform 0.1s !important;
    }}
    
    div[data-testid="stButton"] > button[key="home_logo"]:active {{
        transform: rotate(-8deg) scale(0.9) !important;
    }}

    /* MELLANRUM FÖR ATT UNDVIKA KAOS */
    .top-padding {{ height: 110px; }}

    /* LÄSRUTAN (MAXAD) */
    .song-stage {{
        height: 90vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        border: 4px solid #000000;
        border-radius: 35px; 
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* INSTÄLLNINGAR */
    .settings-area {{
        margin-top: 50px;
        padding: 25px;
        background-color: #f9f9f9;
        border: 2px dashed #000;
        border-radius: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. STATE & NAVIGATION ---
if "page" not in st.session_state: st.session_state.page = "list"
if "song" not in st.session_state: st.session_state.song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# LOGGAN (Renderas först så CSS hittar den)
# Vi använder ett osynligt tecken som label
if st.button(" ", key="home_logo"):
    st.session_state.page = "list"
    st.session_state.song = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte på GitHub.")
else:
    if st.session_state.page == "list":
        # --- SIDA 1: ARKIVET ---
        st.markdown('<div class="top-padding"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.song = os.path.join(root, song_file)
                            st.session_state.page = "song"
                            st.rerun()

        # Inställningar längst ner
        st.markdown('<div class="settings-area">', unsafe_allow_html=True)
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
        # --- SIDA 2: LÅTEN ---
        # Lägger till en liten marginal högst upp så rutan inte krockar med loggan
        st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song):
            with open(st.session_state.song, "r", encoding="utf-8") as f:
                text = f.read()
            
            text = transpose_chords(text, st.session_state.transpose)
            full_display = text + ("\n" * 50)

            # SÄKER AUTO-SCROLL (Targetar bara lokalt ID)
            if st.session_state.scroll > 0:
                speed = (11 - st.session_state.scroll) * 40
                st.markdown(f"""
                    <script>
                    var container = document.getElementById("song-view");
                    if (window.scroller) clearInterval(window.scroller);
                    window.scroller = setInterval(function() {{
                        if (container) container.scrollTop += 1;
                    }}, {speed});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-stage">{full_display}</div>', unsafe_allow_html=True)
        else:
            st.session_state.page = "list"
            st.rerun()
