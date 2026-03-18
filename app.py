import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Tvinga fram en ren och stabil layout
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Gör filnamn till snygg text."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert för inbäddning."""
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

# --- DESIGN (Vitt tema, Maximerad yta, Logga som knapp) ---
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
        text-transform: none !important;
    }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* ANIMATION: SVÄVANDE LOGGA */
    @keyframes floating {{
        0% {{ transform: rotate(-8deg) translateY(0px); }}
        50% {{ transform: rotate(-8deg) translateY(-5px); }}
        100% {{ transform: rotate(-8deg) translateY(0px); }}
    }}

    /* LOGGAN SOM EN RIKTIG KNAPP (Pansarsäker metod) */
    div[data-testid="stButton"] > button[key="logo_home_btn"] {{
        position: fixed !important;
        top: 15px !important;
        left: 20px !important;
        width: 110px !important;
        height: 70px !important;
        z-index: 999999 !important;
        
        /* Loggan som bakgrund */
        background-image: url("data:image/png;base64,{logo_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        cursor: pointer !important;
        
        animation: floating 3s ease-in-out infinite !important;
        transition: transform 0.1s ease-in-out !important;
    }}
    
    /* REAKTION VID KLICK */
    div[data-testid="stButton"] > button[key="logo_home_btn"]:active {{
        transform: rotate(-8deg) scale(0.9) !important;
        animation: none !important;
    }}

    /* LÄSRUTAN (MAXIMERAD FÖR SCENEN) */
    .song-stage-box {{
        height: 90vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px;
        border: 3px solid #000000;
        border-radius: 35px; 
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
        margin-top: 10px;
    }}

    /* KNAPPAR I LISTAN */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 18px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* VERKTYGSBOX */
    .settings-panel {{
        margin-top: 40px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}

    /* MELLANRUM FÖR ATT UNDVIKA LOGGAN I ARKIVET */
    .top-spacer {{
        height: 95px;
        width: 100%;
        display: block;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song" not in st.session_state: st.session_state.current_song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGAN (DEN ENDA VÄGEN HEM) ---
# Denna ligger först så CSS-väljaren hittar den och klär ut den till loggan
if st.button(" ", key="logo_home_btn"):
    st.session_state.view = "list"
    st.session_state.current_song = ""
    st.rerun()

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.markdown('<div class="top-spacer"></div>', unsafe_allow_html=True)
        
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
                            st.session_state.current_song = os.path.join(root, song_file)
                            st.session_state.view = "song"
                            st.rerun()

        # Verktyg längst ner på arkivsidan
        st.markdown('<div class="settings-panel">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            t_m, t_p = st.columns(2)
            if t_m.button("-", key="t_m"): st.session_state.transpose -= 1
            if t_p.button("+", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            s_m, s_p = st.columns(2)
            if s_m.button("Sakta", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_p.button("Fort", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        # Läsrutan börjar högt upp för att loggan ska "flyta" snyggt i hörnet
        st.markdown('<div style="height:65px;"></div>', unsafe_allow_html=True)

        if os.path.exists(st.session_state.current_song):
            with open(st.session_state.current_song, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            content = transpose_chords(raw_text, st.session_state.transpose)
            display_text = content + ("\n" * 55)

            # Auto-scroll
            st.markdown(f"""
                <script>
                var box = window.parent.document.getElementById("song-stage-id");
                if (window.playitScroll) clearInterval(window.playitScroll);
                if ({st.session_state.scroll} > 0) {{
                    var speed = (11 - {st.session_state.scroll}) * 40;
                    window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
                }}
                </script>
            """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-stage-id" class="song-stage-box">{display_text}</div>', unsafe_allow_html=True)
