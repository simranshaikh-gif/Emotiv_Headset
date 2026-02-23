# 🧠 Mental Motion Speller (License-Ready BCI)

This project is a real-time Brain-Computer Interface (BCI) developed for the **Emotiv Headset**. It allows users to type letters, spaces, and delete characters using **Head Motion** and **Facial Expressions**, making it compatible with the **Free Emotiv License**.

## 🚀 How it Works
1. **Navigation (Head Tilt)**: Detects head tilt **Left** or **Right**.
2. **Focus Intensity (Gamma/Mental)**: Detects how hard you are concentrating. This is shown by the **Green Intensity Bar**.
3. **Hybrid Selection**: To click a box, you must **Focus** (keep the bar above 20%) **AND Blink** at the same time.

---

## 🏁 Getting Started

### 1. Navigation & Selection
To type a letter:
1. **Tilt Left/Right**: Move the **Blue Border**.
2. **Focus**: Look at the box intently (The Green Bar should grow).
3. **Blink**: Once the bar is high enough, blink to "Click".

### 2. Hierarchy
- **Level 1 (Blocks)**: Select the group containing your letter (e.g., "A-I").
- **Level 2 (Rows)**: Select the specific row.
- **Level 3 (Letters)**: Select the letter to type it.
- **Reset**: The system automatically returns to Level 1 after typing.

### 3. Startup
1. **Launch Stimulus**: `python stimulus.py`
2. **Launch Processor**: `python processor.py`
3. **Approve**: If Emotiv Launcher asks for access, click **"Approve"**.

---

## ⌨️ Special Keys
Navigate to the **UTILS** block to access:
- **SPACE**: Press the spacebar.
- **DELETE**: Backspace/Delete character.
- **ROOT**: Reset the menu back to the start.

---
*Created as a BCI Accessibility Project.*
