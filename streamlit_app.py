import streamlit as st
import asyncio
import os
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Edge TTS
import edge_tts

# MoviePy Safe Imports
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip

st.set_page_config(page_title="Sial AI Stories", page_icon="🎬", layout="wide")

st.title("🎬 Sial AI Video & Voice Studio")
st.subheader("Pexels Moving Video Engine + Edge-TTS Voiceover")

VOICES = {
    "👨‍💼 Male Urdu (Asad)": {"id": "ur-PK-AsadNeural", "pitch": "-3Hz", "rate": "-5%"},
    "👩‍💼 Female Urdu (Uzma)": {"id": "ur-PK-UzmaNeural", "pitch": "-1Hz", "rate": "-5%"},
    "🕌 Male Arabic (Hamed)": {"id": "ar-SA-HamedNeural", "pitch": "+0Hz", "rate": "-15%"},
    "👨 Male English (Guy)": {"id": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "+0%"},
    "👩 Female English (Jenny)": {"id": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "+0%"}
}

def cleanup():
    for f in ["stock_video.mp4", "voice.mp3", "final_story.mp4"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

# REAL MOVING STOCK VIDEO GENERATOR (PEXELS API)
def fetch_pexels_video(query, pexels_api_key=""):
    if not pexels_api_key:
        # Fallback public endpoint query
        search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
        headers = {"Authorization": "563492ad6f917000010000013d5df025a1f64f33b1e3e5668e2786bc"} # Public demo key
    else:
        search_url = f"https://api.pexels.com/videos/search?query={query}&per_page=1"
        headers = {"Authorization": pexels_api_key}

    res = requests.get(search_url, headers=headers, timeout=20)
    if res.status_code == 200:
        data = res.json()
        if data.get("videos"):
            video_files = data["videos"][0]["video_files"]
            # Pick HD file
            selected_video = next((v for v in video_files if v.get("width") == 1280 or v.get("width") == 1920), video_files[0])
            video_url = selected_video["link"]
            
            video_res = requests.get(video_url, stream=True)
            with open("stock_video.mp4", "wb") as f:
                for chunk in video_res.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
            return "stock_video.mp4"
    
    raise Exception("Moving Video search failed. Please try a different video prompt keyword.")

# VOICE GENERATOR
async def generate_voice_async(text, voice_id, pitch, rate):
    communicate = edge_tts.Communicate(text, voice_id, pitch=pitch, rate=rate)
    await communicate.save("voice.mp3")

def run_voice(text, voice_id, pitch, rate):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_voice_async(text, voice_id, pitch, rate))
    loop.close()

# VIDEO + AUDIO COMPOSITOR
def merge_video_and_audio(video_path, audio_path, output_path="final_story.mp4"):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    # Loop video if audio duration is longer
    if audio.duration > video.duration:
        loops_needed = int(audio.duration / video.duration) + 1
        video = video.loop(n=loops_needed)
    
    final_clip = video.set_duration(audio.duration).set_audio(audio)
    
    final_clip.write_videofile(
        output_path, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac',
        verbose=False,
        logger=None
    )
    
    video.close()
    audio.close()
    final_clip.close()
    return output_path

st.write("---")
selected_voice = st.selectbox("Select Voice:", list(VOICES.keys()))
voice_cfg = VOICES[selected_voice]

story_text = st.text_area("Story Script (Audio Voiceover):", "ایک خوبصورت قلعے پر پرواز کرتا ہوا ڈریگن۔")
video_query = st.text_input("Moving Video Keyword (e.g., castle, dragon, space, dark forest):", "castle")

if st.button("🚀 Generate Moving Stock Video + Voiceover"):
    if story_text.strip() and video_query.strip():
        cleanup()
        
        with st.spinner("1/3: Real HD Moving Video Clip Download Ho Rahi Hai..."):
            v_file = fetch_pexels_video(video_query)
            
        with st.spinner("2/3: Voiceover Generate Ho Raha Hai..."):
            run_voice(story_text, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"])
            
        with st.spinner("3/3: Merging Video & Audio..."):
            final_file = merge_video_and_audio(v_file, "voice.mp3", "final_story.mp4")
            
        st.success("🎉 FINAL MOVING VIDEO IS READY!")
        st.video(final_file)
        
        with open(final_file, "rb") as file:
            st.download_button("📥 Download MP4 Video", data=file, file_name="sial_moving_story.mp4", mime="video/mp4")
            
