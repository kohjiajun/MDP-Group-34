'''
from picamera2 import Picamera2
import time

# Initialize camera
picam2 = Picamera2()

# Start camera
picam2.start()

# Wait for camera to be ready
time.sleep(2)

# Capture frame as a NumPy array
frame = picam2.capture_array()

# Save the photo
img = Image.fromarray(frame)
img.save("test.jpg")

print("Photo captured as test.jpg")
'''
