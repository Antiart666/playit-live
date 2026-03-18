import streamlit as st
import os
import re

# 1. Grundinställningar
st.set_page_config(
    page_title="PlayIt Live",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    name = filename.replace(".md", "")
    name = name.replace("_", " ")
    return name.strip().capitalize()

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

# --- DESIGN (Justerad textstorlek och maximerad yta) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 98% !important;
    }

    .logo-container {
        position: absolute;
        top: -10px;
        left: 20px;
        z-index: 1000;
        transform: rotate(-8deg);
        background: #000000;
        padding: 8px 18px;
        border-radius: 12px;
    }
    
    .logo-text {
        color: #ffffff;
        font-weight: 900;
        font-size: 20px;
        text-transform: uppercase;
    }

    .song-container {
        height: 82vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px; /* Något mindre padding för mer textyta */
        border: 3px solid #000000;
        border-radius: 30px; 
        margin-top: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 18px; /* JUSTERAD FRÅN 20px TILL 18px */
        line-height: 1.5;
        white-space: pre-wrap;
        box-shadow: 10px 10px 0px #f0f0f0;
    }

    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
    }

    input {
        border: 2px solid #000000 !important;
        border-radius: 20px !important;
    }

    .status-box {
        border: 2px solid #000000;
        padding: 10px;
        border-radius: 15px;
        text-align: center;
        font-weight: 700;
        background: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initiera App
st.markdown('<div class="logo-container"><div class="logo-text">PLAYIT</div></div>', unsafe_allow_html=True)
st.write("") 

if "view" not in st.session_state: st.session_state.view = "list"
if "current_song" not in st.session_state: st.session_state.current_song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])

    if st.session_state.view == "list":
        # --- ARKIV-VY ---
        st.title("Arkiv")
        search = st.text_input("Sök låt...", "")
        filtered = [f for f in song_files if search.lower() in f.lower() or search.lower() in clean_title(f).lower()]
        
        st.write("---")
        
        for s in filtered:
            if st.button(clean_title(s)):
                st.session_state.current_song = s
                st.session_state.transpose = 0
                st.session_state.scroll = 0
                st.session_state.view = "song"
                st.rerun()
    
    else:
        # --- LÅT-VY ---
        col_back, col_title = st.columns([1, 4])
        with col_back:
            if st.button("←"):
                st.session_state.view = "list"
                st.rerun()
        with col_title:
            st.subheader(clean_title(st.session_state.current_song))

        # Kontroller i sidomenyn
        st.sidebar.title("KONTROLLER")
        
        st.sidebar.write("### TONART")
        st.sidebar.markdown(f'<div class="status-box">STEG: {st.session_state.transpose}</div>', unsafe_allow_html=True)
        t1, t2 = st.sidebar.columns(2)
        if t1.button("-"): st.session_state.transpose -= 1
        if t2.button("+"): st.session_state.transpose += 1
        
        st.sidebar.markdown("---")
        
        st.sidebar.write("### AUTO-SCROLL")
        st.sidebar.markdown(f'<div class="status-box">FART: {st.session_state.scroll}</div>', unsafe_allow_html=True)
        s1, s2 = st.sidebar.columns(2)
        if s1.button("SAKTARE"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
        if s2.button("SNABBARE"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
        
        if st.sidebar.button("STOPP"):
            st.session_state.scroll = 0
            st.rerun()

        # Läs och bearbeta
        with open(os.path.join(songs_dir, st.session_state.current_song), "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        processed_text = transpose_chords(raw_text, st.session_state.transpose)
        display_text = processed_text + ("\n" * 40) 

        # Scroll-skript
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

        st.markdown(f"""
            <div id="song-box" class="song-container">{display_text}</div>
            {scroll_js}
        """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
