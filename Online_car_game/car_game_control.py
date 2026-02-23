import json
import ssl
import time
import websocket
from threading import Thread
from pynput.keyboard import Key, Controller

# --- Configuration ---
# Emotiv Cortex API
CORTEX_URL = "wss://localhost:6868"
CLIENT_ID = "1kvqPJdSH0SxQMvK9OqGIcw1Th4A34bararpfHQw" 
CLIENT_SECRET = "TKbkvvjxqmf9wetbJzBRwF1hzejC30oOEPpVJIlYU1wROMJwLUgfI7lxoZ6aIlzbeVx4PxVoFOLCNcoQ5O8VCHVKYwmI6OcZoSPyiM6EWJcmeqjLaDsS20NNmBsBTRyz"

# Command Mapping
# Mental Command / Facial Expression -> Keyboard Key
command_map = {
    "push": 'w',   # Accelerate
    "blink": 's',  # Brake (Facial expression)
    "left": 'a',   # Turn Left
    "right": 'd'   # Turn Right
}

class KeyboardController:
    def __init__(self):
        self.keyboard = Controller()
        self.active_keys = set()
        self.current_action = "neutral"

    def update_keys(self, action_source, action_name):
        """
        action_source: 'com' or 'fac'
        action_name: e.g., 'push', 'blink'
        """
        # Logic: If 'fac' (blink) is active, it takes priority for braking.
        # If 'com' (push/left/right) is active, it handles movement.
        
        target_key = command_map.get(action_name)
        
        # Determine if we should release other keys
        # We only want one movement key at a time for simplicity
        if action_name == "neutral":
             for k in list(self.active_keys):
                print(f"Releasing: {k}")
                self.keyboard.release(k)
                self.active_keys.remove(k)
             return

        if target_key:
            # Release other keys if a new action starts
            to_release = [k for k in self.active_keys if k != target_key]
            for k in to_release:
                print(f"Releasing: {k}")
                self.keyboard.release(k)
                self.active_keys.remove(k)

            # Press the new key
            if target_key not in self.active_keys:
                print(f"Pressing: {target_key} (Action: {action_name})")
                self.keyboard.press(target_key)
                self.active_keys.add(target_key)

class CortexClient:
    def __init__(self, kb_controller):
        self.ws = None
        self.url = CORTEX_URL
        self.kb_controller = kb_controller
        self.token = None
        self.session_id = None
        self.headset_id = None
        self.request_id = 1

    def send_request(self, method, params=None):
        req = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params if params else {},
            "id": self.request_id
        }
        self.request_id += 1
        self.ws.send(json.dumps(req))

    def on_open(self, ws):
        print("Connected to Cortex API")
        print("Authorizing...")
        self.send_request("authorize", {
            "clientId": CLIENT_ID, 
            "clientSecret": CLIENT_SECRET,
            "debit": 1
        })

    def on_message(self, ws, message):
        data = json.loads(message)
        
        if "id" in data:
            if "result" in data:
                res = data["result"]
                if "cortexToken" in res:
                    self.token = res["cortexToken"]
                    print("[CORTEX] Authorized successfully!")
                    self.send_request("queryHeadsets")
                elif isinstance(res, list) and len(res) > 0 and "id" in res[0]:
                    for hs in res:
                        if hs["status"] == "connected":
                            self.headset_id = hs["id"]
                            print(f"[CORTEX] Found Headset: {self.headset_id}")
                            break
                    if self.headset_id:
                        self.create_session()
                    else:
                        print("[CORTEX] No CONNECTED headset found. Please connect headset.")
                elif "id" in res and "appId" in res:
                    self.session_id = res["id"]
                    print(f"[CORTEX] Session Created: {self.session_id}")
                    self.subscribe()
            
            if "error" in data:
                print(f"[CORTEX ERROR] {data['error']['message']}")

        if "sid" in data:
            # Handle Mental Commands
            if "com" in data:
                command = data["com"][0]
                power = data["com"][1]
                if power > 0.1:
                    self.kb_controller.update_keys("com", command)
                else:
                    self.kb_controller.update_keys("com", "neutral")
            
            # Handle Facial Expressions
            if "fac" in data:
                # data['fac'] = [eyeAction, eyeActionPower, upperFaceAction, upperFacePower, lowerFaceAction, lowerFacePower]
                # Index 0 is eyeAction (e.g., 'blink', 'winkL', 'winkR')
                eye_action = data["fac"][0]
                if eye_action == "blink":
                    print("Facial Action: Blink detected!")
                    self.kb_controller.update_keys("fac", "blink")

    def create_session(self):
        print("Creating Session...")
        self.send_request("createSession", {
            "cortexToken": self.token,
            "headset": self.headset_id,
            "status": "active"
        })

    def subscribe(self):
        print("Subscribing to Streams (Mental Commands + Facial Expressions)...")
        self.send_request("subscribe", {
            "cortexToken": self.token,
            "session": self.session_id,
            "streams": ["com", "fac"]
        })

    def on_error(self, ws, error):
        print(f"[CORTEX ERROR] {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("[CORTEX] Disconnected.")

    def run(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

if __name__ == "__main__":
    kb = KeyboardController()
    client = CortexClient(kb)
    print("Starting Emotiv Car Game Control...")
    print("Mapping: push -> W, blink -> S, left -> A, right -> D")
    try:
        client.run()
    except KeyboardInterrupt:
        print("Exiting...")
