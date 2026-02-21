import json
import ssl
import time
import requests
import websocket
import threading
import sys

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------

# Emotiv Cortex API Config
CORTEX_URL = "wss://localhost:6868"
CLIENT_ID = "SJp8zTW9D0abRSfEM11393aCeEcf5H6HWWsl97gk"
CLIENT_SECRET = "R3e7Ej24RjAPnG93TlmcfOmzXWTCXstSCRLKN38ebDnvv9oIOe27xsOQbz5GNGoTdFY7ogtHjRLc391OYHB7GieP8HX287nyGpFlmFb3Y7NoYwYcrewE4BrreDj3xPRp" # TODO: Replace with your Client Secret directly
# TIP: For personal use, you can often leave these as empty strings if you use the 
# Emotiv App to approve the connection manually, or generate them at https://www.emotiv.com/my-account/cortex-apps/

# Wave Rover Config
ROVER_IP = "192.168.4.1"  # Default IP when connected to WAVE_ROVER AP
ROVER_PORT = 80           # Standard HTTP port

# Command Mapping (Waveshare Wave Rover JSON API)
# T=1 is for speed control. L and R are motor speeds (-255 to 255).
COMMAND_MAP = {
    "push":    '{"T":1,"L":80,"R":80}',   # Forward
    "pull":    '{"T":1,"L":-80,"R":-80}', # Backward
    "left":    '{"T":1,"L":-80,"R":80}',  # Turn Left
    "right":   '{"T":1,"L":80,"R":-80}',  # Turn Right
    "neutral": '{"T":1,"L":0,"R":0}'        # Stop
}

# -------------------------------------------------------------------------
# ROVER CONTROLLER
# -------------------------------------------------------------------------

class RoverController:
    def __init__(self, ip, port=80):
        self.base_url = f"http://{ip}:{port}"
        self.session = requests.Session()
        self.last_command_sent = None
        self.last_send_time = 0
        print(f"[*] Rover Controller initialized at {self.base_url}")

    def send_command(self, folder_str, command_name):
        """
        Sends the JSON command in a background thread with rate limiting.
        """
        # 1. Don't send the SAME command twice in a row (especially Neutral)
        if command_name == self.last_command_sent:
            return

        # 2. Rate limit: Max 2 network calls per second to avoid crashing ESP32
        current_time = time.time()
        if current_time - self.last_send_time < 0.5:
            return

        json_payload = COMMAND_MAP.get(command_name)
        if not json_payload:
            return

        self.last_command_sent = command_name
        self.last_send_time = current_time

        # Start a background thread for the network request
        thread = threading.Thread(target=self._dispatch_request, args=(command_name, json_payload))
        thread.daemon = True
        thread.start()

    def _dispatch_request(self, command_name, json_payload):
        url = f"{self.base_url}/js"
        params = {"json": json_payload}
        try:
            response = self.session.get(url, params=params, timeout=1.0)
            if response.status_code == 200:
                print(f"[>] Sent {command_name.upper()} (OK)")
            else:
                print(f"[!] Sent {command_name.upper()} (HTTP {response.status_code})")
        except Exception as e:
            # If a command fails, reset last_command_sent so we can try again
            self.last_command_sent = None 
            print(f"[X] Network Error: {str(e)[:50]}...")
            pass

# -------------------------------------------------------------------------
# CORTEX CLIENT
# -------------------------------------------------------------------------

