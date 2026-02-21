# Emotiv Brain-Controlled RC Car - Step-by-Step Guide

This guide will take you from the very beginning (Hardware Setup) to the final step (Driving with your Mind).

## Phase 1: Hardware Setup
**Goal**: Get the car physically ready.

1.  **Wire the Motors**: Connect your motors to the Motor Driver (L298N).
2.  **Wire the ESP32**: Connect the ESP32 to the Motor Driver using these pins:
    *   **Left Motor Speed (ENA)** -> GPIO 32
    *   **Left Motor In1** -> GPIO 33
    *   **Left Motor In2** -> GPIO 25
    *   **Right Motor Speed (ENB)** -> GPIO 26
    *   **Right Motor In1** -> GPIO 14
    *   **Right Motor In2** -> GPIO 27
3.  **Power Up**: Connect your battery to the Motor Driver (and ESP32). Ensure the LEDs on the ESP32 and Motor Driver turn on.

## Phase 2: Software Installation (One-Time)
**Goal**: Get your computer ready.

1.  **Install Python**: Download and install Python 3 from python.org.
2.  **Install Emotiv App**: Download the Emotiv Installer and set up the Cortex UI.
3.  **Install Libraries**: Open a terminal in this project folder and run:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Upload ESP32 Code**:
    *   Connect ESP32 to PC via USB.
    *   Open this folder in VS Code.
    *   Click the **PlatformIO Upload** arrow (bottom bar).
    *   Wait for "SUCCESS".
    *   **Disconnect the USB cable**.

## Phase 3: Training (Before Driving)
**Goal**: Teach the software your brain patterns.

1.  Put on your **Emotiv Headset**.
2.  Open the **Emotiv App** on your PC.
3.  Connect the headset via Bluetooth/Dongle. Ensure Signal Quality is **Green (Good)**.
4.  Go to **Training > Mental Commands**.
5.  Train these actions:
    *   **Push** (used for Forward)
    *   **Pull** (used for Backward)
    *   **Left**
    *   **Right**
    *   **Neutral** (Relax)
6.  Keep the Emotiv App **OPEN**.

## Phase 4: Driving (The Fun Part)
**Goal**: Connect and drive.

1.  **Power On the Car**: Turn on the battery switch on your RC car.
2.  **Connect WiFi**: On your laptop, look for the WiFi network **`RC_car`**. Connect to it. (Password is empty/open).
3.  **Run the Script**:
    *   Open a terminal in this folder.
    *   Run:
        ```bash
        python emotiv_control.py
        ```
4.  **Authorize**:
    *   Look at the terminal. It should say `Connected to Cortex API`.
    *   If a popup appears in the Emotiv App asking for permission, click **Approve**.
    *   The terminal should say `Authorized successfully!`.
5.  **Drive**:
    *   Focus on your trained command (e.g., visualize Pushing the block).
    *   The terminal will show: `Mental Command: push (Power: 0.8)`.
    *   The car should move forward!

## Troubleshooting
*   **"No Internet" on WiFi?**: That is normal. The car provides a local link, not internet.
*   **Car spins in circles?**: Check your motor wiring. Swap the wires of the motor that is spinning backwards.
*   **Script crashes?**: Make sure you installed the requirements in Phase 2.
