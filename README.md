# Emotion and Gesture-Driven Music Performance

## Overview
This project is a Streamlit-based web application that integrates **emotion detection**, **AI-generated music**, and **gesture-driven interaction** using an ESP32 device. The application allows users to:
1. Capture an image using their webcam.
2. Detect emotions from the image using DeepFace.
3. Generate background music based on the detected emotion using the MusicGen model.
4. Interact with the system using gestures (e.g., hand swipes or finger presses) detected by an ESP32 device.

The project demonstrates how AI, IoT, and human-computer interaction can be combined to create an immersive and interactive music performance experience.

---

## Features
- **Emotion Detection**: Uses DeepFace to analyze emotions from a captured image.
- **AI-Generated Music**: Leverages the MusicGen model to generate background music based on the detected emotion.
- **Gesture Interaction**: Communicates with an ESP32 device to detect gestures (e.g., hand swipes, finger presses) and trigger actions in the application.
- **Real-Time Music Playback**: Plays generated music and allows users to interact with the system in real-time.

---

### Hardware
- ESP32 device with gesture sensors (e.g., touch sensors, accelerometer).
- A computer with a webcam for capturing images and with a GPU (recommended).

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/DanyurNan/Emotion-and-Gesture-DJ.git
cd Emotion-and-Gesture-DJ
```

### 2. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configure ESP32
- Upload the appropriate firmware to your ESP32 device to enable gesture detection and communication with the application.
- Ensure the ESP32 is connected to the same network as your computer and update the `ESP32_IP` and `PORT` constants in the `app.py` file with the correct values.

The application will open in your web browser. Follow the on-screen instructions to capture an image, detect emotions, and generate music.

---

## Prerequisites
Before running the project, ensure you have the following installed:


## Usage

### 1. Capture an Image
- Use the webcam widget to capture an image of yourself or another subject.

### 2. Emotion Detection
- The application will analyze the image and display the detected emotions along with their confidence scores.

### 3. Generate Music
- Click the "Generate Music" button to create a background track based on the dominant emotion.

### 4. Gesture Interaction
- Use the ESP32 device to interact with the application:
  - **Finger Presses**: Trigger specific notes to play.
  - **Hand Swipes**: Change the emotion or music style.

---

## Customization
- **Music Generation**: Modify the `generate_music` function in `bnm.py` to adjust the duration, style, or other parameters of the generated music.
- **Gesture Mapping**: Update the `NOTE_PRESSES` and `SCALE_MAPPINGS` constants to customize the notes and scales triggered by gestures.
- **ESP32 Communication**: Modify the `run_client` function to handle additional gestures or sensor inputs.

---

## Troubleshooting
- **ESP32 Connection Issues**:
  - Ensure the ESP32 is connected to the correct IP address and port.
  - Check the wiring and firmware of the ESP32 device.
- **Music Generation Failures**:
  - Ensure the MusicGen model is properly loaded and GPU resources are available.
  - Clear GPU memory using the `clear_gpu_memory` function if necessary.
- **Streamlit Errors**:
  - Restart the Streamlit server if the application becomes unresponsive.

---

## Acknowledgments
- [DeepFace](https://github.com/serengil/deepface) for emotion detection.
- [MusicGen](https://github.com/facebookresearch/audiocraft) for AI-generated music.
- [Streamlit](https://streamlit.io/) for the web application framework.
