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

# --- DESIGN (Ljust tema, vita knappar, svarta kanter) ---
st.markdown("""
    <style>
    /* Huvudbakgrund */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* Mobilanpassning av ytan */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
        max-width: 100%;
    }

    /* Snedställd logga uppe till vänster */
    .logo-text {
        position: absolute;
        top: -10px;
        left: 10px;
        font-size: 28px;
        font-weight: 900;
        transform: rotate(-10deg);
        color: #000000;
        z-index: 100;
        font-family: 'Arial Black', sans-serif;
    }

    /* Låt-boxen */
    .scroll-container {
        height: 70vh;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 15px;
        border: 3px solid #000000;
        border-radius: 0px; /* Mer avskalat med raka hörn */
        font-family: 'Courier New', Courier, monospace;
        font-size: 18px;
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* Vita knappar med svarta kanter */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        text-transform: uppercase;
    }
    
    /* Sökfältet och input */
    input {
        border: 2px solid #000000 !important;
        border-radius: 0px !important;
    }

    /* Sidomenyn ljus */
    section[data-testid="stSidebar"] {
        background-color: #f8f8f8 !important;
        border-right: 2px solid #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initiera Session States
if "view" not in st.session_state: st.session_state.view = "list"
if "selected_song" not in st.session_state: st.session_state.selected_song = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "speed" not in st.session_state: st.session_state.speed = 0

# Visa loggan (placeholder tills du har din bild)
st.markdown('<div class="logo-text">PLAYIT</div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])

    if st.session_state.view == "list":
        # --- LIST-VY ---
        st.title("Mina Låtar")
        search = st.text_input("Sök...", "")
        filtered = [f for f in song_files if search.lower() in f.lower()]
        
        for s in filtered:
            if st.button(s.replace(".md", "")):
                st.session_state.selected_song = s
                st.session_state.transpose = 0
                st.session_state.speed = 0
                st.session_state.view = "song"
                st.rerun()
    
    else:
        # --- LÅT-VY ---
        # Tillbaka-knapp högst upp
        if st.button("← TILLBAKA"):
            st.session_state.view = "list"
            st.rerun()
            
        st.header(st.session_state.selected_song.replace(".md", ""))

        # Sidomeny för kontroller (gömd som standard på mobil)
        st.sidebar.subheader("KONTROLLER")
        
        # Transponering
        st.sidebar.write(f"Tonart steg: {st.session_state.transpose}")
        c1, c2 = st.sidebar.columns(2)
        if c1.button("-"): st.session_state.transpose -= 1
        if c2.button("+"): st.session_state.transpose += 1
        
        st.sidebar.markdown("---")
        
        # Scroll
        st.sidebar.write(f"Scrollfart: {st.session_state.speed}")
        s1, s2 = st.sidebar.columns(2)
        if s1.button("Saktare"): st.session_state.speed = max(0, st.session_state.speed - 1)
        if s2.button("Snabbare"): st.session_state.speed = min(10, st.session_state.speed + 1)
        
        if st.sidebar.button("STOPPA SCROLL"):
            st.session_state.speed = 0
            st.rerun()

        # Läs låten
        with open(os.path.join(songs_dir, st.session_state.selected_song), "r", encoding="utf-8") as f:
            text = f.read()
        
        text = transpose_chords(text, st.session_state.transpose)
        
        # Rendera låten och scroll-skriptet i ett och samma block för att undvika "Script error"
        # Vi lägger till 30 tomma rader i slutet för att kunna scrolla förbi sista versen
        display_text = text + ("\n" * 30)
        
        # Beräkna hastighet (ms)
        delay = (11 - st.session_state.speed) * 30 if st.session_state.speed > 0 else 0

        scroll_script = ""
        if st.session_state.speed > 0:
            scroll_script = f"""
            <script>
            var container = document.getElementById("song-box");
            var scrollVal = 0;
            function doScroll() {{
                if (container) {{
                    container.scrollTop += 1;
                }}
            }}
            if (window.scrollInterval) clearInterval(window.scrollInterval);
            window.scrollInterval = setInterval(doScroll, {delay});
            </script>
            """

        st.markdown(f"""
            <div id="song-box" class="scroll-container">{display_text}</div>
            {scroll_script}
        """, unsafe_allow_html=True)
