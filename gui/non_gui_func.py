from random import randint
from deepface import DeepFace
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import os
from PIL import Image
import concurrent.futures
import time

def clear_gpu_memory():
    """Clears GPU memory to free up resources."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

# Background Music Generation Function
def generate_music(model, description, output_dir="generated_music"):
    """Runs music generation in a separate process to avoid UI lag."""
    try:
        # Generate the initial audio
        print('Generating Music...')
        start_time = time.time()
        generated_wav = model.generate([description])  # Pass description as a list

        # Loop the audio 3 times
        wav_repeated = torch.cat([generated_wav[0]] * 3, dim=-1)  # Repeat the waveform

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the looped audio to a file with a descriptive name
        file_name = f"{description.replace(' ', '_')}.wav"
        output_path = os.path.join(output_dir, "gen_looped")
        audio_write(output_path, wav_repeated.cpu(), model.sample_rate)
        end_time = time.time()
        print('Generation Time Elapsed: ', end_time-start_time)
        return output_path  # Return the file path
    except Exception as e:
        return None  # Return None if music generation fails
    
def capture_emotions(photo):
    description = None
    emotions = None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_img:
        image = Image.fromarray(photo)
        temp_img_path = temp_img.name
        # Save the image to the temporary file
        image.save(temp_img_path)
        

        # Run DeepFace analysis
        try:
            result = DeepFace.analyze(img_path=temp_img_path, actions=["emotion"])
            emotions = result[0]["emotion"]
            dominant_emotion = max(emotions, key=emotions.get)
        except Exception as e:
            print(f"Error analyzing image: {e}")

        # Display emotion results
        print("Detected Emotions")

        # Generate Music Prompt
        description = f"Generate a background track with no melody for a person feeling {dominant_emotion}"
    return emotions, description