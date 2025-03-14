import pygame
import time

def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()

def pause_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()

def volume_set(vol):
    pygame.mixer.music.set_volume(vol)
    
if __name__ == "__main__":
    play_audio("generated_music/nice.wav")
    print("audio paused")
    time.sleep(5)
    pause_audio()
    time.sleep(2)
    volume_set(0.1)
    time.sleep(5)
    pygame.mixer.music.stop()
