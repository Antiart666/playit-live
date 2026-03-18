import streamlit as st
import os
import re
import base64

# 1. Grundinställningar - Tvinga fram en stabil och ljus layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Snyggar till filnamn för visning."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert."""
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

# --- DESIGN (Stabiliserad pixel-layout) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT FRÅN STREAMLIT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXTSTIL */
    * {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
    }}

    /* HUVUDCONTAINER */
    .block-container {{
        padding-top: 1rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* LOGGAN / HEMKNAPPEN (Pixel-låst design) */
    div[data-testid="stButton"] > button[key="logo_home_btn"] {{
        position: fixed !important;
        top: 15px !important;
        left: 20px !important;
        width: 125px !important; /* Låst storlek */
        height: 75px !important; /* Låst storlek */
        z-index: 999999 !important;
        
        /* Loggan som bakgrund */
        background-image: url("data:image/png;base64,{logo_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        
        /* Rensa bort all knapp-grafik och text */
        border: none !important;
        color: transparent !important;
        font-size: 0px !important;
        box-shadow: none !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
    }}
    
    div[data-testid="stButton"] > button[key="logo_home_btn"]:active {{
        transform: rotate(-8deg) scale(0.9) !important;
    }}

    /* SKYDDSZON - STOPPAR BOKSTAVSKAOSET */
    .app-spacer {{
        height: 120px; /* Tvingar ner allt innehåll 120px från toppen */
        width: 100%;
        display: block;
    }}

    /* LÄSRUTAN (MAXAD) */
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
        height: 3.5em !important;
        width: 100% !important;
        text-transform: none !important;
    }}

    /* VERKTYGSBOX */
    .tools-panel {{
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

# --- HEMKNAPPEN (Dold i loggan) ---
# Måste ligga först så CSS hittar den
if st.button("H", key="logo_home_btn"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()

# 3. App-logik
# Lägg till spacer för att undvika kaoset högst upp
st.markdown('<div class="app-spacer"></div>', unsafe_allow_html=True)

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_files = sorted([f for f in files if f.endswith(".md")])
            if valid_files:
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, f in enumerate(valid_files):
                    with cols[idx % 2]:
                        if st.button(clean_title(f), key=os.path.join(root, f)):
                            st.session_state.song_path = os.path.join(root, f)
                            st.session_state.view = "song"
                            st.rerun()

        # --- VERKTYG LÄNGST NER ---
        st.markdown('<div class="tools-panel">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            t1, t2 = st.columns(2)
            if t1.button("-", key="t_m"): st.session_state.transpose -= 1
            if t2.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            s1, s2 = st.columns(2)
            if s1.button("Sakta", key="s_m"): st.session_state.speed = max(0, st.session_state.speed - 1)
            if s2.button("Fort", key="s_p"): st.session_state.speed = min(10, st.session_state.speed + 1)
            st.write(f"Fart: {st.session_state.speed}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        # Läsrutan tar över skärmen
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            content = transpose_chords(raw_text, st.session_state.transpose)
            display_text = content + ("\n" * 55)

            # Säkrad auto-scroll för mobil
            st.markdown(f"""
                <script>
                var box = window.parent.document.getElementById("song-view-id");
                if (window.playitScroll) clearInterval(window.playitScroll);
                if ({st.session_state.speed} > 0) {{
                    var speed = (11 - {st.session_state.speed}) * 40;
                    window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
                }}
                </script>
            """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view-id" class="song-box-stage">{display_text}</div>', unsafe_allow_html=True)
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
        
