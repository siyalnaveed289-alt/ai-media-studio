import streamlit as st
import asyncio
import os
import requests
import urllib.parse
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Edge TTS
import edge_tts

# MoviePy Safe Imports (No ImageMagick Required)
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
except ImportError:
    try:
        from moviepy.video.io.ImageClip import ImageClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
    except Exception as e:
        st.error(f"MoviePy Import Error: {e}")

st.set_page_config(page_title="Sial AI Stories", page_icon="🎬", layout="wide")

st.title("🎬 Sial AI Stories")
st.subheader("Multi-Voice Audio & AI Video Generator (Production Build)")

# Voices Mapping
VOICES = {
    "👨‍💼 Male Urdu (Asad - Deep Storyteller)": {"id": "ur-PK-AsadNeural", "pitch": "-3Hz", "rate": "-5%"},
    "👩‍💼 Female Urdu (Uzma - Storyteller)": {"id": "ur-PK-UzmaNeural", "pitch": "-1Hz", "rate": "-5%"},
    "🕌 Male Arabic (Hamed - Quran Best)": {"id": "ar-SA-HamedNeural", "pitch": "+0Hz", "rate": "-15%"},
    "👨 Male English (Guy Natural)": {"id": "en-US-GuyNeural", "pitch": "+0Hz", "rate": "+0%"},
    "👩 Female English (Jenny Natural)": {"id": "en-US-JennyNeural", "pitch": "+0Hz", "rate": "+0%"}
}

# Cleanup Old Temporary Files
def cleanup_temp_files():
    temp_files = ["ai_scene.jpg", "scene_captioned.jpg", "voice.mp3", "final_story.mp4"]
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass

# Helper 1: Robust AI Image Generator with Fallback
def generate_ai_image_safe(prompt_text, filename="ai_scene.jpg"):
    try:
        encoded_prompt = urllib.parse.quote(f"cinematic fantasy scene, 8k resolution, highly detailed, {prompt_text}")
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1280&height=720&nologo=true"
        
        response = requests.get(image_url, timeout=20)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
    except Exception as e:
        st.warning(f"AI Image Service Warning: {e}. Fallback background creating...")
    
    # Fallback Image Creation if Network or API fails
    img = Image.new('RGB', (1280, 720), color=(15, 23, 42))
    img.save(filename)
    return filename

# Helper 2: Draw Text directly onto Image (Pillow - 100% Stable)
def add_subtitles_to_image(image_path, text, output_path="scene_captioned.jpg"):
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        try:
            font = ImageFont.truetype("arial.ttf", 34)
        except Exception:
            font = ImageFont.load_default()
            
        wrapped_lines = textwrap.wrap(text, width=40)
        box_height = len(wrapped_lines) * 45 + 30
        
        # Bottom Overlay Box
        draw.rectangle([(0, height - box_height), (width, height)], fill=(0, 0, 0))
        
        y_text = height - box_height + 15
        for line in wrapped_lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
            except Exception:
                line_width = len(line) * 10
                
            x_text = max(10, (width - line_width) / 2)
            draw.text((x_text, y_text), line, font=font, fill=(255, 255, 255))
            y_text += 40
            
        img.save(output_path)
        return output_path
    except Exception as e:
        st.error(f"Subtitle Render Error: {e}")
        return image_path

# Helper 3: Safe Audio Generation
async def generate_audio_async(text, voice_id, pitch, rate, output_file="voice.mp3"):
    communicate = edge_tts.Communicate(text, voice_id, pitch=pitch, rate=rate)
    await communicate.save(output_file)

def run_audio_generator(text, voice_id, pitch, rate, output_file="voice.mp3"):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_audio_async(text, voice_id, pitch, rate, output_file))
    loop.close()

# Helper 4: Safe Video Assembly Engine
def create_cinematic_video_safe(image_path, audio_path, caption_text, output_video="final_story.mp4"):
    captioned_img = add_subtitles_to_image(image_path, caption_text, "scene_captioned.jpg")
    
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    img_clip = ImageClip(captioned_img).set_duration(duration)
    final_video = img_clip.set_audio(audio)

    final_video.write_videofile(
        output_video, 
        fps=24, 
        codec='libx264', 
        audio_codec='aac',
        verbose=False,
        logger=None
    )
    
    # Close audio/video streams to free memory
    audio.close()
    img_clip.close()
    final_video.close()
    return output_video

# UI Layout
st.write("---")
selected_voice_name = st.selectbox("Choose Voice Style:", list(VOICES.keys()))
voice_cfg = VOICES[selected_voice_name]

story_prompt = st.text_area("Story Script / Text (Audio & Video):", 
                             "ایک خوبصورت شہزادی اور آگ اگلنے والا ڈریگن، جو ایک پرسرار قلعے میں رہتے تھے۔")

image_prompt = st.text_input("Visual Scene Prompt (Sirf Video ke liye - English me likhein):", 
                             "a brave warrior girl facing a giant fire breathing dragon in a dark castle, hyperrealistic")

st.write("---")
col_btn1, col_btn2 = st.columns(2)

# ================= BUTTON 1: SIRF AUDIO =================
with col_btn1:
    if st.button("🎙️️ Generate Text-to-Voice (Audio Only)"):
        if story_prompt.strip():
            cleanup_temp_files()
            with st.spinner("Voiceover generate ho raha hai..."):
                try:
                    run_audio_generator(story_prompt, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"], "voice.mp3")
                    
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
                    st.error(f"Audio Generation Error: {e}")
        else:
            st.warning("Pehle Story Script text enter karein.")

# ================= BUTTON 2: AI VIDEO =================
with col_btn2:
    if st.button("🎬 Generate AI Video (Audio + Visuals)"):
        if story_prompt.strip() and image_prompt.strip():
            cleanup_temp_files()
            
            with st.spinner("1/3: AI Visual Scene Draw Ho Raha Hai..."):
                img_file = generate_ai_image_safe(image_prompt, "ai_scene.jpg")
                
            if img_file and os.path.exists(img_file):
                st.image(img_file, caption="AI Generated Unique Visual Scene", use_column_width=True)
                
                with st.spinner("2/3: Voiceover Generate Ho Raha Hai..."):
                    try:
                        run_audio_generator(story_prompt, voice_cfg["id"], voice_cfg["pitch"], voice_cfg["rate"], "voice.mp3")
                    except Exception as e:
                        st.error(f"Audio Error: {e}")
                
                if os.path.exists("voice.mp3"):
                    with st.spinner("3/3: HD MP4 Video Render Ho Rahi Hai..."):
                        try:
                            video_file = create_cinematic_video_safe("ai_scene.jpg", "voice.mp3", story_prompt, "final_story.mp4")
                            
                            if os.path.exists(video_file):
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
    
( video ko b generate kara cinema or 3d cartoon videos ma b )
( jis caractor ki picture bajy jayw us ko same wasa hw 100% natural ma he use karo )
