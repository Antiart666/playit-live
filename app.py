import streamlit as st
import os
import re

# Grundinställningar för mobilvänlighet
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- TRANSPONERINGSLOGIK ---
CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0:
        return text
    
    def replace_chord(match):
        chord = match.group(0)
        base_chord = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base_chord):]
        
        # Normalisera b till #
        norm_map = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base_chord in norm_map:
            base_chord = norm_map[base_chord]
        
        if base_chord in CHORDS:
            current_index = CHORDS.index(base_chord)
            new_index = (current_index + steps) % 12
            return CHORDS[new_index] + suffix
        return chord

    chord_pattern = r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b"
    return re.sub(chord_pattern, replace_chord, text)

# --- CSS FÖR UTSEENDE ---
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
        height: 3em;
    }
    .info-box {
        background-color: #262730;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #444;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎸 PlayIt Live PRO")

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error(f"Mappen '{songs_dir}' hittades inte!")
else:
    song_files = [f for f in os.listdir(songs_dir) if f.endswith(".md")]
    
    if not song_files:
        st.info("Ladda upp låtar i mappen 'library' på GitHub.")
    else:
        # --- SIDOMENY ---
        st.sidebar.header("MENY")
        search_term = st.sidebar.text_input("Sök låt/artist", "")
        filtered_songs = [f for f in song_files if search_term.lower() in f.lower()]
        
        if filtered_songs:
            selected_song = st.sidebar.selectbox("Välj låt", sorted(filtered_songs))
            
            # --- NY TRANSPONERINGSDEL ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Transponera")
            
            # Välj start-tonart (för att visa pedagogiskt)
            original_key = st.sidebar.selectbox("Låtens original-tonart:", CHORDS)
            
            # Knappar för att flytta upp/ner
            col1, col2 = st.sidebar.columns(2)
            if "transpose_steps" not in st.session_state:
                st.session_state.transpose_steps = 0
            
            if col1.button("Sänk -1"):
                st.session_state.transpose_steps -= 1
            if col2.button("Höj +1"):
                st.session_state.transpose_steps += 1
            if st.sidebar.button("Nollställ"):
                st.session_state.transpose_steps = 0

            # Räkna ut ny tonart
            current_key_index = (CHORDS.index(original_key) + st.session_state.transpose_steps) % 12
            new_key = CHORDS[current_key_index]
            
            # Visa pedagogisk info
            st.sidebar.markdown(f"""
                <div class="info-box">
                    <small>Original: {original_key}</small><br>
                    <strong>NY TONART: {new_key}</strong><br>
                    <small>({st.session_state.transpose_steps} steg)</small>
                </div>
            """, unsafe_allow_html=True)
            
            # --- AUTO-SCROLL ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Auto-scroll")
            scroll_speed = st.sidebar.slider("Hastighet (0 = av)", 0, 10, 0)
            
            # Läs in och bearbeta låten
            with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose_steps)
                
            st.subheader(selected_song.replace(".md", ""))

            # Scroll-logik
            if scroll_speed > 0:
                delay = (11 - scroll_speed) * 800
                st.markdown(f"<script>setInterval(function() {{ window.scrollBy(0, 1); }}, {delay});</script>", unsafe_allow_html=True)

            # Visa texten
            st.markdown(f'<div class="song-text">{content}</div>', unsafe_allow_html=True)
            
        else:
            st.sidebar.warning("Hittade ingen match.")

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
