import streamlit as st
import asyncio
import edge_tts
import tempfile
import random

# Page Config
st.set_page_config(
    page_title="AI Cinematic Studio Pro",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End UI CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    .title-text {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #ff758c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .subtitle-text {
        text-align: center;
        color: #8b949e;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }

    .ad-banner {
        background: linear-gradient(135deg, #1f242d, #161b22);
        border: 1px dashed #30363d;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: #58a6ff;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 15px 0px;
    }

    .scene-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #238636, #2ea043);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 24px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #2ea043, #3fb950);
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# Main Title Header
st.markdown("<h1 class='title-text'>🐉 AI Cinematic Story Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>Smart Fantasy Video Matcher & Urdu Voice Narration</p>", unsafe_allow_html=True)

# TOP AD BANNER
st.markdown("""
<div class='ad-banner'>
    📢 <b>SPONSORED ADS / PROMOTION SPOT</b><br>
    <span style='color:#8b949e;'>Click here to explore partner tools & AI offers</span>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### ⚙️ **Studio Dashboard**")
st.sidebar.markdown("---")

voice_option = st.sidebar.selectbox(
    "🎙️ **Select Voice Model**", 
    ["ur-PK-AsadNeural (Urdu Male)", "ur-PK-UzmaNeural (Urdu Female)", "en-US-ChristopherNeural (English Male)"]
)

st.sidebar.markdown("---")
st.sidebar.success("✅ **Smart Cinematic Engine Active**")

# SIDEBAR AD BANNER
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class='ad-banner'>
    🎯 <b>AdSpot</b><br>
    Monetize Your Traffic
</div>
""", unsafe_allow_html=True)

# Input Area
user_input = st.text_area(
    "✍️ **Script & Story Input:**", 
    height=130, 
    value="Koh-e-Qaf ke paharon mein ek ajeeb dragon rehta tha.\nUski saans se aag ke sholay nikalte thay.\nZayn ne himmat karke dragon ka samna kiya.",
    placeholder="Write your line-by-line script here..."
)

async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        await communicate.save(fp.name)
        return fp.name

# Curated Stable Fantasy & Cinematic Video Library (Including Sintel & Epic Open Sources)
FANTASY_VIDEOS = {
    "dragon": "https://media.w3.org/2010/05/sintel/trailer.mp4",
    "pahar": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
    "aag": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "jung": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "default": [
        "https://media.w3.org/2010/05/sintel/trailer.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4"
    ]
}

def get_matching_video(line_text, index):
    text_lower = line_text.lower()
    if "dragon" in text_lower or "aag" in text_lower or "sholay" in text_lower:
        return FANTASY_VIDEOS["dragon"]
    elif "pahar" in text_lower or "mountain" in text_lower:
        return FANTASY_VIDEOS["pahar"]
    elif "jung" in text_lower or "fight" in text_lower or "samna" in text_lower:
        return FANTASY_VIDEOS["jung"]
    else:
        # Fallback pool rotation
        pool = FANTASY_VIDEOS["default"]
        return pool[index % len(pool)]

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 Generate Voice & Cinematic Video Scenes"):
    if not user_input.strip():
        st.warning("Pehele text enter karein.")
    else:
        lines = [line.strip() for line in user_input.split('\n') if line.strip()]
        
        for idx, line in enumerate(lines, 1):
            st.markdown("<div class='scene-box'>", unsafe_allow_html=True)
            st.markdown(f"### 📍 **Scene {idx}:** *\"{line}\"*", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            # Audio Generation
            with col1:
                st.subheader("🔊 **Voice Audio**")
                with st.spinner("Generating Voice..."):
                    voice_code = voice_option.split()[0]
                    audio_path = asyncio.run(generate_audio(line, voice_code))
                    st.audio(audio_path, format="audio/mp3")
            
            # Cinematic Video Player using HTML5 for 100% Mobile Stability
            with col2:
                st.subheader("🎞️ **Cinematic Video Clip**")
                video_url = get_matching_video(line, idx)
                video_html = f"""
                <video width="100%" height="auto" controls autoplay muted loop style="border-radius: 8px; border: 1px solid #30363d;">
                    <source src="{video_url}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                """
                st.markdown(video_html, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

        # BOTTOM AD BANNER
        st.markdown("""
        <div class='ad-banner'>
            🔥 <b>SUPPORT OUR STUDIO</b> — Click sponsor links above to keep this tool free!
        </div>
        """, unsafe_allow_html=True)
        
        st.success("✅ **Processing Complete!** Voice and matching fantasy cinematic videos generated successfully.")
    
