import asyncio
import json
import ssl
import time
import websocket
from threading import Thread

# --- Configuration ---
# Emotiv Cortex API
CORTEX_URL = "wss://localhost:6868"
# TODO: Enter your actual Client ID and Secret if the public/app session doesn't auto-authorize.
# You can get these from https://www.emotiv.com/my-account/cortex-apps/
CLIENT_ID = "1kvqPJdSH0SxQMvK9OqGIcw1Th4A34bararpfHQw" 
CLIENT_SECRET = "TKbkvvjxqmf9wetbJzBRwF1hzejC30oOEPpVJIlYU1wROMJwLUgfI7lxoZ6aIlzbeVx4PxVoFOLCNcoQ5O8VCHVKYwmI6OcZoSPyiM6EWJcmeqjLaDsS20NNmBsBTRyz"

# ESP32 WebSocket
ESP32_IP = "192.168.4.1" # Default AP IP for ESP32
ESP32_PORT = 81
ESP32_URL = f"ws://{ESP32_IP}:{ESP32_PORT}/"

# Command Mapping
# Type 0 is Joystick: {type:0, x: -100..100, y: -100..100}
CMD_FORWARD = {"type": 0, "x": 0, "y": -100}
CMD_BACKWARD = {"type": 0, "x": 0, "y": 100}
CMD_LEFT = {"type": 0, "x": -100, "y": 0}
CMD_RIGHT = {"type": 0, "x": 100, "y": 0}
CMD_STOP = {"type": 0, "x": 0, "y": 0}

class CortexClient:
    def __init__(self, controller):
        self.ws = None
        self.url = CORTEX_URL
        self.controller = controller
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
        # Step 1: Request Access (Optional if already approved, but good practice)
        # self.send_request("requestAccess", {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET})
        
        # Step 2: Authorize (Get Token)
        # If client_id/secret are empty, this might fail or rely on cached/anonymous if supported.
        # Ideally user provides them.
        print("Authorizing...")
        self.send_request("authorize", {
            "clientId": CLIENT_ID, 
            "clientSecret": CLIENT_SECRET,
            "debit": 1
        })

    def on_message(self, ws, message):
        data = json.loads(message)
        
        # Handle Responses
        if "id" in data:
            if "result" in data:
                res = data["result"]
                # Authorization Response -> Get Token
                if "cortexToken" in res:
                    self.token = res["cortexToken"]
                    print("\n[CORTEX] Authorized successfully!")
                    # Check for headset
                    self.send_request("queryHeadsets")
                
                # Query Headsets Response -> Get Headset ID
                elif isinstance(res, list) and len(res) > 0 and "id" in res[0]:
                    # Find the first connected headset
                    for hs in res:
                        if hs["status"] == "connected":
                            self.headset_id = hs["id"]
                            print(f"[CORTEX] Found Headset: {self.headset_id}")
                            break
                    
                    if self.headset_id:
                        self.create_session()
                    else:
                        print("[CORTEX] No CONNECTED headset found. Please connect headset.")
                        # Retry after delay? For simpler logic we stop or user restarts.
                
                # Create Session Response
                elif "id" in res and "appId" in res:
                    self.session_id = res["id"]
                    print(f"[CORTEX] Session Created: {self.session_id}")
                    self.subscribe()
            
            if "error" in data:
                print(f"[CORTEX ERROR] {data['error']['message']}")

        # Handle Stream Data (subscription)
        if "sid" in data:
            # We are looking for 'com' stream
            if "com" in data:
                # data['com'] is [command, power] e.g. ["push", 0.5]
                command = data["com"][0]
                power = data["com"][1]
                print(f"Mental Command: {command} (Power: {power})")
                
                # Map to RC
                if power > 0.1: # Threshold to avoid noise
                    self.controller.send_command(command)
                else:
                    self.controller.send_command("neutral")

    def create_session(self):
        print("Creating Session...")
        self.send_request("createSession", {
            "cortexToken": self.token,
            "headset": self.headset_id,
            "status": "active"
        })

    def subscribe(self):
        print("Subscribing to Mental Commands...")
        self.send_request("subscribe", {
            "cortexToken": self.token,
            "session": self.session_id,
            "streams": ["com"]
        })

    def on_error(self, ws, error):
        print(f"[CORTEX ERROR] {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("[CORTEX] Disconnected.")

    def run(self):
        # SSL ignore for localhost self-signed
        self.ws = websocket.WebSocketApp(self.url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


class RCController:
    def __init__(self):
        self.ws_esp = None
        self.connected_esp = False
        self.running = True
        self.last_send_time = 0
        self.send_interval = 0.1 # 100ms limit (10Hz)
        self.last_cmd = None

    def connect_esp(self):
        """Connects to the ESP32 WebSocket server."""
        while self.running:
            try:
                print(f"Connecting to ESP32 at {ESP32_URL}...")
                self.ws_esp = websocket.WebSocketApp(ESP32_URL,
                                                     on_open=self.on_open_esp,
                                                     on_message=self.on_message_esp,
                                                     on_error=self.on_error_esp,
                                                     on_close=self.on_close_esp)
                self.ws_esp.run_forever()
            except Exception as e:
                print(f"ESP32 Connection failed: {e}")
                time.sleep(2)

    def on_open_esp(self, ws):
        print("[ESP32] Connected!")
        self.connected_esp = True

    def on_message_esp(self, ws, message):
        """Handles messages from ESP32 (Debug info)."""
        print(f"[ESP32] {message}")

    def on_error_esp(self, ws, error):
        print(f"[ESP32 ERROR] {error}")

    def on_close_esp(self, ws, close_status_code, close_msg):
        print("[ESP32] Disconnected")
        self.connected_esp = False

    def send_command(self, action):
        """Sends a JSON command to the ESP32."""
        if not self.connected_esp:
            return

        cmd = CMD_STOP
        if action == "push": # Forward
            cmd = CMD_FORWARD
        elif action == "pull": # Backward
            cmd = CMD_BACKWARD
        elif action == "left":
            cmd = CMD_LEFT
        elif action == "right":
            cmd = CMD_RIGHT
        
        # Rate Limit & Change Detection:
        # Send immediately if command CHANGED (e.g. moving -> stop)
        # Otherwise, respect the 10Hz limit (keep-alive)
        current_time = time.time()
        
        # Initialize last_cmd if strictly necessary here, but better in __init__
        # Assuming we can just check if we should send
        should_send = False
        
        if cmd != self.last_cmd:
             should_send = True
        elif current_time - self.last_send_time >= self.send_interval:
             should_send = True
             
        if should_send:
            try:
                self.ws_esp.send(json.dumps(cmd))
                self.last_send_time = current_time
                self.last_cmd = cmd
            except Exception as e:
                print(f"Failed to send: {e}")

    def start(self):
        # Start ESP32 connection in a separate thread
        t = Thread(target=self.connect_esp)
        t.daemon = True
        t.start()
        
        # Start Cortex Client in main thread
        cortex = CortexClient(self)
        try:
            cortex.run()
        except KeyboardInterrupt:
            self.running = False
            print("Stopping...")

if __name__ == "__main__":
    controller = RCController()
    controller.start()
