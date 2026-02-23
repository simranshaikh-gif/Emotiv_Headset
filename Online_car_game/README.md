# Emotiv Brain-Controlled Car Game: Madalin Stunt Cars 2

This project allows you to play **Madalin Stunt Cars 2** using your mind and eye blinks with an Emotiv EEG headset. It uses the Emotiv Cortex API to translate mental commands and facial expressions into keyboard inputs.

## 🚀 Get Started

### 1. Prerequisites
- **Hardware**: Emotiv EEG Headset (EPOC X, EPOC+, etc.)
- **Software**: 
  - [Emotiv App / EmotivBCI](https://www.emotiv.com/products/emotiv-app) (Headset calibration & Mental Command training)
  - Python 3.12 or 3.13

### 2. Installation
Install the required Python libraries:
```powershell
pip install pynput websocket-client
```

### 3. Setup
- **Train Mental Commands**: Open the Emotiv App and ensure you have trained the **Push**, **Left**, and **Right** commands.
- **Connect Headset**: Ensure your headset is connected and has good contact quality.
- **Open Game**: Open [Madalin Stunt Cars 2](https://www.madalingames.com/madalin-stunt-cars-2/) in your browser. **Click inside the game** to ensure it is focused.

## 🎮 Controls

The script maps your brain signals to the following keys:

| Action | Control | Result |
| :--- | :--- | :--- |
| **Push** | **W** | Accelerate |
| **Blink** | **S** | Brake / Reverse |
| **Left** | **A** | Turn Left |
| **Right** | **D** | Turn Right |

## 🛠️ Usage
Run the control script from this directory:
```powershell
python car_game_control.py
```
*(If `python` fails, use `py -3.13 car_game_control.py`)*

Once the terminal displays `Subscribing to Streams...`, your brain commands will control the car!

## 📜 How it Works
The `car_game_control.py` script connects to the Emotiv Cortex Service via WebSockets. It listens for `com` (Mental Commands) and `fac` (Facial Expressions) streams. When a command is detected above the power threshold, it uses the `pynput` library to simulate a real keyboard press.
