from picamera import PiCamera
import time

camera = PiCamera()
avg = 0
for i in range(0,10):
    start = time.time()

    camera.start_preview()
    #time.sleep(2)
    camera.capture('/home/pi/Desktop/SpeedTest/image.jpg')
    camera.stop_preview()

    end = time.time()
    avg = avg + (end-start)
print(avg/i)
