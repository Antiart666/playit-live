import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Maximerad yta från start
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER ---

def clean_title(filename):
    """Gör filnamn snygga för listan."""
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

# --- CSS (Ghost & Overlay Metoden) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT FRÅN STREAMLIT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXT */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}

    /* 1. LOGGAN (DEN SOM SYNS) */
    .logo-overlay {{
        position: fixed !important;
        top: 20px !important;
        left: 20px !important;
        width: 110px !important; /* Din önskade storlek */
        height: auto !important;
        z-index: 999998 !important;
        pointer-events: none !important; /* GÖR ATT KLICK GÅR IGENOM BILDEN */
    }}

    /* 2. SPÖKKNAPPEN (DEN SOM FUNGERAR) */
    div[data-testid="stButton"] > button[key="ghost_home_btn"] {{
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        width: 130px !important;
        height: 85px !important;
        z-index: 999999 !important;
        opacity: 0 !important; /* HELT OSYNLIG */
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}

    /* SKYDDSVÄGG MOT BOKSTAVSKAOS */
    .top-barrier {{
        height: 110px;
        display: block;
    }}

    /* LÄSRUTAN (GRÄNSLÖS & TABS-VÄNLIG) */
    .song-display-area {{
        height: 92vh !important; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 5px !important;
        border: none !important; /* INGA KANTER SOM BEGÄRT */
        
        /* Courier för monospaced tabs */
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 14px !important; /* Mindre text för att motverka taggighet */
        line-height: 1.2 !important;
        white-space: pre !important; /* Viktigt: Behåller tabs raka */
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
        margin: 40px 10px;
        padding: 25px;
        background-color: #fcfcfc;
        border: 2px dashed #000;
        border-radius: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIK & NAVIGATION ---
if "view" not in st.session_state: st.session_state.view = "list"
if "song_path" not in st.session_state: st.session_state.song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# RITA LOGGAN (Bild-lagret)
if logo_b64:
    st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="logo-overlay">', unsafe_allow_html=True)
else:
    # Om bilden saknas, visa en nödlösning så du kan navigera
    st.markdown('<div class="logo-overlay" style="color:red; font-weight:900;">LOGGA SAKNAS</div>', unsafe_allow_html=True)

# RITA SPÖKKNAPPEN (Funktions-lagret)
if st.button(" ", key="ghost_home_btn"):
    st.session_state.view = "list"
    st.session_state.song_path = ""
    st.rerun()

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte.")
else:
    if st.session_state.view == "list":
        # ARKIV
        st.markdown('<div class="top-barrier"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
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
        st.markdown('<div style="height:70px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song_path):
            with open(st.session_state.song_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose)
            full_text = content + ("\n" * 60)

            # Auto-scroll (Lokaliserad fix)
            if st.session_state.scroll > 0:
                delay = (11 - st.session_state.scroll) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-view");
                    if (window.playitScroll) clearInterval(window.playitScroll);
                    window.playitScroll = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {delay});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-display-area">{full_text}</div>', unsafe_allow_html=True)
        else:
            st.session_state.view = "list"
            st.rerun()
