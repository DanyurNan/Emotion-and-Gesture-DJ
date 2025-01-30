#import fluidsynth
import time
import threading
import tinysoundfont

SYNTH_OFFSET = 12

class Synth():
    def __init__(self):
        self.fs = tinysoundfont.Synth()
        self.sfid = self.fs.sfload('soundfont\MusicLab_Acoustic_Guitars.sf2') #File that creates the sound for the notes, we could add more and change depending on emotion(?)
        self.fs.program_select(0, self.sfid, 0, 25)
        #self.fs.setting('synth.gain', 0.999999)
        self.fs.start()
    
    def play_note(self, note):
        self.fs.noteon(0, note+SYNTH_OFFSET, 127)
        time.sleep(3.0)
        self.fs.noteoff(0, note+SYNTH_OFFSET)



if __name__ == "__main__": #TESTING PURPOSES
    synth = Synth()