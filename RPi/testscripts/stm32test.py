import serial
import time

# Test your serial port
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    print(f"Connected to {ser.name}")
    print("Waiting for messages... (Press Ctrl+C to stop)")
    
    # Wait for messages indefinitely
    while True:
        response = ser.readline().decode('utf-8').strip()
        if response:
            print(f"Received: {response}")
    
except KeyboardInterrupt:
    print("\nStopped by user")
    ser.close()
    print("Connection closed")
except Exception as e:
    print(f"Connection failed: {e}")