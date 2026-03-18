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

# --- DESIGN (Inter-font, Rundade hörn, Kontrollpanel) ---
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
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 98% !important;
    }

    /* LOGGA */
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
    .logo-text { color: #ffffff; font-weight: 900; font-size: 20px; text-transform: uppercase; }

    /* LÄSRUTAN */
    .song-container {
        height: 78vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border: 3px solid #000000;
        border-radius: 25px; 
        margin-top: 5px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 17px; /* En aning mindre för att rymma hela rader */
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* KNAPPAR */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }

    /* KONTROLLPANEL (Den 'fiffiga' rutan) */
    .control-panel {
        background-color: #f8f8f8;
        border: 2px solid #000000;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 10px;
    }

    input { border: 2px solid #000000 !important; border-radius: 15px !important; }
    
    /* Kategorier rubrik */
    .cat-header {
        font-size: 14px;
        font-weight: 900;
        text-transform: uppercase;
        margin-top: 20px;
        border-bottom: 2px solid #000000;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Initiera State
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song" not in st.session_state: st.session_state.current_song = ""
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0
if "show_controls" not in st.session_state: st.session_state.show_controls = False

st.markdown('<div class="logo-container"><div class="logo-text">PLAYIT</div></div>', unsafe_allow_html=True)
st.write("") 

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Skapa mappen 'library' på GitHub först!")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        st.title("Arkiv")
        search = st.text_input("Sök i din låtbank...", "")
        
        # Hämta mappar och filer
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Övrigt"
            
            # Filtrera filer
            valid_files = sorted([f for f in files if f.endswith(".md")])
            filtered_files = [f for f in valid_files if search.lower() in f.lower() or search.lower() in clean_title(f).lower()]
            
            if filtered_files:
                st.markdown(f'<div class="cat-header">{category}</div>', unsafe_allow_html=True)
                # Visa i 2 kolumner på mobil för att spara plats
                cols = st.columns(2)
                for idx, s in enumerate(filtered_files):
                    with cols[idx % 2]:
                        if st.button(clean_title(s), key=os.path.join(root, s)):
                            st.session_state.current_song = s
                            st.session_state.current_path = os.path.join(root, s)
                            st.session_state.transpose = 0
                            st.session_state.scroll = 0
                            st.session_state.show_controls = False
                            st.session_state.view = "song"
                            st.rerun()

    else:
        # --- SIDA 2: SCENLÄGET ---
        # Översta raden: Tillbaka och Kontroll-toggle
        nav_col1, nav_col2 = st.columns([1, 1])
        with nav_col1:
            if st.button("← ARKIV"):
                st.session_state.view = "list"
                st.rerun()
        with nav_col2:
            label = "✖ STÄNG VERKTYG" if st.session_state.show_controls else "⚙ VERKTYG"
            if st.button(label):
                st.session_state.show_controls = not st.session_state.show_controls
                st.rerun()

        # Den 'fiffiga' kontrollpanelen som dyker upp/försvinner
        if st.session_state.show_controls:
            with st.container():
                st.markdown('<div class="control-panel">', unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("**TONART**")
                    if st.button("-"): st.session_state.transpose -= 1
                    if st.button("+"): st.session_state.transpose += 1
                with c2:
                    st.write("**SCROLL**")
                    if st.button("Saktare"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
                    if st.button("Snabbare"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
                with c3:
                    st.write("**INFO**")
                    st.write(f"Steg: {st.session_state.transpose}")
                    st.write(f"Fart: {st.session_state.scroll}")
                    if st.button("STOPP"): 
                        st.session_state.scroll = 0
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Visa titel kort
        st.subheader(clean_title(st.session_state.current_song))

        # Läs och bearbeta låten
        with open(st.session_state.current_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        text = transpose_chords(text, st.session_state.transpose)
        display_text = text + ("\n" * 40)

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

# Vill du ha ett djupgående expertsvar eller räcker det med en kortare sammanfattning?
