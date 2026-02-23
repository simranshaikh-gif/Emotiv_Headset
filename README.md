# Brain-Computer Interface Device Control using EEG (SSVEP)

## Overview
This project demonstrates a Brain-Computer Interface (BCI) system that allows a user to control external hardware using brainwave signals captured from an Emotiv EEG headset.

The system detects Steady-State Visually Evoked Potential (SSVEP) responses and converts them into real-time commands for a microcontroller, enabling hands-free control of a physical device such as an RC car or embedded system.

---

## System Architecture
EEG Headset → Emotiv BCI Software → Signal Processing → Command Classification → Serial Communication → Microcontroller → Device Actuation

---

## Features
- Real-time EEG signal acquisition
- Signal preprocessing and filtering
- SSVEP frequency detection
- Command mapping (Left / Right / Forward / Stop)
- Microcontroller-based hardware control
- Hands-free human-machine interaction

---

## Implemented Applications
- Brain-controlled cursor
- LED control using EEG commands
- RC car movement using brain signals
- SSVEP speller interface

---

## Hardware Used
- Emotiv EEG Headset
- Microcontroller (STM32 / Arduino)
- Motor driver module
- RC car / Embedded device

---

## Software & Tools
- Emotiv BCI Software (real-time EEG data streaming)
- Python (signal handling & serial communication)
- Embedded C firmware

---

## Working Principle
The user focuses on flickering visual stimuli of specific frequencies.  
Each frequency produces a corresponding SSVEP response in the brain.  
The system detects the dominant frequency, classifies the user’s intention, and sends the corresponding command to the microcontroller through serial communication.  
The microcontroller then actuates motors or other connected hardware.

---

## Key Concepts
- EEG signal acquisition
- Signal preprocessing
- Frequency-based classification
- Human-machine interaction
- Embedded hardware control

---

## Demonstration
(Add your Google Drive or YouTube demo video link here)

---

## Future Improvements
- Machine learning based classification
- Wireless device control
- Multi-command interface
- Robotic platform integration

---

## Author
**Simran Shaikh**  
Embedded & Intelligent Systems | Edge AI | Brain-Computer Interface
