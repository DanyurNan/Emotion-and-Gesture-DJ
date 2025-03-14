import pygame
import time

def play_audio(audio_path):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    pygame.mixer.music.pause()

def pause_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
    
if __name__ == "__main__":
    play_audio("C:/Users/erice/Desktop/audiocraft/generated_music/gen_looped.wav")
    pause_audio()
    print("audio paused")
    time.sleep(5)
    pause_audio()
    time.sleep(5)
    pygame.mixer.music.stop()