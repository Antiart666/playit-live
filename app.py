import streamlit as st
import os
import re
import base64

# 1. Grundinställningar - Enkel och stabil layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Snyggar till titeln på låten."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan."""
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

# --- DESIGN (Tvingar fram ordning och reda) ---
logo_b64 = get_image_base64("logo.png")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-LAYOUT */
    header, footer, #MainMenu { visibility: hidden !important; display: none !important; }
    
    /* TVINGA VIT BAKGRUND */
    .stApp { background-color: #ffffff !important; }
    
    /* FIXA TEXTEN */
    * { color: #000000 !important; font-family: 'Inter', sans-serif !important; }

    .block-container {
        padding-top: 1rem !important;
        max-width: 98% !important;
    }

    /* LOGGA-STYLING */
    .logo-img {
        width: 100px;
        transform: rotate(-8deg);
        border: 2px solid #000;
        border-radius: 12px;
        background: #000;
    }

    /* LÄSRUTAN */
    .song-stage {
        height: 80vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        border: 3px solid #000000;
        border-radius: 25px; 
        padding: 20px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* KNAPPAR */
    .stButton > button {
        background-color: #ffffff !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAVIGATION & HEADER ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song" not in st.session_state: st.session_state.song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# Vi skapar en stabil Header-rad
head_col1, head_col2 = st.columns([1, 3])

with head_col1:
    # Denna knapp tar dig alltid hem
    if st.button("🏠 HEM"):
        st.session_state.view = "list"
        st.session_state.song = ""
        st.rerun()

with head_col2:
    # Visar loggan om den finns
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-img">', unsafe_allow_html=True)
    else:
        st.write("🎸 **PLAYIT LIVE**")

st.write("---") # En linje som separerar header från innehåll

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.subheader("Mina Låtar")
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Alla"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                st.markdown(f"**{category.upper()}**")
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.song = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # Verktyg längst ner
        st.write("---")
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            if st.button("-"): st.session_state.transpose -= 1
            if st.button("+"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            if st.button("Saktare"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if st.button("Snabbare"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")

    else:
        # --- SIDA 2: LÅTEN ---
        if os.path.exists(st.session_state.song):
            with open(st.session_state.song, "r", encoding="utf-8") as f:
                text = f.read()
            
            text = transpose_chords(text, st.session_state.transpose)
            full_display = text + ("\n" * 50)

            # Enkel och stabil auto-scroll
            if st.session_state.scroll > 0:
                speed = (11 - st.session_state.scroll) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-rutan");
                    if (window.scroller) clearInterval(window.scroller);
                    window.scroller = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {speed});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-rutan" class="song-stage">{full_display}</div>', unsafe_allow_html=True)
