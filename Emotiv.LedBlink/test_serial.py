import serial
import time

# configuration
COM_PORT = 'COM5'  # Update this if your ESP32 is on a different port
BAUD_RATE = 115200

try:
    esp = serial.Serial(COM_PORT, BAUD_RATE)
    print(f"Connected to {COM_PORT} at {BAUD_RATE}")
    time.sleep(2)  # Wait for connection to stabilize

    while True:
        print("Sending LED ON...")
        esp.write(b'1')
        time.sleep(2)

        print("Sending LED OFF...")
        esp.write(b'0')
        time.sleep(2)

except serial.SerialException as e:
    print(f"Error opening serial port {COM_PORT}: {e}")
except KeyboardInterrupt:
    print("\nExiting...")
    if 'esp' in locals() and esp.is_open:
        esp.close()
