import socket
import time
import keyboard
import sound
import threading

'''Test client script to connect to the glove ESP32 server, read in gestures, and convert them into music notes
Full implementation along with application interface in app.py'''

# Constants for ESP32 communication
ESP32_IP = '192.168.26.79' 
PORT = 10000

# Musical Key and Scale Mappings
KEY_OFFSET = {'C':48, 'D': 50, 'E': 52, 'F':53, 'G':55, 'A': 57, 'B': 59}
SCALE_MAPPINGS = {'major': [[0,2,4,5,7], [0,4,7,11,12], [5,7,9,11,12]], 
                  'minor': [[0,2,3,5,7], [0,3,7,8,12], [5,7,8,10,12]]}

# Test Intialization of Key and Scale
base_note = KEY_OFFSET['D']
scale = 'major'
mapping = SCALE_MAPPINGS[scale][0]

running = True

def change_key(gen_key, gen_scale):
    base_note = KEY_OFFSET[gen_key]
    scale = gen_scale

def run_client():
    synth = sound.Synth() # Initialize Soundfont Script

    # Connect to ESP32 Server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ESP32_IP, PORT))
    mapping = SCALE_MAPPINGS[scale][0] 
    print("Connected to ESP32 server")

    # Check for ESP32 Messages
    while running:

        # Reset Sensors if Disconnected
        if keyboard.is_pressed('space'):
            data = "r"
            print("reseting sensors")
            client_socket.send(data.encode())
        data = client_socket.recv(1024)
        if not data:
            break

        message = data.decode().strip()

        # Check for Finger Movement
        if message.split()[0] == "press":
            print("Note press on sensor", message.split()[1] + ", Note", base_note + mapping[int(message.split()[1])]) # Converts Finger Number to Pitch using Mapping
            threading.Thread(target=synth.play_note, args=(base_note + mapping[int(message.split()[1])],)).start()

        # Check for Hand Swipes to Change Note Mapping
        elif message == "swipe left":
            print("Hand swipe left") 
            mapping = SCALE_MAPPINGS[scale][0] 
        elif message == "swipe right":
            print("Hand swipe right") 
            mapping = SCALE_MAPPINGS[scale][2] 
        elif message == "swipe forward":
            print("Hand swipe forward") 
            mapping = SCALE_MAPPINGS[scale][1] 

        # Displays Message if Sensor is Disconnected
        elif message.split()[0] == "disconnected":
            print("Sensor", message.split()[1], "is disconnected, check wiring and reset.")

    print("Connection closed by client")
    client_socket.close()

def close_client():
    global running
    running = False


if __name__ == "__main__":
    run_client()