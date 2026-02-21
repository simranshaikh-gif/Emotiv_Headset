import websocket
import json
import serial
import time
import ssl
import threading

# --- CONFIGURATION ---
# Note: CLIENT_ID and CLIENT_SECRET are usually needed for full apps.
# For local testing, sometimes default/empty works if you approve in Launcher.
CLIENT_ID = "SJp8zTW9D0abRSfEM11393aCeEcf5H6HWWsl97gk" 
CLIENT_SECRET = "R3e7Ej24RjAPnG93TlmcfOmzXWTCXstSCRLKN38ebDnvv9oIOe27xsOQbz5GNGoTdFY7ogtHjRLc391OYHB7GieP8HX287nyGpFlmFb3Y7NoYwYcrewE4BrreDj3xPRp"

COM_PORT = 'COM5'
BAUD_RATE = 115200
CORTEX_URL = "wss://localhost:6868"

# --- GLOBAL STATE ---
socket = None
auth_token = None
session_id = None
headset_id = None
blink_count = 0
last_time = 0
led_state = False
esp = None

# --- SERIAL SETUP ---
def setup_serial():
    global esp
    try:
        esp = serial.Serial(COM_PORT, BAUD_RATE)
        print(f"Serial connected on {COM_PORT}")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Serial Error: {e}")
        return False

# --- CORTEX HELPERS ---
def send_request(method, params=None):
    req = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": 1
    }
    socket.send(json.dumps(req))

def on_open(ws):
    print("Connected to Cortex! Starting setup...")
    # Step 1: Request Access (triggers popup)
    send_request("requestAccess", {
        "clientId": CLIENT_ID,
        "clientSecret": CLIENT_SECRET
    })

def on_message(ws, message):
    global auth_token, session_id, headset_id, blink_count, last_time, led_state, esp

    data = json.loads(message)
    
    # Handle Responses (Auth flow)
    if "result" in data:
        res = data["result"]
        if "accessGranted" in res and res["accessGranted"]:
            print("Access Granted! Authorizing...")
            send_request("authorize", {"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET, "debit": 1000})
        elif "cortexToken" in res:
            auth_token = res["cortexToken"]
            print("Authorized! Searching for headset...")
            send_request("queryHeadsets")
        elif isinstance(res, list) and len(res) > 0:
            headset_id = res[0]["id"]
            print(f"Found Headset: {headset_id} ({res[0]['status']})")
            if res[0]["status"] in ["connected", "detected"]:
                send_request("createSession", {"cortexToken": auth_token, "headset": headset_id, "status": "active"})
            else:
                print("Headset not connected properly yet. Retrying...")
                time.sleep(2)
                send_request("queryHeadsets")
        elif "id" in res and "appId" in res:
            session_id = res["id"]
            print(f"Session Created ({session_id})! Subscribing to 'fac' (Facial)...")
            send_request("subscribe", {"cortexToken": auth_token, "session": session_id, "streams": ["fac"]})
        elif "success" in res and "streams" in res:
            print("SUBSCRIBED! Detecting Blinks now...")
            print("--> PLEASE BLINK FIRMLY <--")

    if "error" in data:
        print(f"Cortex Error: {data['error']['message']}")

    # Handle Stream Data (fac) with DEBUG PRINTS
    if "fac" in data:
        try:
            # Print raw data so we can see what key/index the blink is on
            # fac = [eyeAct, uAct, lAct, eyebrows, smile, clench...]
            fac_data = data["fac"]
            # specific index varies by headset version. Let's just print "Blink" if any value is high
            
            # The first value is usually the action (e.g. 'blink', 'winkL', 'winkR')
            action = fac_data[0] 
            power = fac_data[1] if len(fac_data) > 1 else 0

            # Only print if something interesting is happening (to avoid spam)
            if action != 'neutral': 
                 print(f"Action: {action} | Power: {power}")

            # Logic for "blink" or "wink"
            if action in ['blink', 'winkL', 'winkR'] or (isinstance(action, (int, float)) and action > 0.5):
                current_time = time.time()
                
                if current_time - last_time > 0.2: # Simple debounce
                    if current_time - last_time < 1.0:
                        blink_count += 1
                        print(f"!!! BLINK DETECTED !!! Count: {blink_count}")
                    else:
                        blink_count = 1
                        print("!!! BLINK DETECTED !!! Count: 1")
                    
                    last_time = current_time

                    if blink_count >= 2:
                        led_state = not led_state
                        cmd = b'1' if led_state else b'0'
                        if esp: esp.write(cmd)
                        print(f"*** DOUBLE BLINK -> LED {'ON' if led_state else 'OFF'} ***")
                        blink_count = 0
        except Exception as e:
            print(f"Error parsing data: {e} | Raw: {data['fac']}")

def on_error(ws, error):
    print(f"Socket Error: {error}")

def on_close(ws, close_status, close_msg):
    print("Socket Closed")

# --- MAIN ---
if __name__ == "__main__":
    setup_serial()
    
    # Disable SSL verify
    socket = websocket.WebSocketApp(CORTEX_URL,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
    socket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
