import streamlit as st
import os
import re
import base64

# 1. Konfiguration - Total kontroll över layouten
st.set_page_config(
    page_title="PlayIt Live PRO",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HJÄLPFUNKTIONER ---

def clean_title(filename):
    """Gör EYE_OF_THE_TIGER till Eye of the tiger"""
    name = filename.replace(".md", "").replace("_", " ")
    return name.strip().capitalize()

def get_image_base64(path):
    """Laddar loggan säkert och transparent."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except: return None
    return None

CHORDS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose_chords(text, steps):
    if steps == 0: return text
    def replace_chord(match):
        chord = match.group(0)
        base = re.match(r"^[A-G][#b]?", chord).group(0)
        suffix = chord[len(base):]
        norm = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        if base in norm: base = norm[base]
        if base in CHORDS:
            idx = (CHORDS.index(base) + steps) % 12
            return CHORDS[idx] + suffix
        return chord
    return re.sub(r"\b[A-G][#b]?(?:m|maj|min|dim|aug|sus|add|7|9|11|13)*\b", replace_chord, text)

# --- DESIGN (Inter-font, Stabil layout, Inga krockar) ---
logo_b64 = get_image_base64("logo.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');

    /* DÖLJ ALLT FRÅN STREAMLIT */
    header, footer, #MainMenu {{ visibility: hidden !important; display: none !important; }}
    .stApp {{ background-color: #ffffff !important; }}
    
    /* GLOBAL TEXTSTIL */
    * {{ 
        color: #000000 !important; 
        font-family: 'Inter', sans-serif !important;
        text-transform: none !important;
    }}

    .block-container {{
        padding-top: 0rem !important;
        max-width: 98% !important;
        background-color: #ffffff !important;
    }}

    /* DEN SNEDSTÄLLDA LOGGAN (Pansarsäker och transparent!) */
    .logo-sticker {{
        position: fixed;
        top: 15px;
        left: 20px;
        z-index: 1000000;
        width: 110px;
        height: auto;
        cursor: pointer;
        transform: rotate(-8deg);
        transition: transform 0.1s ease-in-out;
        
        /* Tvingar transparens och tar bort *all* border */
        border: none !important;
        background-color: transparent !important;
        background-image: none !important;
        box-shadow: none !important;
    }}
    
    .logo-sticker:active {{
        transform: rotate(-8deg) scale(0.9);
    }}

    /* DEN RIKTIGA HEMKNAPPEN (Sitter bredvid loggan, inte över) */
    div[data-testid="stButton"] > button[key="manual_home_btn"] {{
        position: fixed !important;
        top: 20px !important;
        left: 145px !important; /* Flyttad 35px åt sidan för att undvika krock */
        width: 100px !important;
        height: 55px !important;
        z-index: 999999 !important;
        
        background-color: transparent !important;
        border: none !important;
        color: #000000 !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        text-transform: uppercase !important;
        font-size: 10px !important;
    }}

    /* LÄSRUTAN (MAXIMERAD FÖR SCENEN) */
    .song-wrapper {{
        height: 90vh; /* Tvingar rutan att täcka nästan hela skärmen */
        width: 100%;
        overflow-y: auto;
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 20px;
        border: 4px solid #000000;
        border-radius: 35px; 
        font-family: 'Courier New', Courier, monospace !important;
        font-size: 18px; /* Lite större text för scenen */
        line-height: 1.5;
        white-space: pre-wrap;
    }}

    /* KNAPPAR I LISTAN */
    div[data-testid="stButton"] > button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        border-radius: 18px !important;
        font-weight: 700 !important;
        height: 3.5em !important;
        width: 100% !important;
    }}

    /* VERKTYGSBOX LÄNGST NER */
    .settings-tray {{
        margin-top: 40px;
        padding: 25px;
        background-color: #fcfcfc;
        border-radius: 30px;
        border: 2px dashed #000000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. State Management
if "view" not in st.session_state: st.session_state.view = "list"
if "current_path" not in st.session_state: st.session_state.current_path = ""
if "transpose" not in st.session_state: st.session_state.transpose = 0
if "scroll" not in st.session_state: st.session_state.scroll = 0

# --- DEN RIKTIGA HEMKNAPPEN (Bredvid loggan, inte över) ---
# Vi använder en riktig Streamlit-knapp för 100% säkerhet
if st.button("🏠 HEM", key="manual_home_btn"):
    st.session_state.view = "list"
    st.session_state.current_path = ""
    st.rerun()

# --- RITA LOGGAN OCH GE DEN EN HEM-FUNKTION VIA JS ---
if logo_b64:
    st.markdown(f"""
        <div class="logo-sticker" id="logo-trigger">
            <img src="data:image/png;base64,{logo_b64}" style="width:100%; height:auto;">
        </div>
        <script>
        // Ett litet JS som klickar på Streamlits hem-knapp när man trycker på loggan
        var logo = window.parent.document.getElementById("logo-trigger");
        if (logo) {{
            logo.onclick = function() {{
                var btns = window.parent.document.querySelectorAll('button');
                var homeBtn = Array.from(btns).find(b => b.innerText.includes("🏠 HEM"));
                if (homeBtn) homeBtn.click();
            }};
        }}
        </script>
    """, unsafe_allow_html=True)
else:
    # Om logo.png saknas på GitHub
    st.error("Filen 'logo.png' saknas på GitHub. Ladda upp den!")

songs_dir = "library"

# 3. App-logik
if not os.path.exists(songs_dir):
    st.error("Mappen 'library' saknas.")
else:
    if st.session_state.view == "list":
        # --- SIDA 1: ARKIVET ---
        # Mellanrum för att undvika krock högst upp
        st.markdown('<div style="height:110px;"></div>', unsafe_allow_html=True)
        
        for root, dirs, files in os.walk(songs_dir):
            category = os.path.basename(root)
            if category == "library": category = "Mina Låtar"
            
            valid_songs = sorted([f for f in files if f.endswith(".md")])
            if valid_songs:
                # Visar kategorinamnet snyggt
                st.markdown(f'<div style="font-weight:900; color:#888; margin-top:20px; font-size:11px; text-transform:uppercase; letter-spacing:1px;">{category}</div>', unsafe_allow_html=True)
                cols = st.columns(2)
                for i, song_file in enumerate(valid_songs):
                    with cols[i % 2]:
                        if st.button(clean_title(song_file), key=os.path.join(root, song_file)):
                            st.session_state.current_path = os.path.join(root, song_path)
                            st.session_state.view = "song"
                            st.rerun()

        # --- INSTÄLLNINGAR LÄNGST NER ---
        st.markdown('<div class="settings-tray">', unsafe_allow_html=True)
        st.subheader("⚙️ Inställningar")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Tonart**")
            t_m, t_p = st.columns(2)
            if t_m.button("- Ton", key="t_m"): st.session_state.transpose -= 1
            if t_p.button("+ Ton", key="t_p"): st.session_state.transpose += 1
            st.write(f"Steg: {st.session_state.transpose}")
        with c2:
            st.write("**Scroll**")
            s_m, s_p = st.columns(2)
            if s_m.button("Saktare", key="s_m"): st.session_state.scroll = max(0, st.session_state.scroll - 1)
            if s_p.button("Snabbare", key="s_p"): st.session_state.scroll = min(10, st.session_state.scroll + 1)
            st.write(f"Fart: {st.session_state.scroll}")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # --- SIDA 2: SCENLÄGET (Låten) ---
        # Läsrutan börjar högt upp för att loggan ska "flyta" snyggt i hörnet
        st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)

        if os.path.exists(st.session_state.current_path):
            with open(st.session_state.current_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            content = transpose_chords(raw_text, st.session_state.transpose)
            display_text = content + ("\n" * 55)

            # Säkrad auto-scroll för mobiler
            st.markdown(f"""
                <script>
                var box = window.parent.document.getElementById("song-view-box");
                if (window.playitScroll) clearInterval(window.playitScroll);
                if ({st.session_state.scroll} > 0) {{
                    var speed = (11 - {st.session_state.scroll}) * 40;
                    window.playitScroll = setInterval(function() {{ if (box) box.scrollTop += 1; }}, speed);
                }}
                </script>
            """, unsafe_allow_html=True)

            st.markdown(f'<div id="song-view-box" class="song-wrapper">{display_text}</div>', unsafe_allow_html=True)
