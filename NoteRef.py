import sound
import threading
import time

KEY_OFFSET = {'C':48, 'D': 50, 'E': 52, 'F':53, 'G':55, 'A': 57, 'B': 59}
SCALE_MAPPINGS = {'major': [[0,2,4,5,7], [0,4,7,11,12], [5,7,9,10,12]], 
                  'minor': [[0,2,3,5,7], [0,3,7,8,12], [5,7,8,10,12]]}
#SCALE_STEPPING = {'major': [0,2,4,5,7,9,11,12], 'minor': [0,2,3,5,7,8,10,12]}

if __name__ == "__main__":
    synth = sound.Synth()

    key = "G major"
    finger_map = 1

    base_note = KEY_OFFSET[key.split()[0]]
    scale = key.split()[1]
    mapping = SCALE_MAPPINGS[scale][finger_map] #Mapping changes based on some user control (swipe gesture or from interface)

    for i in range(5):  #i correspondes to finger press received from client
        threading.Thread(target=synth.play_note, args=(base_note + mapping[i],)).start()
        time.sleep(0.5)
