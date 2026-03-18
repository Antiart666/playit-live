import streamlit as st
import os
import re
import base64

# 1. Grundinställningar
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Gör filnamn till snygga titlar."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar bilden säkert."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except:
            return None
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

# --- DESIGN (Stabiliserad layout och Flytande Logga) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STREAMLIT STANDARD */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
    }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
    }}

    /* LOGGAN / HEMKNAPPEN (Super-Stabil) */
    .logo-container {{
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000000;
        width: 120px; /* Låst storlek */
        cursor: pointer;
        transform: rotate(-8deg);
        transition: transform 0.1s;
    }}
    .logo-container:active {{ transform: rotate(-8deg) scale(0.9); }}
    
    .logo-img {{
        width: 100%;
        height: auto;
        display: block;
    }}

    /* MUR SOM STOPPAR BOKSTAVSKAOSET */
    .app-top-spacer {{
        height: 130px; /* Tvingar ner allt innehåll så det aldrig nuddar loggan */
        width: 100%;
        display: block;
    }}

    /* LÄSRUTAN (MAXAD FÖR SCENEN) */
    .song-box-stage {{
        height: 88vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border: 4px solid #000000;
        border-radius: 35px; 
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* ARKIV-KNAPPAR */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 3px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        height: 3.8em !important;
        width: 100% !important;
    }}

    /* VERKTYGSBOX LÄNGST NER */
    .tools-section {{
        margin-top: 50px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "speed" not in st.session_state: st.session_state.speed = 0

# --- LOGGAN SOM HEMKNAPP (Pansarsäker metod) ---
# Vi lägger till ett skript som känner av klick på bilden och laddar om sidan
if logo_b64:
    st.markdown(f"""
        <div class="logo-container" id="home-logo">
            <img src="data:image/png;base64,{logo_b64}" class="logo-img">
        </div>
        <script>
        var logo = window.parent.document.getElementById("home-logo");
        if (logo) {{
            logo.onclick = function() {{
                // Vi skickar användaren till bas-adressen vilket nollställer appen
                window.parent.location.href = window.parent.location.pathname;
            }};
        }}
        </script>
    """, unsafe_allow_html=True)
else:
    st.error("Filen 'logo.png' saknas på GitHub. Ladda upp den!")

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- ARKIVET ---
        st.markdown('<div class="app-top-spacer"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, song_file in enumerate(valid_songs):
                    with cols[idx % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.song_path = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # --- VERKTYG ---
        st.markdown('<div class="tools-section">', unsafe_allow_html=
