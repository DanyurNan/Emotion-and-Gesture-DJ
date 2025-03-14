from random import randint
from deepface import DeepFace
import torch
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
import tempfile
import os
import wave
from PIL import Image
import concurrent.futures
import time

def clear_gpu_memory():
    """Clears GPU memory to free up resources."""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

# Background Music Generation Function
def generate_music(model, description, index, output_dir="generated_music"):
    """Runs music generation in a separate process to avoid UI lag."""
    try:
        # Generate the initial audio
        print('Generating Music...')
        start_time = time.time()
        generated_wav = model.generate([description], progress=True)  # Pass description as a list

        # Loop the audio 3 times
        wav_repeated = torch.cat([generated_wav[0]] * 3, dim=-1)  # Repeat the waveform

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the looped audio to a file with a descriptive name
        output_path = os.path.join(output_dir, f"audio{index}")
        audio_write(output_path, wav_repeated.cpu(), model.sample_rate)
        end_time = time.time()
        print('Generation Time Elapsed: ', end_time-start_time)
        return f'{output_path}.wav'  # Return the file path
    except Exception as e:
        return None  # Return None if music generation fails
    
def capture_emotions(photo):
    success = 0
    emotions = None
    description = None
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
            success = 1
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return success, emotions, description

        # Display emotion results
        print("Detected Emotions")

        # Generate Music Prompt
        description = f"Generate a background track with no melody for a person feeling {dominant_emotion}"
    return success, emotions, description

def get_wav_length(file_path):
    try:
        with wave.open(file_path, 'r') as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)
            return duration
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    model = MusicGen.get_pretrained("facebook/musicgen-small")
    model.set_generation_params(duration=7) 
    apath = generate_music(model, "lol", 0)
    duration = get_wav_length(apath)
    print(f"The duration of the audio file is: {duration} seconds")
    print(apath)
