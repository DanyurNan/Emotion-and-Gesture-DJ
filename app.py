import streamlit as st
from deepface import DeepFace
import torch
import multiprocessing
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import os

# Streamlit App Title
st.title("Emotion & Gesture Controlled DJ")

# Initialize webcam using Streamlit’s built-in camera input
photo = st.camera_input("Take a Photo")

# Load MusicGen Model (Cached for Speed)
@st.cache_resource
def load_model():
    model = MusicGen.get_pretrained("facebook/musicgen-small")
    model.set_generation_params(duration=7)  # Faster generation (7 seconds)
    return model

model = load_model()

def clear_gpu_memory():
    """Clears GPU memory to free up resources."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

# Background Music Generation Function
def generate_music(description, result_queue):
    """Runs music generation in a separate process to avoid UI lag."""
    try:
        # Generate the initial audio
        generated_wav = model.generate([description])  # Pass description as a list

        # Loop the audio 3 times
        wav_repeated = torch.cat([generated_wav[0]] * 3, dim=-1)  # Repeat the waveform

        # Save the looped audio to a file
        output_dir = "generated_music"  # Directory to save the music file
        os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
        output_path = os.path.join(output_dir, "generated_music_looped.wav")  # File path
        audio_write(output_path, wav_repeated.cpu(), model.sample_rate)

        result_queue.put(output_path)  # Send the file path to the main process
    except Exception as e:
        result_queue.put(None)  # Send None if music generation fails
        raise e

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
        description = f"Generate an ambient track for a person feeling {dominant_emotion}"
        st.session_state["music_description"] = description
        
    clear_gpu_memory()

    # Music Generation Button
    if st.button("Generate Music"):
        with st.spinner("Generating Music..."):
            result_queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=generate_music, args=(description, result_queue))
            process.start()
            process.join()  # Wait for the process to complete

            # Retrieve the generated music file path
            music_file = result_queue.get()

            if music_file:  # Check if music generation was successful
                st.session_state["music_file"] = music_file
                st.success("Music generated and looped 3 times!")

                # Read the saved music file and play it
                audio_file = open("generated_music\generated_music_looped.wav.wav", 'rb').read()
                st.audio(audio_file, format='audio/wav')
            else:
                st.error("Failed to generate music. Please try again.")
