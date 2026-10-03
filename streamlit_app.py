import streamlit as st
import asyncio
import edge_tts
import requests
import tempfile
import os

# Page Config
st.set_page_config(
    page_title="AI Media Studio Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End & Smooth UI CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Title Gradient */
    .title-text {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff4b4b, #f06292);
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

    /* Ad Banner Container */
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

    /* Card Styling */
    .scene-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    
    /* Button Animation */
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
""", unsafe_allow_text=True)

# Main Title Header
st.markdown("<h1 class='title-text'>⚡ AI Media Studio Pro</h1>", unsafe_allow_text=True)
st.markdown("<p class='subtitle-text'>Ultra-Fast Voice Narration & Visual Studio Engine</p>", unsafe_allow_text=True)

# TOP AD BANNER PLACEHOLDER (Yahan apna AdSterra/Banner link laga sakte hain)
st.markdown("""
<div class='ad-banner'>
    📢 <b>SPONSORED ADS / PROMOTION SPOT</b><br>
    <span style='color:#8b949e;'>Click here to explore partner tools & AI offers</span>
</div>
""", unsafe_allow_text=True)

# Sidebar
st.sidebar.markdown("### ⚙️ **Studio Dashboard**")
st.sidebar.markdown("---")

voice_option = st.sidebar.selectbox(
    "🎙️ **Select Voice Model**", 
    ["ur-PK-AsadNeural (Urdu Male)", "ur-PK-UzmaNeural (Urdu Female)", "en-US-ChristopherNeural (English Male)"]
)

st.sidebar.markdown("---")
pexels_api_key = st.sidebar.text_input("🔑 **Pexels API Key (Optional)**", type="password", help="Enter key for auto HD video clips")

# SIDEBAR AD BANNER
st.sidebar.markdown("<br>", unsafe_allow_text=True)
st.sidebar.markdown("""
<div class='ad-banner'>
    🎯 <b>AdSpot</b><br>
    Monetize Your Traffic
</div>
""", unsafe_allow_text=True)

# Input Area
user_input = st.text_area(
    "✍️️ **Script & Poetry Input:**", 
    height=130, 
    value="Dil se jo baat nikalti hai, asar rakhti hai,\nPar nahin, taaqat-e-parwaaz magar rakhti hai.",
    placeholder="Write your line-by-line script here..."
)

async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        await communicate.save(fp.name)
        return fp.name

def fetch_pexels_video(query, api_key):
    if not api_key:
        return None
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['videos']:
                return data['videos'][0]['video_files'][0]['link']
    except Exception:
        pass
    return None

st.markdown("<br>", unsafe_allow_text=True)

if st.button("🚀 Generate High-Speed Media"):
    if not user_input.strip():
        st.warning("Pehele text enter karein.")
    else:
        lines = [line.strip() for line in user_input.split('\n') if line.strip()]
        
        for idx, line in enumerate(lines, 1):
            st.markdown("<div class='scene-box'>", unsafe_allow_text=True)
            st.markdown(f"### 📍 **Scene {idx}:** *\"{line}\"*")
            
            col1, col2 = st.columns(2)
            
            # Audio
            with col1:
                st.subheader("🔊 **Voice Audio**")
                with st.spinner("Generating Voice..."):
                    voice_code = voice_option.split()[0]
                    audio_path = asyncio.run(generate_audio(line, voice_code))
                    st.audio(audio_path, format="audio/mp3")
            
            # Video Clip
            with col2:
                st.subheader("🎞️ **Matching Clip**")
                if pexels_api_key:
                    with st.spinner("Searching Clip..."):
                        video_url = fetch_pexels_video(line, pexels_api_key)
                        if video_url:
                            st.video(video_url)
                        else:
                            st.info("No matching video clip found.")
                else:
                    st.info("💡 Add Pexels API Key in Sidebar for background video clips.")
            
            st.markdown("</div>", unsafe_allow_text=True)

        # BOTTOM AD BANNER
        st.markdown("""
        <div class='ad-banner'>
            🔥 <b>SUPPORT OUR STUDIO</b> — Click sponsor links above to keep this tool free!
        </div>
        """, unsafe_allow_text=True)
        
        st.success("✅ **Processing Complete!** Download audio & create your video.")
    
