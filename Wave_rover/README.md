# 🧠 Emotiv BCI Wave Rover Setup Guide

Follow these steps exactly to control your robot with your brainwaves.

## Step 1: Headset Preparation
-   **Charge**: Ensure your Emotiv headset is charged.
-   **Hydrate**: If using EPOC X, ensure the felt pads are hydrated with saline.
-   **Wear**: Put on the headset. Open **Emotiv Launcher** and ensure you have a **"Good" (green)** signal quality on all sensors.

## Step 2: Code Configuration
-   Open `emotiv_rover_bridge.py` in VS Code.
-   Paste your **Client ID** and **Client Secret** (from [Emotiv Console](https://www.emotiv.com/my-account/cortex-apps/)) into the config area.

## Step 3: Train Your Thoughts (Most Important!)
-   Open the **Emotiv App** (Mental Commands section).
-   **Train Neutral**: 30 seconds of relaxing.
-   **Train LEFT**: Imagine turning a steering wheel left vividly.
-   **Train PUSH**: Imagine pushing a heavy wall forward (this is mapped to "Forward").
-   **Verify**: Ensure the "Detection Power" in the app goes high when you think these thoughts.

## Step 4: Robot WiFi Connection
-   Turn on the Wave Rover.
-   On your laptop, connect to the WiFi network named **WAVE_ROVER**.
-   Open your browser to `http://192.168.4.1` just to confirm the car's web page opens.

## Step 5: Start Control
-   Keep the Emotiv App running in the background.
-   In VS Code terminal, run the script:
    ```bash
    python emotiv_rover_bridge.py
    ```
-   Wait for `SYSTEM READY - LISTENING FOR THOUGHTS`.
-   **Think "LEFT"** (the action you trained).
-   The terminal should show: `[>] Sent LEFT -> http://192.168.4.1/js?json={"T":1,"L":-150,"R":150} (OK)`

---
### ⚠️ Why it might "not work":
1.  **WiFi**: If you are not on the `WAVE_ROVER` WiFi, the command will fail.
2.  **Detection Power**: If the Emotiv App doesn't see your thought as "confident", the script won't send the command. Train more!
3.  **Approve Access**: The FIRST time you run the script, check your Emotiv App—it may ask you to click **"Approve"** to allow the script to connect.
