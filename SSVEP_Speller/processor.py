import websocket
import json
import ssl
import time
import numpy as np
import os
from threading import Thread, Lock
from scipy.signal import welch, butter, lfilter
import pyautogui

# --- Configuration ---
CLIENT_ID = "SJp8zTW9D0abRSfEM11393aCeEcf5H6HWWsl97gk"
CLIENT_SECRET = "R3e7Ej24RjAPnG93TlmcfOmzXWTCXstSCRLKN38ebDnvv9oIOe27xsOQbz5GNGoTdFY7ogtHjRLc391OYHB7GieP8HX287nyGpFlmFb3Y7NoYwYcrewE4BrreDj3xPRp"
URL = "wss://127.0.0.1:6868"
STATE_FILE = "state.json"

FREQS = [8.0, 10.0, 12.0]
CONFIDENCE_THRESHOLD = 4 # Increaserd for hierarchical stability
WINDOW_SIZE = 256
SAMPLING_RATE = 128

# Hierarchy Mapping (Must match stimulus.py)
HIERARCHY = {
    "ROOT": ["A-M", "N-Z", "UTILS"],
    "A-M": ["A-D", "E-I", "J-M"],
    "N-Z": ["N-S", "T-W", "X-Z"],
    "UTILS": ["SPACE", "DELETE", "ROOT"],
    "A-D": ["A", "B", "C-D"],
    "E-I": ["E-G", "H", "I"],
    "J-M": ["J", "K", "L-M"],
    "N-S": ["N-P", "Q", "R-S"],
    "T-W": ["T", "U", "V-W"],
    "X-Z": ["X", "Y", "Z"],
}

def get_labels_for_scene(scene):
    if scene in HIERARCHY: return HIERARCHY[scene]
    if scene == "C-D": return ["C", "D", "ROOT"]
    if scene == "E-G": return ["E", "F", "G"]
    if scene == "L-M": return ["L", "M", "ROOT"]
    if scene == "N-P": return ["N", "O", "P"]
    if scene == "R-S": return ["R", "S", "ROOT"]
    if scene == "V-W": return ["V", "W", "ROOT"]
    return []

