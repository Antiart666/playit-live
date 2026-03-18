import streamlit as st
import os
import re

# Grundinställningar för mobilvänlighet och mörkt tema
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FUNKTIONER FÖR TRANSPONERING ---
def transpose_chords(text, steps):
    if steps == 0:
        return text
    
    chords = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    def replace_chord(match):
        chord = match.group(0)
        # Separera grundton från tillägg (m, 7, sus etc)
        base_chord = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base_chord):]
        
        # Hantera b-förtecken (omvandla till #)
        if base_chord == "Db": base_chord = "C#"
        if base_chord == "Eb": base_chord = "D#"
        if base_chord == "Gb": base_chord = "F#"
        if base_chord == "Ab": base_chord = "G#"
        if base_chord == "Bb": base_chord = "A#"
        
        if base_chord in chords:
            current_index = chords.index(base_chord)
            new_index = (current_index + steps) % 12
            return chords[new_index] + suffix
        return chord

    # Hittar ackord (bokstäver som ofta står ensamma eller med tillägg)
    chord_pattern = r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b"
    return re.sub(chord_pattern, replace_chord, text)

# --- CSS FÖR UTSEENDE OCH AUTO-SCROLL ---
st.markdown("""
    <style>
    /* Design för låttexten */
    .song-text {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap; 
        word-wrap: break-word;
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        font-size: 16px; /* Något större för läsbarhet på scen */
        line-height: 1.5;
        border: 2px solid #333;
        margin-top: 10px;
    }
    
    /* Justering för sidomenyn */
    section[data-testid="stSidebar"] {
        width: 85% !important;
    }
    
    /* Knapp-styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
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
        st.sidebar.header("Navigation")
        search_term = st.sidebar.text_input("Sök låt/artist", "")
        filtered_songs = [f for f in song_files if search_term.lower() in f.lower()]
        
        if filtered_songs:
            selected_song = st.sidebar.selectbox("Välj låt", sorted(filtered_songs))
            
            # --- TRANSPONERINGSKONTROLL ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Verktyg")
            steps = st.sidebar.number_input("Transponera (steg)", -11, 12, 0)
            
            # --- AUTO-SCROLL KONTROLL ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Auto-scroll")
            scroll_speed = st.sidebar.slider("Hastighet", 0, 10, 0)
            
            # Läs in låten
            with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
                content = f.read()
            
            # Transponera om användaren valt det
            if steps != 0:
                content = transpose_chords(content, steps)
                
            st.subheader(selected_song.replace(".md", ""))

            # --- IMPLEMENTATION AV SCROLL ---
            if scroll_speed > 0:
                delay = (11 - scroll_speed) * 1000 # Millisekunder
                st.markdown(f"""
                    <script>
                    var scrollInterval = setInterval(function() {{
                        window.scrollBy(0, 1);
                    }}, {delay});
                    </script>
                    """, unsafe_allow_html=True)
                if st.button("Stoppa Scroll"):
                    st.rerun()

            # Visa texten
            st.markdown(f'<div class="song-text">{content}</div>', unsafe_allow_html=True)
            
        else:
            st.sidebar.warning("Ingen låt matchar sökningen.")

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
