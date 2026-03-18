import streamlit as st
import os

# Grundinställningar för mobilvänlighet
st.set_page_config(
    page_title="PlayIt Live",
    page_icon="🎸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS för att hålla ihop texten och förhindra att den "rinner ut"
st.markdown("""
    <style>
    .song-text {
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap; /* Håller radbrytningar men bryter vid kanten */
        word-wrap: break-word;
        background-color: #1a1a1a;
        color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        font-size: 14px;
        line-height: 1.4;
        border: 1px solid #333;
    }
    /* Gör sidomenyn lite bredare på mobil för sökfältet */
    section[data-testid="stSidebar"] {
        width: 80% !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎸 PlayIt Live")

# Sökväg till mappen med låtar
songs_dir = "library"

if not os.path.exists(songs_dir):
    st.error(f"Mappen '{songs_dir}' hittades inte på GitHub!")
else:
    # Hämta alla .md-filer
    song_files = [f for f in os.listdir(songs_dir) if f.endswith(".md")]
    
    if not song_files:
        st.info("Ladda upp dina låtar (.md) i mappen 'library' på GitHub för att se dem här.")
    else:
        # Sidomeny för sök och val
        st.sidebar.header("Mina Låtar")
        search_term = st.sidebar.text_input("Sök låt eller artist...", "")
        
        # Filtrera låtar baserat på sökning
        filtered_songs = [f for f in song_files if search_term.lower() in f.lower()]
        
        if filtered_songs:
            selected_song = st.sidebar.selectbox("Välj en låt", sorted(filtered_songs))
            
            # Läs in och visa vald låt
            with open(os.path.join(songs_dir, selected_song), "r", encoding="utf-8") as f:
                content = f.read()
                
            st.subheader(selected_song.replace(".md", ""))
            # Här använder vi vår "song-text" klass för att hålla ihop allt
            st.markdown(f'<div class="song-text">{content}</div>', unsafe_allow_html=True)
        else:
            st.sidebar.warning("Ingen låt matchar din sökning.")

st.sidebar.markdown("---")
st.sidebar.write("Tips: Använd sökfältet ovan för att snabbt hitta dina tabs!")
