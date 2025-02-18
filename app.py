import streamlit as st
from deepface import DeepFace
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import os
import concurrent.futures

st.title("Emotion & Gesture Controlled DJ")

photo = st.camera_input("Take a Photo")

# Load MusicGen Model (Cached for Speed)
@st.cache_resource
def load_model():
    model = MusicGen.get_pretrained("facebook/musicgen-small")
    model.set_generation_params(duration=7) 
    return model

model = load_model()

def clear_gpu_memory():
    """Clears GPU memory to free up resources."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

# Background Music Generation Function
def generate_music(description, output_dir="generated_music"):
    """Runs music generation in a separate process to avoid UI lag."""
    try:
        # Generate the initial audio
        generated_wav = model.generate([description])  # Pass description as a list

        # Loop the audio 3 times
        wav_repeated = torch.cat([generated_wav[0]] * 3, dim=-1)  # Repeat the waveform

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the looped audio to a file with a descriptive name
        file_name = f"{description.replace(' ', '_')}.wav"
        output_path = os.path.join(output_dir, "gen_looped.wav")
        audio_write(output_path, wav_repeated.cpu(), model.sample_rate)
        return output_path  # Return the file path
    except Exception as e:
        return None  # Return None if music generation fails

# Streamlit UI Logic
if photo:
    with st.spinner("Analyzing Image..."):
        # Save the image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
            temp_img.write(photo.getvalue())
            temp_img_path = temp_img.name

        # Run DeepFace analysis
        try:
            result = DeepFace.analyze(img_path=temp_img_path, actions=["emotion"])
            emotions = result[0]["emotion"]
            dominant_emotion = max(emotions, key=emotions.get)
        except Exception as e:
            st.error(f"Error analyzing image: {e}")
            st.stop()

        # Display emotion results
        st.subheader("Detected Emotions")
        for emotion, score in emotions.items():
            st.write(f"**{emotion.capitalize()}**: {score:.2f}%")

        # Generate Music Prompt
        description = f"Generate a background track with no melody for a person feeling {dominant_emotion}"
        st.session_state["music_description"] = description
        
    clear_gpu_memory()

    # Music Generation Button
    if st.button("Generate Music"):
        with st.spinner("Generating Music..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(generate_music, description)
                music_file = future.result()

            if music_file:  # Check if music generation was successful
                st.session_state["music_file"] = music_file
                st.success(f"Music generated and saved as {music_file}")

                # Read the saved music file and play it
                audio_file = open("generated_music/gen_looped.wav.wav", 'rb').read()
                st.audio(audio_file, format='audio/wav')
            else:
                st.error("Failed to generate music. Please try again.")
