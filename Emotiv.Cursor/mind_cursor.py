import websocket
import json
import ssl
import time
import threading
import pyautogui
import os

# ==============================================================================
# 🔧 USER CONFIGURATION (Required)
# ==============================================================================
# Get these from https://id.emotivcloud.com/ -> My Apps -> New App
CLIENT_ID = "SJp8zTW9D0abRSfEM11393aCeEcf5H6HWWsl97gk"
CLIENT_SECRET = "R3e7Ej24RjAPnG93TlmcfOmzXWTCXstSCRLKN38ebDnvv9oIOe27xsOQbz5GNGoTdFY7ogtHjRLc391OYHB7GieP8HX287nyGpFlmFb3Y7NoYwYcrewE4BrreDj3xPRp"

# Folder to open on Double Blink
TARGET_FOLDER = r"C:\Users\sim_s\Documents"
# ==============================================================================

# Movement speed
STEP = 40
# Cortex URL
URL = "wss://localhost:6868"

class CortexCursor:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.ws = None
        self.cortex_token = None
        self.session_id = None
        self.headset_id = None
        self.is_connected = False
        self.request_id = 1
        
        # State tracking
        self.auth_done = False
        self.session_done = False
        
        # Blink tracking
        self.last_blink_time = 0
        self.blink_count = 0

    def get_id(self):
        self.request_id += 1
        return self.request_id

    def on_message(self, ws, message):
        data = json.loads(message)
        
        # 1. Handle Responses (Results)
        if 'result' in data:
            result = data['result']
            req_id = data.get('id')
            
            # Auth flow responses
            if 'accessGranted' in result:
                print("✅ Access Granted. Authorizing...")
                self.authorize()
            
            elif 'cortexToken' in result:
                self.cortex_token = result['cortexToken']
                print("✅ Authorized. Token received.")
                self.query_headsets()
                
            # Handle queryHeadsets response (list of headsets)
            elif isinstance(result, list):
                if len(result) > 0 and 'id' in result[0]:
                    # Found headsets
                    self.headset_id = result[0]['id']
                    print(f"✅ Headset found: {self.headset_id}. Creating session...")
                    self.create_session()
                else:
                    print("⚠️ No headset found. retrying in 3 seconds...")
                    time.sleep(3)
                    self.query_headsets()
                
            elif 'id' in result and 'appId' in result:
                # Session created
                self.session_id = result['id']
                print(f"✅ Session created: {self.session_id}. Subscribing...")
                self.subscribe()
                
            elif 'success' in result and len(result['success']) > 0:
                 print("✅ Subscribed to Mental Commands & Face! Ready to move cursor. 🧠🖱️")

        # 2. Handle Errors
        elif 'error' in data:
             print(f"❌ Error: {data['error']['message']}")

        # 3. Handle Facial Expressions (Double Blink)
        elif 'fac' in data:
            # eyeAct is usually at index 0 for 'fac' stream (check docs/implementation)
            # Default mapping: [eyeAct, uAct, uPow, lAct, lPow]
            eye_act = data['fac'][0] 
            
            if eye_act == 'blink':
                current_time = time.time()
                # Check if this blink is within 1 second of the last one
                if current_time - self.last_blink_time < 1.0:
                    print("👀 DOUBLE BLINK DETECTED! Opening folder...")
                    self.open_folder()
                    self.last_blink_time = 0 # Reset
                else:
                    print("👁️ Blink detected")
                    self.last_blink_time = current_time

        # 4. Handle Data Stream (Mental Commands)
        elif 'com' in data:
            command = data['com'][0]
            power = data['com'][1]
            
            # DEBUG: Print everything so we see if connection is alive!
            # print(f"🧠 Command: {command} | Power: {power}")

            if power > 0.1:  # Reduced threshold for easier testing
                self.move_cursor(command)

    def open_folder(self):
        try:
            os.startfile(TARGET_FOLDER)
        except Exception as e:
            print(f"❌ Failed to open folder: {e}")

    def move_cursor(self, command):
        x, y = pyautogui.position()
        
        if command == "push":
            pyautogui.moveTo(x, y - STEP)
            print(f"⬆️ PUSH")
            
        elif command == "left":
            pyautogui.moveTo(x - STEP, y)
            print(f"⬅️ LEFT")
            
        elif command == "right":
            pyautogui.moveTo(x + STEP, y)
            print(f"➡️ RIGHT")
            
        elif command == "pull":
            pyautogui.moveTo(x, y + STEP)
            print(f"⬇️ PULL")

    def on_error(self, ws, error):
        print(f"Connection Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("Connection Closed")

    def on_open(self, ws):
        print("Connected to Cortex API. Requesting access...")
        self.request_access()

    # --- API Calls ---
    
    def send_request(self, method, params=None):
        req = {
            "jsonrpc": "2.0",
            "id": self.get_id(),
            "method": method,
        }
        if params:
            req["params"] = params
        self.ws.send(json.dumps(req))

    def request_access(self):
        self.send_request("requestAccess", {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        })

    def authorize(self):
        self.send_request("authorize", {
            "clientId": self.client_id,
            "clientSecret": self.client_secret
        })

    def query_headsets(self):
        self.send_request("queryHeadsets")

    def create_session(self):
        self.send_request("createSession", {
            "cortexToken": self.cortex_token,
            "headset": self.headset_id,
            "status": "active"
        })

    def subscribe(self):
        self.send_request("subscribe", {
            "cortexToken": self.cortex_token,
            "session": self.session_id,
            "streams": ["com", "fac"]
        })

    def start(self):
        # Disable SSL verification for localhost
        self.ws = websocket.WebSocketApp(
            URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    if "YOUR_CLIENT_ID_HERE" in CLIENT_ID:
        print("⚠️  PLEASE UPDATE YOUR CLIENT_ID AND CLIENT_SECRET IN THE SCRIPT!")
        print("   Get them from https://id.emotivcloud.com/")
    else:
        cursor = CortexCursor(CLIENT_ID, CLIENT_SECRET)
        cursor.start()
