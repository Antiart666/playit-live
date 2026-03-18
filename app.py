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

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan och gör om till kod. Kraschar inte om filen saknas."""
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

# --- CSS (Den här gången sitter den!) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ STANDARD-STRECK OCH MENYER */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* FIXA TEXTEN */
    * {{ color: #000000 !important; font-family: 'Inter', sans-serif !important; }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
    }}

    /* POSITIONERING AV LOGGA-BEHÅLLAREN */
    .logo-anchor {{
        position: fixed;
        top: 15px;
        left: 20px;
        z-index: 1000000;
    }}

    /* LOGGAN SOM EN RIKTIG KNAPP (Klädd i din bild) */
    .logo-anchor button {{
        width: 110px !important; /* Storleken du ville ha */
        height: 65px !important;
        background-image: url("data:image/png;base64,{logo_b64 if logo_b64 else ''}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-color: transparent !important;
        border: none !important;
        color: transparent !important;
        box-shadow: none !important;
        transform: rotate(-8deg) !important;
        cursor: pointer !important;
        padding: 0 !important;
    }}
    
    .logo-anchor button:active {{
        transform: rotate(-8deg) scale(0.9) !important;
    }}

    /* SKYDD MOT BOKSTAVSKAOS */
    .top-spacer {{
        height: 110px; /* Skapar en mur så texten inte kan hoppa upp */
        width: 100%;
    }}

    /* LÄSRUTAN (MAXAD) */
    .song-box {{
        height: 88vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        border: 4px solid #000000;
        border-radius: 35px; 
        padding: 25px;
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* KNAPPAR I LISTAN */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        border: 3px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State & Navigation
if "page" not in st.session_state: st.session_state.page = "list"
if "song" not in st.session_state: st.session_state.song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- LOGGAN (HÖGST UPP I KODEN) ---
st.markdown('<div class="logo-anchor">', unsafe_allow_html=True)
if st.button(" ", key="home_logo"):
    st.session_state.page = "list"
    st.session_state.song = ""
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Om loggan saknas på GitHub, visa en liten varning så vi vet
if not logo_b64:
    st.warning("⚠️ Hittade inte 'logo.png' på GitHub. Kontrollera filnamnet!")

songs_dir = "library"

# --- 3. RENDERING ---

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte.")
else:
    if st.session_state.page == "list":
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
                            st.session_state.song = os.path.join(root, song_file)
                            st.session_state.page = "song"
                            st.rerun()

        # Inställningar
        st.markdown('<div style="margin-top:50px; padding:20px; background:#f9f9f9; border:2px dashed #000; border-radius:25px;">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
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
        # Lägger till ett litet mellanrum så rutan inte krockar med loggan
        st.markdown('<div style="height:75px;"></div>', unsafe_allow_html=True)
        
        if os.path.exists(st.session_state.song):
            with open(st.session_state.song, "r", encoding="utf-8") as f:
                text = f.read()
            
            text = transpose_chords(text, st.session_state.transpose)
            full_display = text + ("\n" * 50)

            # Auto-scroll
            if st.session_state.scroll > 0:
                speed = (11 - st.session_state.scroll) * 45
                st.markdown(f"""
                    <script>
                    var box = document.getElementById("song-view");
                    if (window.scroller) clearInterval(window.scroller);
                    window.scroller = setInterval(function() {{
                        if (box) box.scrollTop += 1;
                    }}, {speed});
                    </script>
                """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view" class="song-box">{full_display}</div>', unsafe_allow_html=True)
