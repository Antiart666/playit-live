import streamlit as st
import os
import re

# 1. Grundinställningar - Modernt och avskalat
st.set_page_config(
    page_title="PlayIt Live",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TRANSPONERINGSLOGIK ---
CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0: return text
    def replace_chord(match):
        chord = match.group(0)
        base_chord = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base_chord):]
        norm_map = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base_chord in norm_map: base_chord = norm_map[base_chord]
        if base_chord in CHORDS:
            new_index = (CHORDS.index(base_chord) + steps) % 12
            return CHORDS[new_index] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- DESIGN (Inter-typsnitt, vita knappar, svarta kanter) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* Global stil med Inter-typsnitt */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    .stApp {
        background-color: #ffffff !important;
    }

    /* Snedställd logga uppe till vänster (Vault-stil) */
    .logo-container {
        position: absolute;
        top: 0px;
        left: 20px;
        z-index: 1000;
        transform: rotate(-12deg);
        background: #000000;
        padding: 10px 20px;
        border: 2px solid #000000;
    }
    
    .logo-text {
        color: #ffffff;
        font-weight: 900;
        font-size: 24px;
        letter-spacing: -1px;
        text-transform: uppercase;
    }

    /* Låt-behållaren */
    .song-container {
        height: 70vh;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 30px;
        border: 3px solid #000000;
        margin-top: 20px;
        font-family: 'Courier New', Courier, monospace; /* Behåll monospace för tabs */
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
    }

    /* Vita knappar med svarta kanter */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        font-weight: 700 !important;
        height: 4em !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Sökfältet */
    input {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        padding: 15px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Sidomeny */
    section[data-testid="stSidebar"] {
        background-color: #f0f0f0 !important;
        border-right: 3px solid #000000;
    }

    /* Info-rutor */
    .status-box {
        border: 2px solid #000000;
        padding: 15px;
        text-align: center;
        font-weight: 700;
        margin-bottom: 10px;
        background: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Logga och App-struktur
st.markdown('<div class="logo-container"><div class="logo-text">PLAYIT</div></div>', unsafe_allow_html=True)
st.write("") # Mellanrum för loggan

# Initiera session states för navigering
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song" not in st.session_state: st.session_state.current_song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

songs_dir = "library"

# 3. Huvudlogik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])

    if st.session_state.view == "list":
        # --- VY: LÅTLISTA & SÖK ---
        st.title("ARKIV")
        search = st.text_input("SÖK LÅT ELLER ARTIST", "")
        filtered = [f for f in song_files if search.lower() in f.lower()]
        
        st.write("---")
        
        # Visa låtarna som stora knappar
        for s in filtered:
            if st.button(s.replace(".md", "")):
                st.session_state.current_song = s
                st.session_state.transpose = 0
                st.session_state.scroll = 0
                st.session_state.view = "song"
                st.rerun()
    
    else:
        # --- VY: LÅTEN ---
        # Navigering högst upp
        if st.button("← TILLBAKA TILL ARKIVET"):
            st.session_state.view = "list"
            st.rerun()
            
        st.header(st.session_state.current_song.replace(".md", ""))

        # Sidomeny för kontroller
        st.sidebar.title("INSTÄLLNINGAR")
        
        # Transponering
        st.sidebar.write("### TRANSPONERA")
        st.sidebar.markdown(f'<div class="status-box">STEG: {st.session_state.transpose}</div>', unsafe_allow_html=True)
        t1, t2 = st.sidebar.columns(2)
        if t1.button("-"): st.session_state.transpose -= 1
        if t2.button("+"): st.session_state.transpose += 1
        if st.sidebar.button("NOLLSTÄLL TONART"): st.session_state.transpose = 0
        
        st.sidebar.markdown("---")
        
        # Auto-scroll
        st.sidebar.write("### AUTO-SCROLL")
        st.sidebar.markdown(f'<div class="status-box">FART: {st.session_state.scroll}</div>', unsafe_allow_html=True)
        s1, s2 = st.sidebar.columns(2)
        if s1.button("SAKTARE"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
        if s2.button("SNABBARE"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
        
        if st.sidebar.button("STOPPA SCROLL"):
            st.session_state.scroll = 0
            st.rerun()

        # Läs låten
        with open(os.path.join(songs_dir, st.session_state.current_song), "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        # Transponera ackorden
        processed_text = transpose_chords(raw_text, st.session_state.transpose)
        
        # Lägg till extra rader i slutet för att kunna scrolla hela vägen
        display_text = processed_text + ("\n" * 30)

        # JavaScript för scroll
        scroll_js = ""
        if st.session_state.scroll > 0:
            delay = (11 - st.session_state.scroll) * 35
            scroll_js = f"""
            <script>
            var box = document.getElementById("song-box");
            if (window.sInterval) clearInterval(window.sInterval);
            window.sInterval = setInterval(function() {{
                if (box) box.scrollTop += 1;
            }}, {delay});
            </script>
            """

        # Visa låttexten
        st.markdown(f"""
            <div id="song-box" class="song-container">{display_text}</div>
            {scroll_js}
        """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
