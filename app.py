import streamlit as st
import os
import re
import streamlit.components.v1 as components

# Grundinställningar
st.set_page_config(
    page_title="PlayIt Live PRO",
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

# --- CSS FÖR DESIGN OCH SCROLL-CONTAINER ---
st.markdown("""
    <style>
    /* Denna container blir vår egen scrollbara yta */
    .scroll-container {
        height: 70vh;
        overflow-y: auto;
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #444;
        font-family: 'Courier New', Courier, monospace;
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        height: 3.5em;
    }
    .info-box {
        background-color: #262730;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #444;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎸 PlayIt Live PRO")

if "transpose_steps" not in st.session_state: st.session_state.transpose_steps = 0
if "is_scrolling" not in st.session_state: st.session_state.is_scrolling = False

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])
    
    if song_files:
        st.sidebar.header("MENY")
        selected_song = st.sidebar.selectbox("Välj låt", song_files)
        
        # --- TRANSPONERING ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("Transponera")
        t_col1, t_col2 = st.sidebar.columns(2)
        if t_col1.button("Sänk -1"): st.session_state.transpose_steps -= 1
        if t_col2.button("Höj +1"): st.session_state.transpose_steps += 1
        st.sidebar.write(f"Steg: {st.session_state.transpose_steps}")

        # --- AUTO-SCROLL KONTROLLER ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("Auto-scroll")
        
        if st.sidebar.button("STARTA SCROLL"):
            st.session_state.is_scrolling = True
        
        if st.sidebar.button("STOPPA SCROLL"):
            st.session_state.is_scrolling = False
            st.rerun()

        # Läs och förbered texten
        with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose_steps)
        st.subheader(selected_song.replace(".md", ""))

        # HTML/JS för att scrolla inuti containern
        # Vi använder ett unikt ID 'song-box' för containern
        container_html = f'<div id="song-box" class="scroll-container">{content}</div>'
        
        if st.session_state.is_scrolling:
            # JavaScript som letar upp 'song-box' inuti parent-fönstret
            components.html("""
                <script>
                var container = window.parent.document.getElementById("song-box");
                if (container) {
                    var scrollInterval = setInterval(function() {
                        container.scrollTop += 1;
                    }, 50); // Justera siffran 50 för hastighet (lägre = snabbare)
                }
                </script>
            """, height=0)

        st.markdown(container_html, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
