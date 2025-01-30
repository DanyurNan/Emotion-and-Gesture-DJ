import cv2
import streamlit as st
from deepface import DeepFace
import numpy as np
import torch
from random import randint
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import time
import io

# Streamlit app title
st.title("Webcam Emotion and Demographics Analyzer")

# Initialize webcam
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Emotion to musical pattern mapping
PATTERN_MAPPING = {
    'disgust': 'minor', 'fear': 'minor', 'happy': 'major', 'sad': 'minor', 'surprise': 'major', 'neutral': 'major'
}
KEY = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Initialize MusicGen model
model = MusicGen.get_pretrained('facebook/musicgen-small')
model.set_generation_params(duration=20)  # Duration of the music

# Button to capture a frame
if st.button("Capture Photo"):
    ret, frame = capture.read()
    
    if ret:
        # Convert the frame to RGB and display it
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, caption='Captured Photo', use_column_width=True)
        
        # Save the frame as an image
        cv2.imwrite("photo.png", frame)
        st.success("Photo saved as 'photo.png'")

        # Analyze the image using DeepFace
        with st.spinner('Analyzing the photo...'):
            result = DeepFace.analyze(img_path='photo.png', actions=['emotion', 'gender', 'race'])
            st.write(result)

            # Extract emotions and dominant characteristics
            emotions = result[0]['emotion']
            dominant_gender = result[0]['dominant_gender']
            dominant_race = result[0]['dominant_race']

            # Display emotion percentages
            emotion_percentages = {emotion: f"{score:.2f}%" for emotion, score in emotions.items()}
            st.subheader("Emotions in Percentages:")
            for emotion, percentage in emotion_percentages.items():
                st.write(f"{emotion.capitalize()}: {percentage}")

            # Generate music description based on emotion
            description = ["Generate a background track with no melody for a person who is "]
            for emotion, percentage in emotion_percentages.items():
                description.append(f"{emotion.capitalize()}: {percentage} ")

            # Add dominant gender and race to the description
            # description.append(f"Dominant Gender: {dominant_gender}")
            # description.append(f"Dominant Race: {dominant_race}")

            # Map dominant emotion to chord progression
            dominant_emotion = max(emotions, key=emotions.get)
            chord_progression = PATTERN_MAPPING.get(dominant_emotion, 'major')

            # Select a random key for the track
            key = KEY[randint(0, 6)]

            # Final music description
            description.append(f"In the key of {key} {chord_progression}")

            # Print the description to the console for debugging
            st.subheader("Generated Music Description:")
            st.write(" ".join(description))

            # Generate the background music (only one track)
            st.spinner("Generating music...")
            start_time = time.time()
            wav = model.generate(description)  # Only generates one audio track
            
            # Loop the generated music by repeating the audio
            wav_repeated = torch.cat([wav[0]] * 3, dim=-1) 
            
            # Save the generated audio as one file
            audio_write('generated_music_looped', wav_repeated.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
            
            end_time = time.time()
            st.success(f"Music generated and saved as 'generated_music_looped.wav' in {end_time - start_time:.2f} seconds!")

            # Display audio player for the generated music
            audio_file = open('generated_music_looped.wav', 'rb').read()
            st.audio(audio_file, format='audio/wav')

# Release the capture when done
capture.release()