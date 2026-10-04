import streamlit as st
import asyncio
import edge_tts
import os
import requests
import urllib.parse
from PIL import Image

# MoviePy import compatibility fix
try:
    from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip
except ImportError:
    from moviepy.video.io.ImageClip import ImageClip
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.VideoClip import TextClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

st.set_page_config(page_title="Sial AI Stories", page_icon="🎬", layout="wide")

st.title("🎬 Sial AI Stories")
st.subheader("Multi-Voice Audio & AI Video Generator")

# Voices Mapping
VOICES = {
    "👨‍💼 Male Urdu (Asad - Deep Storyteller)": {"id": "ur-PK-AsadNeural", "pitch": "-3Hz", "rate": "-5%"},
    "👩‍💼 Female Urdu (Uzma - Storyteller)": {"id": "ur-PK-UzmaNeural", "pitch": "-1Hz", "rate": "-5%"},
    "🕌 Male Arabic (Hamed - Quran Best)": {"id": "ar-SA-HamedNeural", "pitch": "+0Hz", "rate": "-15%"},
    "👨 Male English (Guy Natural)": {"id": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "+0%"},
    "👩 Female English (Jenny Natural)": {"id": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "+0%"}
}

# Helper 1: Free AI Image Generator (Pollinations AI)
def generate_ai_image(prompt_text, filename="scene.jpg"):
    try:
        encoded_prompt = urllib.parse.quote(f"cinematic fantasy scene, 8k resolution, highly detailed, {prompt_text}")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
        
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        st.error(f"Image Generation Error: {e}")
    return None

# Helper 2: Audio Generator
async def generate_audio(text, voice_id, pitch, rate, output_file="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice_id, pitch=pitch, rate=rate)
    await communicate.save(output_file)

# Helper 3: Video Assembly Engine
def create_cinematic_video(image_path, audio_path, caption_text, output_video="final_story.mp4"):
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Load AI Generated Image
    img_clip = ImageClip(image_path).set_duration(duration)

    # Subtitles / Captions Overlay
    txt_clip = TextClip(caption_text, fontsize=28, color='white', bg_color='black', 
                        size=(1100, None), method='caption')
    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(duration)

    # Combine Image + Text + Audio
    final_video = CompositeVideoClip([img_clip, txt_clip])
    final_video = final_video.set_audio(audio)

    final_video.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac')
    return output_video

# UI Inputs
st.write("---")
selected_voice_name = st.selectbox("Choose Voice Style:", list(VOICES.keys()))
voice_cfg = VOICES[selected_voice_name]

story_prompt = st.text_area("Story Script / Text (Audio aur Video dono ke liye):", 
                             "ایک خوبصورت شہزادی اور آگ اگلنے والا ڈریگن، جو ایک پرسرار قلعے میں رہتے تھے۔")

image_prompt = st.text_input("Visual Scene Prompt (Sirf Video ke liye - English me likhein):", 
                             "a brave warrior girl facing a giant fire breathing dragon in a dark castle, hyperrealistic")

st.write("---")
col_btn1, col_btn2 = st.columns(2)

# BUTTON 1: SIRF AUDIO GENERATE KAREIN
with col_btn1:
    if st.button("🎙️ Generate Text-to-Voice (Audio Only)"):
        if story_prompt.strip():
            with st.spinner("Voiceover generate ho raha hai..."):
                try:
                    if os.path.exists("voice.mp3"):
                        os.remove("voice.mp3")
                    
                    asyncio.run(generate_audio(story_prompt, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"], "voice.mp3"))
                    
                    if os.path.exists("voice.mp3"):
                        st.success("🎉 Audio Successfully Ban Gayi!")
                        st.audio("voice.mp3", format="audio/mp3")
                        
                        with open("voice.mp3", "rb") as file:
                            st.download_button(
                                label="📥 Download Audio MP3",
                                data=file,
                                file_name="sial_ai_voice.mp3",
                                mime="audio/mp3"
                            )
                except Exception as e:
                    st.error(f"Audio Error: {e}")
        else:
            st.warning("Pehle Story Script text enter karein.")

# BUTTON 2: AI VIDEO GENERATE KAREIN
with col_btn2:
    if st.button("🎬 Generate AI Video (Audio + Visuals)"):
        if story_prompt.strip() and image_prompt.strip():
            with st.spinner("1/3: AI Visual Scene Draw Ho Raha Hai..."):
                img_file = generate_ai_image(image_prompt, "ai_scene.jpg")
                
            if img_file and os.path.exists(img_file):
                st.image(img_file, caption="AI Generated Unique Visual Scene", use_column_width=True)
                
                with st.spinner("2/3: Voiceover Generate Ho Raha Hai..."):
                    asyncio.run(generate_audio(story_prompt, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"], "voice.mp3"))
                
                with st.spinner("3/3: Video Render Ho Rahi Hai..."):
                    try:
                        video_file = create_cinematic_video("ai_scene.jpg", "voice.mp3", story_prompt, "sial_ai_story.mp4")
                        
                        st.success("🎉 HD Video Successfully Ban Gayi!")
                        st.video(video_file)
                        
                        with open(video_file, "rb") as file:
                            st.download_button(
                                label="📥 Download HD MP4 Video",
                                data=file,
                                file_name="sial_ai_cinematic_story.mp4",
                                mime="video/mp4"
                            )
                    except Exception as e:
                        st.error(f"Video Assembly Error: {e}")
            else:
                st.error("Image generate nahi ho saki, dobara try karein.")
        else:
            st.warning("Video ke liye Script aur Visual Scene Prompt dono enter karein.")
                         
