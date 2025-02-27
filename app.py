import streamlit as st
from deepface import DeepFace
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import os
import concurrent.futures
import socket
import threading
import sound
import keyboard

# Constants for ESP32 communication
ESP32_IP = '192.168.217.79'
PORT = 10000
NOTE_PRESSES = [60, 62, 64]

# Streamlit App Title
st.title("Emotion & Gesture Driven Music Performance")

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
    

# ESP32 Client Function (Runs in Background)
def run_client():
    """Runs in the background to communicate with ESP32."""
    synth = sound.Synth()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ESP32_IP, PORT))
    print("Connected to ESP32 server")

    try:
        while True:
            if keyboard.is_pressed('space'):
                data = "r"
                print("Resetting sensors")
                client_socket.send(data.encode())
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if message.split()[0] == "press":
                print("Note press on sensor", message.split()[1])
                # Update session state with the note to play
                st.session_state["note_to_play"] = NOTE_PRESSES[int(message.split()[1])]
            elif message == "swipe left":
                print("Hand swipe left")
                # Trigger a GUI method (e.g., change emotion)
                st.session_state["swipe_direction"] = "left"
            elif message == "swipe right":
                print("Hand swipe right")
                # Trigger a GUI method (e.g., change emotion)
                st.session_state["swipe_direction"] = "right"
            elif message.split()[0] == "disconnected":
                print("Sensor", message.split()[1], "is disconnected, check wiring and reset.")
    except KeyboardInterrupt:
        print("Connection closed by client")
    client_socket.close()

# Start the ESP32 client in a background thread
if "client_thread" not in st.session_state:
    st.session_state.client_thread = threading.Thread(target=run_client, daemon=True)
    st.session_state.client_thread.start()
    

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
                
# Handle ESP32 events in the UI
if "note_to_play" in st.session_state:
    st.write(f"Playing note: {st.session_state.note_to_play}")
    # Call a method to play the note (e.g., using a sound library)
    # synth.play_note(st.session_state.note_to_play)
    del st.session_state["note_to_play"]  # Clear the note after playing

if "swipe_direction" in st.session_state:
    st.write(f"Hand swipe detected: {st.session_state.swipe_direction}")
    # Trigger a GUI action based on swipe direction
    del st.session_state["swipe_direction"]  # Clear the swipe direction after handling
