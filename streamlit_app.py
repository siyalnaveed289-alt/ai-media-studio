import streamlit as st
import asyncio
import edge_tts
import os

# Page Configuration
st.set_page_config(page_title="AI Media Studio", page_icon="🎬", layout="wide")

st.title("🎬 AI Media Studio")
st.markdown("### Persistent Cinematic & Poem Video Generator")

# Sidebar for Voice Settings
st.sidebar.header("🎙️ Voice & Audio Settings")
language = st.sidebar.selectbox("Language / Language Style", ["Urdu (Pakistan) - Female", "English (US) - Male", "English (UK) - Female"])

voice_map = {
    "Urdu (Pakistan) - Female": "ur-PK-UzmaNeural",
    "English (US) - Male": "en-US-ChristopherNeural",
    "English (UK) - Female": "en-GB-SoniaNeural"
}

selected_voice = voice_map[language]

# Main Prompt Area
st.subheader("📝 Enter Poetry Verses or Video Prompts")
user_input = st.text_area(
    "Write text line-by-line (each line generates separate narration):",
    height=150,
    value="Dil se jo baat nikalti hai, asar rakhti hai,\nPar nahin, taaqat-e-parwaaz magar rakhti hai."
)

# Function for Async Edge TTS Generation
async def generate_audio(text, voice, output_filename):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

# Generate Button
if st.button("🚀 Generate Studio Media & Narration", type="primary"):
    if not user_input.strip():
        st.error("Kripya pehle text ya poetry enter karein!")
    else:
        lines = [line.strip() for line in user_input.split("\n") if line.strip()]
        st.info(f"Processing {len(lines)} scenes/lines...")
        
        progress_bar = st.progress(0)
        
        for idx, line in enumerate(lines):
            st.markdown(f"#### 🎬 Scene {idx + 1}: *\"{line}\"*")
            
            # Generate Audio File
            audio_file = f"scene_{idx+1}.mp3"
            try:
                asyncio.run(generate_audio(line, selected_voice, audio_file))
                
                # Display Audio Player
                if os.path.exists(audio_file):
                    st.audio(audio_file, format="audio/mp3")
                    st.caption("✅ Audio Narration Generated Successfully!")
            except Exception as e:
                st.error(f"Error generating audio for Scene {idx+1}: {e}")
            
            progress_bar.progress((idx + 1) / len(lines))
            
        st.success("🎉 All Scenes Processed! Media Studio Ready.")
        
