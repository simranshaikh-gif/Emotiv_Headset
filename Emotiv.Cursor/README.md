#  Brain-Controlled Cursor — Full Step-by-Step Guide

## STAGE 1 — Prepare the Headset (Very Important)

1. Charge headset fully
2. Plug USB dongle
3. Open **Emotiv Launcher**
4. Login
5. Turn ON headset
6. Click toggle next to EPOC X

You must see:
 **Green dot**

If not green → nothing below will work.

---

## STAGE 2 — Wear & Fix Electrode Quality

Open **Apps → EmotivBCI**

Before training:

1. Wet felt pads
2. Wear headset slightly forward
3. Adjust slowly

For mental commands, the most important sensors are:

**AF3, AF4, F3, F4**

These are the *prefrontal cortex* (imagination & intention area).

Goal:
Mostly green or yellow is OK.

---

## STAGE 3 — Train Mental Commands (THIS IS THE REAL BCI PART)

Inside **EmotivBCI**:

You will see a floating cube.

Now you teach your brain patterns to the system.

### Step 1: Neutral

First train **Neutral** (VERY IMPORTANT)

Click train → relax → think NOTHING → stare calmly.

This becomes the baseline brain state.

---

### Step 2: Train “Push”

Click train Push.

While training:
Imagine strongly that you are **pushing a heavy wall forward with your hands**.

Important:
Do NOT blink, move head, or tense face.

You must imagine movement, not physically move.

Repeat 3–5 training cycles.

You will see training accuracy improve.

---

### Step 3: Train “Left”

Click train Left.

Imagine:
You are forcefully pushing something to your left side.

Again — only imagination.

Train 3–5 times.

---

### Step 4: Test

Switch to **Live Mode**.

Now:

* think Push → cube moves forward
* think Left → cube moves left

When the cube moves correctly → your brain patterns are learned.

You just created a machine learning classifier trained by your own brain.

---

## STAGE 4 — Install Python Mouse Control

Now we connect BCI → computer mouse.

### Install Python library

In VS Code terminal:

```bash
pip install -r requirements.txt
```

`pyautogui` is what moves the cursor.

---

## STAGE 5 — Get Your Credentials (REQUIRED)

To control the mouse, the script needs permission to talk to the Emotiv app.

1.  Go to **[id.emotivcloud.com](https://id.emotivcloud.com/)** and login.
2.  Click **My Apps** → **New App**.
    *   **App Name**: `MindCursor`
    *   **Redirect URI**: (Leave empty)
    *   **Description**: (Any text)
3.  Click **Create**.
4.  Copy your **Client ID** and **Client Secret**.

### Update the Script

1.  Open `mind_cursor.py`.
2.  Paste your keys at the top:

```python
CLIENT_ID = "Paste_Client_ID_Here"
CLIENT_SECRET = "Paste_Client_Secret_Here"
```
3.  Save the file.

---

## STAGE 6 — Connect & Run

The file `mind_cursor.py` connects to the Emotiv Cortex API via WebSocket.

Make sure:

* Emotiv Launcher OPEN
* Headset connected (green dot)

Run:

```bash
python mind_cursor.py
```

Look at Emotiv Launcher → a popup appears:

**Allow application access**

Click **ALLOW**.

check terminal for:
 **Session created**
 **Subscribed**

---

## STAGE 7 — Use It

Now:

1. Keep EmotivBCI running in Live mode
2. Run the Python script
3. Sit still

Then:

Think “push” → cursor moves up
Think “left” → cursor moves left

You are literally moving the mouse without touching it.

---

# Tips (Very Important)

BCI is 70% mental training.

Do:

* stay relaxed
* breathe normally
* same imagination every time

Don’t:

* blink hard
* move eyebrows
* clench jaw

You must imagine movement, not physically move.

After ~15 minutes practice, control becomes MUCH better.

---

# How to Demonstrate

Open Paint.

Then:
Draw shapes without touching mouse.

That becomes a **very powerful demo**.
