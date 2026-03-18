import streamlit as st
import os
import re

# Grundinställningar
st.set_page_config(
    page_title="PlayIt Live ULTIMATE",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOGIK FÖR TRANSPONERING ---
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

# --- CSS FÖR DESIGN ---
st.markdown("""
    <style>
    .song-text {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap; 
        word-wrap: break-word;
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        font-size: 16px;
        line-height: 1.5;
        border: 2px solid #444;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .stop-btn>div>button {
        background-color: #ff4b4b !important;
        color: white !important;
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

st.title("🎸 PlayIt Live ULTIMATE")

# Initiera session states
if "transpose_steps" not in st.session_state: st.session_state.transpose_steps = 0
if "scroll_speed" not in st.session_state: st.session_state.scroll_speed = 0
if "last_song" not in st.session_state: st.session_state.last_song = ""

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])
    
    if song_files:
        st.sidebar.header("MENY")
        search = st.sidebar.text_input("Sök låt", "")
        filtered = [f for f in song_files if search.lower() in f.lower()]
        
        if filtered:
            selected_song = st.sidebar.selectbox("Välj låt", filtered)
            
            # Nollställ transponering om vi byter låt
            if selected_song != st.session_state.last_song:
                st.session_state.transpose_steps = 0
                st.session_state.scroll_speed = 0
                st.session_state.last_song = selected_song

            # --- TRANSPONERINGSKONTROLLER ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Transponera")
            orig_key = st.sidebar.selectbox("Original-tonart:", CHORDS)
            
            t_col1, t_col2 = st.sidebar.columns(2)
            if t_col1.button("Sänk -1"): st.session_state.transpose_steps -= 1
            if t_col2.button("Höj +1"): st.session_state.transpose_steps += 1
            if st.sidebar.button("Nollställ Tonart"): st.session_state.transpose_steps = 0

            new_key = CHORDS[(CHORDS.index(orig_key) + st.session_state.transpose_steps) % 12]
            st.sidebar.markdown(f'<div class="info-box"><small>{orig_key} ➔ </small><strong>{new_key}</strong></div>', unsafe_allow_html=True)

            # --- AUTO-SCROLL KONTROLLER ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Auto-scroll")
            
            s_col1, s_col2 = st.sidebar.columns(2)
            if s_col1.button("Saktare"): st.session_state.scroll_speed = max(0, st.session_state.scroll_speed - 1)
            if s_col2.button("Snabbare"): st.session_state.scroll_speed = min(10, st.session_state.scroll_speed + 1)
            
            st.sidebar.markdown(f'<div class="info-box">Fart: <strong>{st.session_state.scroll_speed}</strong></div>', unsafe_allow_html=True)
            
            st.sidebar.markdown('<div class="stop-btn">', unsafe_allow_html=True)
            if st.sidebar.button("STOPPA SCROLL"):
                st.session_state.scroll_speed = 0
                st.rerun()
            st.sidebar.markdown('</div>', unsafe_allow_html=True)

            # --- VISA LÅTEN ---
            with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose_steps)
            st.subheader(selected_song.replace(".md", ""))

            if st.session_state.scroll_speed > 0:
                delay = (11 - st.session_state.scroll_speed) * 800
                st.markdown(f"<script>setInterval(function() {{ window.scrollBy(0, 1); }}, {delay});</script>", unsafe_allow_html=True)

            st.markdown(f'<div class="song-text">{content}</div>', unsafe_allow_html=True)
        else:
            st.sidebar.warning("Ingen träff.")

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
