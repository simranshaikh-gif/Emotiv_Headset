import websocket
import ssl

# Define the URL for the Cortex service
CORTEX_URL = "wss://localhost:6868"

def on_open(ws):
    print("Connected to Cortex")
    print("Check your Emotiv Launcher for an access request popup!")
    # We just want to trigger the popup, so we can close after a short delay or just wait
    # Keeping it open to ensure connection persists until approved if needed, 
    # but usually the connection request itself triggers the prompt.

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Disconnected from Cortex")

if __name__ == "__main__":
    # Disable SSL verification for localhost self-signed certs
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Newer websocket-client versions use sslopt
    ws = websocket.WebSocketApp(CORTEX_URL,
                                on_open=on_open,
                                on_error=on_error,
                                on_close=on_close)
    
    print(f"Attempting connection to {CORTEX_URL}...")
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
