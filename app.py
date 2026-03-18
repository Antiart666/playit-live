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
    """Gör om filnamn till snygg läsbar text."""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    """Hanterar transponering av ackord i texten."""
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

# --- DESIGN (Inter-font, Rundade hörn, Scen-layout) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    .block-container {
        padding-top: 0.5rem !important;
        max-width: 98% !important;
    }

    /* Fast Header för logga */
    .header-area {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 20px;
    }

    .logo-container {
        transform: rotate(-8deg);
        background: #000000;
        padding: 8px 18px;
        border-radius: 12px;
        display: inline-block;
    }
    .logo-text { color: #ffffff; font-weight: 900; font-size: 18px; text-transform: uppercase; }

    /* Låtrutan - Maxad och rundad */
    .song-container {
        height: 80vh; 
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff;
        color: #000000;
        padding: 20px;
        border: 3px solid #000000;
        border-radius: 25px; 
        font-family: 'Courier New', Courier, monospace;
        font-size: 17px; 
        line-height: 1.5;
        white-space: pre-wrap;
    }

    /* Knappar - Runda och tydliga */
    .stButton>button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        text-transform: uppercase;
    }
    
    /* Sökfältet */
    input { border: 2px solid #000000 !important; border-radius: 15px !important; }

    /* Kategorirubriker */
    .category-label {
        font-size: 13px;
        font-weight: 900;
        text-transform: uppercase;
        color: #666;
        margin-top: 25px;
        margin-bottom: 10px;
        letter-spacing: 1px;
        border-left: 4px solid #000;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Status & Navigation
if "view" not in st.session_state: st.session_state.view = "list"
if "current_song_path" not in st.session_state: st.session_state.current_song_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0
if "show_tools" not in st.session_state: st.session_state.show_tools = False

# Render Header
st.markdown('<div class="logo-container"><div class="logo-text">PLAYIT</div></div>', unsafe_allow_html=True)

songs_dir = "library"

# 3. Huvudlogik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' hittades inte på GitHub.")
else:
    if st.session_state.view == "list":
        # --- ARKIV-VY ---
        st.title("Arkiv")
        search = st.text_input("SÖK LÅT...", placeholder="Skriv titel eller artist")
        
        # Samla alla låtar och kategorier genom att vandra i mapparna
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            # Filtrera .md-filer
            valid_files = sorted([f for f in files if f.endswith(".md")])
            filtered_files = [f for f in valid_files if search.lower() in f.lower() or search.lower() in clean_title(f).lower()]
            
            if filtered_files:
                st.markdown(f'<div class="category-label">{category}</div>', unsafe_allow_html=True)
                # Visa i två kolumner för bättre överblick
                cols = st.columns(2)
                for i, filename in enumerate(filtered_files):
                    with cols[i % 2]:
                        if st.button(clean_title(filename), key=os.path.join(root, filename)):
                            st.session_state.current_song_path = os.path.join(root, filename)
                            st.session_state.transpose = 0
                            st.session_state.scroll = 0
                            st.session_state.show_tools = False
                            st.session_state.view = "song"
                            st.rerun()

    else:
        # --- SCEN-VY (Låten är öppen) ---
        
        # Navigeringsrad ovanför låten
        nav_col1, nav_col2 = st.columns([1, 1])
        with nav_col1:
            if st.button("← TILL ARKIVET"):
                st.session_state.view = "list"
                st.rerun()
        with nav_col2:
            tool_label = "✖ STÄNG VERKTYG" if st.session_state.show_tools else "⚙ INSTÄLLNINGAR"
            if st.button(tool_label):
                st.session_state.show_tools = not st.session_state.show_tools
                st.rerun()

        # Verktygspanel (Transponering och Scroll)
        if st.session_state.show_tools:
            st.info("Här kan du justera tonart och scrollfart för låten.")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("**TONART**")
                if st.button("- Sänk"): st.session_state.transpose -= 1
                if st.button("+ Höj"): st.session_state.transpose += 1
            with c2:
                st.write("**SCROLL**")
                if st.button("Saktare"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
                if st.button("Snabbare"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            with c3:
                st.write("**STATUS**")
                st.write(f"Steg: {st.session_state.transpose}")
                st.write(f"Fart: {st.session_state.scroll}")
                if st.button("STOPP"): 
                    st.session_state.scroll = 0
                    st.rerun()
            st.markdown("---")

        # Visa titeln tydligt
        st.subheader(clean_title(os.path.basename(st.session_state.current_song_path)))

        # Innehållshantering
        with open(st.session_state.current_song_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = transpose_chords(content, st.session_state.transpose)
        # La till extra utrymme i botten
        display_text = content + ("\n" * 45)

        # Scroll-funktion
        if st.session_state.scroll > 0:
            delay = (11 - st.session_state.scroll) * 35
            st.markdown(f"""
                <script>
                var box = window.parent.document.getElementById("song-box");
                if (window.sInterval) clearInterval(window.sInterval);
                window.sInterval = setInterval(function() {{
                    if (box) box.scrollTop += 1;
                }}, {delay});
                </script>
            """, unsafe_allow_html=True)

        st.markdown(f'<div id="song-box" class="song-container">{display_text}</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.write("Rock on! 🤘")
