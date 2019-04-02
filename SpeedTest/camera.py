from picamera import PiCamera
import time

camera = PiCamera()
avg = 0
for i in range(0,50):
    start = time.time()

    camera.start_preview()
    camera.capture('/home/pi/Desktop/NavSense/SpeedTest/image.jpg')
    camera.stop_preview()

    end = time.time()
    avg = avg + (end-start)
print(avg/i)
