# Emotiv Headset LED Control

This project enables controlling an LED connected to an ESP32 microcontroller using eye blinks detected by an Emotiv EPOC X headset. The system uses the Emotiv Cortex API to detect facial expressions and sends commands to the ESP32 via Serial communication.

## Features
- **Project Structure**:
  - `blink_led.py`: Main Python script to interface with Emotiv Cortex API and send commands to ESP32.
  - `esp32_led/esp32_led.ino`: Arduino sketch for the ESP32 to receive commands and control the LED.
  - `src/main.cpp`: C++ source file for the ESP32 (PlatformIO version).
  - `cortex_test.py`: A simple script to test the connection to the Emotiv Cortex API.

- **Functionality**:
  - Detects double-blinks using the Emotiv headset.
  - Toggles the built-in LED on the ESP32 (GPIO 2).

## Prerequisites

### Hardware
- Emotiv EPOC X Headset (or compatible Emotiv Headset)
- ESP32 Development Board
- USB Cable for ESP32

### Software
- Python 3.x
- Arduino IDE (or PlatformIO)
- Emotiv App (Must be running for Cortex Service)

### Python Dependencies
Install the required libraries:
```bash
pip install websocket-client pyserial
```

## Setup & specific instructions

1. **Hardware Setup**:
   - Connect the ESP32 to your computer via USB.
   - Ideally, note the COM port (e.g., `COM5` on Windows).

2. **ESP32 Firmware**:
   - Open `esp32_led/esp32_led.ino` in Arduino IDE or use the `src/main.cpp` with PlatformIO.
   - Upload the code to your ESP32 board.
   - Ensure the baud rate is set to `115200` in the serial monitor if you want to debug.

3. **Cortex API Configuration**:
   - Open `blink_led.py`.
   - Update `CLIENT_ID` and `CLIENT_SECRET` with your credentials from the Emotiv Developer Portal.
     - *Note: For local testing, sometimes default/empty values work if you approve the connection in the Emotiv Launcher.*
   - Update `COM_PORT` to match your ESP32's port.

## Usage

1. Ensure your Emotiv headset is connected and has good contact quality.
2. Run the main script:
   ```bash
   python blink_led.py
   ```
3. Look at the console output. You might be prompted to approve access in the Emotiv Launcher.
4. Perform a **double-blink** intentionally.
   - A single blink is detected but ignored for triggering.
   - Two blinks within 1 second will toggle the LED on the ESP32.
   - The console will display: `*** DOUBLE BLINK -> LED ON ***` or `*** DOUBLE BLINK -> LED OFF ***`.

## Troubleshooting

- **Connection Refused**: Ensure the Emotiv App is running and the Cortex Service is active.
- **Serial Error**: Verify the correct `COM_PORT` and ensure no other application (like Arduino Serial Monitor) is using it.
- **No Blinks Detected**: Check headset contact quality in the Emotiv App. The facial expression stream (`fac`) relies on good signal quality.
