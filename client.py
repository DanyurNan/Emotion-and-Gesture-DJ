import socket
import time
import keyboard
import sound
import threading

ESP32_IP = '192.168.26.79' 
PORT = 10000
#NOTE_PRESSES = [60, 62, 64, 65, 67, 69]
KEY_OFFSET = {'C':48, 'D': 50, 'E': 52, 'F':53, 'G':55, 'A': 57, 'B': 59}
SCALE_MAPPINGS = {'major': [[0,2,4,5,7], [0,4,7,11,12], [5,7,9,10,12]], 
                  'minor': [[0,2,3,5,7], [0,3,7,8,12], [5,7,8,10,12]]}

base_note = KEY_OFFSET['C']
scale = 'major'
mapping = SCALE_MAPPINGS[scale][0] 

def run_client(): #CALLED WHEN GUI IS CALLED, SHOULD RUN IN THE BACKGROUND AS THREAD
    synth = sound.Synth()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ESP32_IP, PORT))
    print("Connected to ESP32 server")

    try:
        while True:
            if keyboard.is_pressed('space'):
                data = "r"
                print("reseting sensors")
                client_socket.send(data.encode())
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if message.split()[0] == "press":
                print("Note press on sensor", message.split()[1])
                threading.Thread(target=synth.play_note, args=(base_note + mapping[int(message.split()[1])],)).start() #SHOULD BE SENT TO METHOD IN GUI INSTEAD, GUI CHOOSES NOTE TO PLAY
            elif message == "swipe left":
                print("Hand swipe left") 
                mapping = SCALE_MAPPINGS[scale][0] 
            elif message == "swipe right":
                print("Hand swipe right") 
                mapping = SCALE_MAPPINGS[scale][2] 
            elif message == "swipe forward":
                print("Hand swipe forward") 
                mapping = SCALE_MAPPINGS[scale][1] 
            elif message.split()[0] == "disconnected":
                print("Sensor", message.split()[1], "is disconnected, check wiring and reset.")
    except KeyboardInterrupt:
        print("Connection closed by client")
    client_socket.close()

if __name__ == "__main__": #TESTING PURPOSES
    run_client()