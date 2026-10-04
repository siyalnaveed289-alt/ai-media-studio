import streamlit as st
import asyncio
import os
import requests
import time

# Edge TTS
import edge_tts

# MoviePy Safe Imports
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except ImportError:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip

st.set_page_config(page_title="Sial AI Stories", page_icon="🎬", layout="wide")

st.title("🎬 Sial AI Moving Video Generator")
st.subheader("Real AI Video + Multi-Voice Script Engine")

VOICES = {
    "👨‍💼 Male Urdu (Asad)": {"id": "ur-PK-AsadNeural", "pitch": "-3Hz", "rate": "-5%"},
    "👩‍💼 Female Urdu (Uzma)": {"id": "ur-PK-UzmaNeural", "pitch": "-1Hz", "rate": "-5%"},
    "🕌 Male Arabic (Hamed)": {"id": "ar-SA-HamedNeural", "pitch": "+0Hz", "rate": "-15%"},
    "👨 Male English (Guy)": {"id": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "+0%"},
    "👩 Female English (Jenny)": {"id": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "+0%"}
}

def cleanup():
    for f in ["raw_ai_video.mp4", "voice.mp3", "final_story.mp4"]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

# REAL MOVING AI VIDEO GENERATOR
def generate_real_ai_video(prompt):
    st.info("⌛ Pollinations AI Video Model se real moving MP4 render ho rahi hai...")
    
    # Clean and encode prompt for AI Video Engine
    formatted_prompt = requests.utils.quote(f"cinematic footage, highly detailed, realistic motion, {prompt}")
    video_url = f"https://image.pollinations.ai/prompt/{formatted_prompt}?model=video&width=1280&height=720&nologo=true"
    
    response = requests.get(video_url, stream=True, timeout=120)
    
    if response.status_code == 200:
        with open("raw_ai_video.mp4", "wb") as f:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
        return "raw_ai_video.mp4"
    else:
        raise Exception(f"AI Video Server Response Failed (Status Code: {response.status_code})")

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
    
    # Loop video if audio is longer than AI video clip
    if audio.duration > video.duration:
        loops_needed = int(audio.duration / video.duration) + 1
        video = video.loop(n=loops_needed)
    
    # Trim video to match exact audio length
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

story_text = st.text_area("Story Script (Audio Voiceover):", "ایک آگ اگلنے والا ڈریگن آسکر کے قلعے پر پرواز کر رہا ہے۔")
video_prompt = st.text_input("Visual Video Prompt (English only for AI Video):", "a massive red dragon flying over a medieval castle, breathing fire, cinematic high detail")

if st.button("🚀 Generate Real Moving AI Video"):
    if story_text.strip() and video_prompt.strip():
        cleanup()
        
        # Step 1: Real AI Video Generation
        with st.spinner("1/3: Real AI Moving Video MP4 generate ho rahi hai... (Takes up to 1-2 mins)"):
            ai_video_file = generate_real_ai_video(video_prompt)
        
        st.video(ai_video_file)
        st.success("✅ Raw AI Moving Video Clip Ready!")
        
        # Step 2: Voice Generation
        with st.spinner("2/3: Voiceover generate ho rahi hai..."):
            run_voice(story_text, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"])
            
        # Step 3: Merging Audio & Video
        with st.spinner("3/3: Video aur Voice Synchronize ho rahe hain..."):
            final_file = merge_video_and_audio(ai_video_file, "voice.mp3", "final_story.mp4")
            
        st.write("---")
        st.success("🎉 FINAL REAL MOVING AI VIDEO IS READY!")
        st.video(final_file)
        
        with open(final_file, "rb") as file:
            st.download_button("📥 Download Final MP4 Video", data=file, file_name="sial_real_ai_video.mp4", mime="video/mp4")
            
    else:
        st.warning("Script aur Video Prompt dono enter karein.")