class CortexClient:
    def __init__(self):
        self.ws = None
        self.auth_token = None
        self.session_id = None
        self.headset_id = None
        self.request_id = 1
        self.rover = RoverController(ROVER_IP, ROVER_PORT)
        
        # State tracking
        self.is_connected = False
        self.response_queue = {} # Map request_id to response

    def connect(self):
        print(f"[*] Connecting to Cortex at {CORTEX_URL}...")
        # Cortex uses self-signed certs for localhost
        self.ws = websocket.WebSocketApp(
            CORTEX_URL,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        # Verify=False because of localhost self-signed cert
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    def send_request(self, method, params=None):
        req_id = self.request_id
        self.request_id += 1
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": req_id
        }
        
        if self.ws:
            self.ws.send(json.dumps(payload))
            return req_id
        return None

    def on_open(self, ws):
        print("[*] WebSocket Connected.")
        self.is_connected = True
        
        # Start the setup flow in a separate thread to not block the WP loop
        threading.Thread(target=self.setup_flow).start()

    def on_message(self, ws, message):
        data = json.loads(message)
        
        # Handle async subscription data
        if "sid" in data:
            self.handle_stream_data(data)
            return

        # Handle formatting of simple results
        if "result" in data:
            # print(f"DEBUG: {data}")
            pass
            
        if "error" in data:
            print(f"[!] API Error: {data['error']['message']}")

        # Store response for synchronous-looking calls if needed
        # (Simplified for this script: mostly we just fire and forget in the setup flow)
        if "id" in data:
            self.response_queue[data["id"]] = data

    def on_error(self, ws, error):
        print(f"[!] WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("[*] WebSocket Closed.")
        self.is_connected = False

    def wait_for_response(self, req_id, timeout=5):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if req_id in self.response_queue:
                resp = self.response_queue.pop(req_id)
                return resp
            time.sleep(0.1)
        return None

    # ---------------------------------------------------------------------
    # SYSTEM SETUP FLOW
    # ---------------------------------------------------------------------
    def setup_flow(self):
        time.sleep(1) # Give socket a moment
        
        # 1. Request Access (Approve in Emotiv App if needed)
        print("[1] Requesting Access...")
        req = self.send_request("requestAccess", {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET
        })
        resp = self.wait_for_response(req, timeout=20) # Long timeout for manual approval
        if not resp or "error" in resp:
            print("[!] Access Denied or Timeout. Please check Emotiv App.")
            return

        # 2. Authorize (Get Token)
        print("[2] Authorizing...")
        req = self.send_request("authorize", {
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET,
            "debit": 1
        })
        resp = self.wait_for_response(req)
        if not resp or "result" not in resp:
            print("[!] Authorization failed.")
            return
        
        self.auth_token = resp["result"]["cortexToken"]
        print("[+] Authorized successfully!")

        # 3. Query Headsets
        print("[3] Searching for headset...")
        while not self.headset_id:
            req = self.send_request("queryHeadsets")
            resp = self.wait_for_response(req)
            if resp and "result" in resp and len(resp["result"]) > 0:
                self.headset_id = resp["result"][0]["id"]
                status = resp["result"][0]["status"]
                print(f"[+] Found Headset: {self.headset_id} (Status: {status})")
            else:
                print("... No headset found. Is it on and connected? Retrying in 3s...")
                time.sleep(3)
        
        # 4. Create Session
        print("[4] Creating Session...")
        req = self.send_request("createSession", {
            "cortexToken": self.auth_token,
            "headset": self.headset_id,
            "status": "open"  # Changed from 'active' for better compatibility
        })
        resp = self.wait_for_response(req)
        if not resp or "result" not in resp:
            print("[!] Failed to create session.")
            return
        
        self.session_id = resp["result"]["id"]
        print(f"[+] Session Created: {self.session_id}")

        # 5. Subscribe to Mental Commands (com)
        print("[5] Subscribing to Mental Commands...")
        req = self.send_request("subscribe", {
            "cortexToken": self.auth_token,
            "session": self.session_id,
            "streams": ["com"]
        })
        resp = self.wait_for_response(req)
        if not resp or "result" not in resp:
            print("[!] Failed to subscribe.")
            return
        
        print("\n" + "="*50)
        print(" SYSTEM READY - LISTENING FOR THOUGHTS")
        print("="*50 + "\n")

    # ---------------------------------------------------------------------
    # DATA HANDLER
    # ---------------------------------------------------------------------
    def handle_stream_data(self, data):
        # Format: { "sid": "...", "com": ["push", 0.72] }
        if "com" in data:
            command_data = data["com"]
            action = command_data[0]
            power = command_data[1]
            
            # --- FAIL-SAFE STOP LOGIC ---
            # If the headset is not confident (power < 0.3) OR the thought is Neutral, 
            # we tell the car to STOP immediately.
            if power < 0.3 or action == "neutral":
                # We only log this once in a while to keep terminal clean
                if self.rover.last_command_sent != "neutral":
                    print(f"Detected: NEUTRAL/STOP ({int(power*100)}%)")
                self.rover.send_command("neutral", "neutral")
            else:
                # Active command (Push, Left, Right)
                print(f"Detected: {action.upper()} ({int(power*100)}%)")
                self.rover.send_command(action, action)

if __name__ == "__main__":
    client = CortexClient()
    try:
        client.connect()
    except KeyboardInterrupt:
        print("\nStopping...")
