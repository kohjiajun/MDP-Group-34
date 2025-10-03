from picamera2 import Picamera2, Preview
import time

# Check available cameras first
print("Available cameras:")
camera_info = Picamera2.global_camera_info()
print(camera_info)

# Initialize camera with explicit camera index
if len(camera_info) > 0:
    picam2 = Picamera2(camera_num=0)
else:
    print("No cameras found!")
    exit(1)

camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)

#picam2.start_preview(Preview.QTGL)
picam2.start()

time.sleep(2)

picam2.capture_file("/home/gavkujo/MDP-Group-34/RPi/test.jpg")

print("Photo captured as test.jpg")
picam2.stop()