class EEGProcessor:
    def __init__(self):
        self.ws = None
        self.auth_token = None
        self.session_id = None
        self.headset_id = None
        self.motion_data = {"gyroX": 0}
        self.facial_data = {"blink": 0}
        self.mental_data = {"focus": 0.0}
        self.sensor_indices = {"gyroX": -1, "blink": -1, "gamma_indices": []}
        self.request_id = 0
        self.is_running = False
        self.blink_triggered = False

    def on_message(self, ws, message):
        data = json.loads(message)
        if "id" in data:
            res = data.get("result", {})
            error = data.get("error", {})
            if error:
                print(f"❌ Cortex API Error: {error.get('message', 'Unknown error')}")
                return

            if "accessGranted" in res: self.authorize()
            elif "cortexToken" in res: self.auth_token = res["cortexToken"]; self.query_headsets()
            elif isinstance(res, list) and len(res) > 0 and "id" in res[0]: 
                self.headset_id = res[0]["id"]
                print(f"🎧 Headset Found: {self.headset_id}")
                self.create_session()
            elif "id" in res and "status" in res: 
                self.session_id = res["id"]
                print(f"📡 Session Created: {self.session_id}")
                self.subscribe()
            elif "success" in res:
                # Capture indices for motion, facial, and power
                if isinstance(res["success"], list) and len(res["success"]) > 0:
                    for stream_info in res["success"]:
                        cols = stream_info.get("cols", [])
                        if "gyroX" in cols: self.sensor_indices["gyroX"] = cols.index("gyroX")
                        if "blink" in cols: self.sensor_indices["blink"] = cols.index("blink")
                        # pow cols typically like "O1/gamma", "O2/gamma" etc.
                        gamma_cols = [i for i, c in enumerate(cols) if "gamma" in c.lower()]
                        if gamma_cols: self.sensor_indices["gamma_indices"] = gamma_cols
                print("✅ Subscribed to available streams (Motion, Facial, Mental).")
                
            elif "failure" in res:
                fail = res["failure"][0]
                print(f"\n⚠️  Subscription Failed (Code {fail.get('code')}): {fail.get('message')}")
                if fail.get('code') == -32016:
                    print("💡 HINT: This usually means raw 'eeg' is not allowed on your license, OR no headset is detected.")
            else:
                print(f"❓ Uncaught Result: {res}")

        elif "pow" in data:
            # pow is band power. We average gamma across available sensors.
            indices = self.sensor_indices.get("gamma_indices", [])
            if indices:
                powers = [data["pow"][i] for i in indices]
                # Update focus score (normalized roughly 0-1 for the UI)
                avg_gamma = sum(powers) / len(powers)
                self.mental_data["focus"] = min(avg_gamma / 10.0, 1.0) # Simple normalization

        elif "met" in data:
            # Performance Metrics: [ "foc", "str", "rel", "int", "eng", "exc" ]
            # index 0 is Focus
            self.mental_data["focus"] = data["met"][0]

        elif "mot" in data:
            if self.sensor_indices["gyroX"] != -1:
                self.motion_data["gyroX"] = data["mot"][self.sensor_indices["gyroX"]]

        elif "fac" in data:
            print(f"📡 FACE DATA: {data['fac']}") # Log raw facial data
            if self.sensor_indices["blink"] != -1:
                blink_val = data["fac"][self.sensor_indices["blink"]]
                if blink_val > 0:
                    print(f"✨ BLINK DETECTED: {blink_val}")
                    self.blink_triggered = True
            else:
                # Fallback: check if the first element is "blink" string
                if data["fac"][0] == "blink":
                    print("✨ BLINK STRING DETECTED")
                    self.blink_triggered = True

    def on_error(self, ws, error): print(f"❌ WebSocket Error: {error}")
    def on_close(self, ws, status, message): self.is_running = False
    def on_open(self, ws): self.request_access()
    def send(self, method, params=None):
        self.request_id += 1
        payload = {"jsonrpc": "2.0", "id": self.request_id, "method": method}
        if params: payload["params"] = params
        self.ws.send(json.dumps(payload))
    def request_access(self): self.send("requestAccess", {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET})
    def authorize(self): self.send("authorize", {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET})
    def query_headsets(self): self.send("queryHeadsets")
    def create_session(self): self.send("createSession", {"cortexToken": self.auth_token, "headset": self.headset_id, "status": "active"})
    def subscribe(self): self.send("subscribe", {"cortexToken": self.auth_token, "session": self.session_id, "streams": ["mot", "fac", "pow", "met"]})

    def run(self):
        self.ws = websocket.WebSocketApp(URL, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        self.is_running = True
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

def write_state(scene, select_idx=None, highlight_idx=1, focus=0.0):
    state = {"scene": scene, "highlight_idx": highlight_idx, "focus_score": focus}
    if select_idx is not None:
        state["selection_idx"] = select_idx
        state["highlight_time"] = time.time()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def main():
    processor = EEGProcessor()
    thread = Thread(target=processor.run); thread.daemon = True; thread.start()
    
    current_scene = "ROOT"
    highlight_idx = 1 # Center by default
    
    print("🚀 Motion & Facial Speller Started!")
    
    try:
        while True:
            time.sleep(0.05) # Fast update for motion
            
            # 1. Navigation (Head Tilt)
            gyro = processor.motion_data["gyroX"]
            focus = processor.mental_data["focus"]
            
            # Thresholds for tilt (Adjust based on sensitivity)
            if gyro < -1500: # Tilt Left
                highlight_idx = 0
            elif gyro > 1500: # Tilt Right
                highlight_idx = 2
            else: # Center
                highlight_idx = 1
            
            # 2. Selection (Blink + Mental Focus)
            # Threshold of 0.3 for focus intensity (adjust as needed)
            focus_threshold = 0.2 
            
            if processor.blink_triggered:
                processor.blink_triggered = False # Reset
                
                if focus >= focus_threshold:
                    idx = highlight_idx
                    print(f"✅ Mental Selection Triggered (Focus: {int(focus*100)}%)")
                    
                    # Logic transition
                    write_state(current_scene, select_idx=idx, highlight_idx=highlight_idx, focus=focus)
                    time.sleep(0.5) # Feedback delay
                    
                    if current_scene == "ROOT":
                        current_scene = HIERARCHY["ROOT"][idx]
                        print(f"📂 Entered Block: {current_scene}")
                    elif current_scene in HIERARCHY:
                        current_scene = HIERARCHY[current_scene][idx]
                        print(f"📝 Entered Row: {current_scene}")
                    else:
                        options = get_labels_for_scene(current_scene)
                        selected = options[idx]
                        
                        if selected == "ROOT":
                            current_scene = "ROOT"
                            print("🔄 Reset to ROOT")
                        elif selected == "SPACE":
                            print("⌨️  SPACE")
                            pyautogui.press('space')
                            current_scene = "ROOT"
                        elif selected == "DELETE":
                            print("⌫  DELETE")
                            pyautogui.press('backspace')
                            current_scene = "ROOT"
                        else:
                            print(f"✨ TYPING: {selected}")
                            pyautogui.write(selected)
                            current_scene = "ROOT"
                    
                    write_state(current_scene, highlight_idx=highlight_idx, focus=focus)
                    time.sleep(1.0) # Cooldown to prevent double-blink selection
                else:
                    print(f"⚠️ Blink detected but Focus too low ({int(focus*100)}% < {int(focus_threshold*100)}%)")
            else:
                # Update highlight and focus only
                write_state(current_scene, highlight_idx=highlight_idx, focus=focus)

    except KeyboardInterrupt: pass

if __name__ == "__main__": main()
