import streamlit as st
import os
import re
import base64

# 1. Grundinställningar - Tvinga fram en ren, ljus layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Gör om filnamn till snygga titlar."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Kodar bilden så den kan användas i CSS."""
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
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

# --- DESIGN (Inter-font, rundade hörn och logga-knapp) ---
logo_b64 = get_image_base64("logo.png")

# Här bygger vi den magiska CSS-koden
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STREAMLITS STANDARD-LAYOUT */
    header, footer, #MainMenu {{ visibility: hidden !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GÖR ALL TEXT SVART */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif; }}

    /* FLYTTA NER INNEHÅLLET SÅ LOGGAN FÅR PLATS */
    .block-container {{
        padding-top: 5rem !important;
        max-width: 98% !important;
    }}

    /* MAGISK LOGGA-KNAPP (Vi gör den första knappen till din logga) */
    div[data-testid="stButton"]:first-child button {{
        position: fixed !important;
        top: 15px !important;
        left: 20px !important;
        width: 100px !important;
        height: 60px !important;
        z-index: 10000 !important;
        
        /* Här lägger vi in din bild som bakgrund på knappen */
        background-image: url("data:image/png;base64,{logo_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        
        /* Ta bort all standard-look */
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}
    
    /* Ta bort hovringseffekter på loggan */
    div[data-testid="stButton"]:first-child button:hover,
    div[data-testid="stButton"]:first-child button:active {{
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        transform: rotate(-4deg) scale(1.05) !important;
    }}

    /* LÄSRUTAN (STAGE MODE) */
    .song-box {{
        height: 85vh;
        overflow-y: auto;
        background: #ffffff;
        border: 3px solid #000;
        border-radius: 30px;
        padding: 25px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 17px;
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* VANLIGA KNAPPAR I ARKIVET */
    div[data-testid="stButton"] button {{
        background: #ffffff !important;
        border: 2px solid #000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }}

    /* VERKTYGSBOXEN LÄNGST NER */
    .tools-area {{
        background: #fcfcfc;
        border: 2px dashed #000;
        border-radius: 25px;
        padding: 20px;
        margin-top: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State & Navigation
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "speed" not in st.session_state: st.session_state.speed = 0

# --- DEN MAGISKA HEMKNAPPEN ---
# Denna måste ligga först i koden för att CSS-väljaren (:first-child) ska hitta den
if st.button(" ", key="home_logo_btn"):
    st.session_state.view = "list"
    st.rerun()

songs_dir = "library"

# 3. Rendering
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas på GitHub.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.header("Arkiv")
        
        # Hämta alla låtar
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Alla låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.write(f"**{category.upper()}**")
                cols = st.columns(2)
                for idx, f in enumerate(valid_files):
                    with cols[idx % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song_path = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()

        # --- VERKTYG LÄNGST NER ---
        st.markdown('<div class="tools-area">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Tonart")
            t_col1, t_col2 = st.columns(2)
            if t_col1.button("- Ton"): st.session_state.transpose -= 1
            if t_col2.button("+ Ton"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("Scroll")
            s_col1, s_col2 = st.columns(2)
            if s_col1.button("Sakta"): st.session_state.speed = max(0, st.session_state.speed - 1)
            if s_col2.button("Fort"): st.session_state.speed = min(10, st.session_state.speed + 1)
            st.write(f"Fart: {st.session_state.speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET ---
        # "Dold" knapp som bara syns vid dubbelklick
        if st.button("← ARKIV", key="manual_back_btn"):
            st.session_state.view = "list"
            st.rerun()

        with open(st.session_state.song_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose)
        display_text = content + ("\n" * 50)

        # JavaScript för Dubbelklick & Scroll (Säkrad för mobiler)
        st.markdown(f"""
            <script>
            // Hitta tillbaka-knappen och dölj den
            var btns = window.parent.document.querySelectorAll('div[data-testid="stButton"]');
            var backBtn = Array.from(btns).find(b => b.innerText.includes("ARKIV"));
            if (backBtn) backBtn.style.display = 'none';

            // Visa vid dubbelklick
            window.parent.document.addEventListener('dblclick', function() {{
                if (backBtn) backBtn.style.display = (backBtn.style.display === 'none') ? 'block' : 'none';
            }});

            // Scroll-logik
            var container = window.parent.document.getElementById("song-rutan-id");
            if (window.playitScroll) clearInterval(window.playitScroll);
            if ({st.session_state.speed} > 0) {{
                var delay = (11 - {st.session_state.speed}) * 40;
                window.playitScroll = setInterval(function() {{
                    if (container) container.scrollTop += 1;
                }}, delay);
            }}
            </script>
        """, unsafe_allow_html=True)

        st.markdown(f'<div id="song-rutan-id" class="song-box">{display_text}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
