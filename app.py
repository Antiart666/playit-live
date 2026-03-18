import streamlit as st
import os
import re
import streamlit.components.v1 as components

# Grundinställningar - Kompakt layout och mörkt tema som standard
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

# --- DESIGN (CSS) ---
st.markdown("""
    <style>
    /* Bakgrunden */
    .stApp {
        background-color: #f0f0f0;
        color: #000000;
    }
    
    /* Ta bort onödigt vitt utrymme högst upp */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Den ljusa boxen för låten */
    .scroll-container {
        height: 75vh;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #000000;
        font-family: 'Courier New', Courier, monospace;
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
    }
    
    /* Tydliga knappar: Vita med svarta kanter */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
        height: 3.5em;
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #000000;
    }
    
    /* Infoboxar för transponering och fart */
    .info-box {
        background-color: #e0e0e0;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #000000;
        color: #000000;
        margin-bottom: 10px;
    }
    
    /* Snedställd logga */
    .logo-container {
        transform: rotate(-15deg);
        position: absolute;
        top: 20px;
        left: 20px;
        font-size: 24px;
        font-weight: bold;
        color: #000000;
    }
    </style>
    """, unsafe_allow_html=True)

# Plats för din logga
st.markdown('<div class="logo-container">LOGGA</div>', unsafe_allow_html=True)

st.title("🎸 PlayIt Live")

# Initiera session states
if "transpose_steps" not in st.session_state: st.session_state.transpose_steps = 0
if "scroll_speed" not in st.session_state: st.session_state.scroll_speed = 0
if "last_song" not in st.session_state: st.session_state.last_song = ""
if "view" not in st.session_state: st.session_state.view = "list"  # 'list' eller 'song'

songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas!")
else:
    song_files = sorted([f for f in os.listdir(songs_dir) if f.endswith(".md")])
    
    if song_files:
        if st.session_state.view == "list":
            # --- LÅTLIST-VY ---
            st.subheader("Mina Låtar")
            search = st.text_input("Sök låt", "")
            filtered = [f for f in song_files if search.lower() in f.lower()]
            
            for song in filtered:
                if st.button(song.replace(".md", "")):
                    st.session_state.last_song = song
                    st.session_state.transpose_steps = 0
                    st.session_state.scroll_speed = 0
                    st.session_state.view = "song"
                    st.rerun()
                    
        else:
            # --- LÅTVY ---
            selected_song = st.session_state.last_song
            
            # --- Tydligare Navigering ---
            if st.sidebar.button("<- Tillbaka till låtlistan"):
                st.session_state.view = "list"
                st.rerun()
            
            st.subheader(selected_song.replace(".md", ""))

            # --- TRANSPONERING (Gömda i sidomenyn) ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Transponera")
            t_col1, t_col2 = st.sidebar.columns(2)
            if t_col1.button("Sänk -1"): st.session_state.transpose_steps -= 1
            if t_col2.button("Höj +1"): st.session_state.transpose_steps += 1
            st.sidebar.markdown(f'<div class="info-box">Steg: <strong>{st.session_state.transpose_steps}</strong></div>', unsafe_allow_html=True)

            # --- AUTO-SCROLL (Gömda i sidomenyn) ---
            st.sidebar.markdown("---")
            st.sidebar.subheader("Auto-scroll")
            s_col1, s_col2 = st.sidebar.columns(2)
            if s_col1.button("Saktare"): st.session_state.scroll_speed = max(0, st.session_state.scroll_speed - 1)
            if s_col2.button("Snabbare"): st.session_state.scroll_speed = min(10, st.session_state.scroll_speed + 1)
            
            st.sidebar.markdown(f'<div class="info-box">Fart: <strong>{st.session_state.scroll_speed}</strong></div>', unsafe_allow_html=True)
            
            if st.sidebar.button("STOPPA SCROLL", type="primary"):
                st.session_state.scroll_speed = 0
                st.rerun()

            # Läs och förbered texten
            with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
                content = f.read()
            
            content = transpose_chords(content, st.session_state.transpose_steps)

            # Skapa containern med texten
            # Vi lägger till massor av extra tomrum i botten av texten så man kan scrolla hela vägen ut
            full_display_content = content + "\n\n" + ("\n" * 20)
            st.markdown(f'<div id="song-box" class="scroll-container">{full_display_content}</div>', unsafe_allow_html=True)
            
            # JavaScript för att styra farten (1-10)
            if st.session_state.scroll_speed > 0:
                # Beräkna delay: Ju högre fart, desto kortare väntetid mellan stegen
                # Fart 1 = 200ms, Fart 10 = 20ms
                ms_delay = (11 - st.session_state.scroll_speed) * 20
                
                components.html(f"""
                    <script>
                    var container = window.parent.document.getElementById("song-box");
                    if (container) {{
                        var scrollInterval = setInterval(function() {{
                            container.scrollTop += 1;
                        }}, {ms_delay});
                    }}
                    </script>
                """, height=0)

else:
    st.info("Inga låtar hittades i mappen 'library'.")

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
