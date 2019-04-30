"""NAVSENSE Object Detection Program

For use with the Coral Accelerator and the Raspberry Pi 3B+

For Raspberry Pi, you need to install 'feh' as image viewer:
sudo apt-get install feh

Example:
	python3 obj_detection.py --model models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite --label models/coco_labels.txt
"""

import argparse
import platform
import subprocess
import picamera
import RPi.GPIO as GPIO
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from threading import Thread, Lock

button_mutex = Lock()
ttx_mutex = Lock()
interrupt = 0
# Exit ttx function when set to 1
stop_ttx = 0

# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

def hardware_interrupt(ttx_t):
  GPIO.setmode(GPIO.BOARD)
  GPIO.add_event_detect(3,GPIO.RISING)
  while True:
    if GPIO.event_detected(3) or input() :
      # if button pressed again within 2 seconds, shutdown
      stop = time.time() + 2
      while time.time() < stop:
        if GPIO.event_detected(3) or input():
         GPIO.cleanup()
         call("sudo shutdown -h now") 
      button_mutex.acquire()
      interrupt = 1 
      button_mutex.release()
      if ttx_t.isAlive():
        ttx_mutex.acquire()
        stop_ttx = 1 
        ttx_mutex.release()

def text_to_speech(result,labels):
  # Jack's Code
  print("Running Text To Speech")

def main():
  # Parse Arguments
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--model', help='Path of the detection model.', required=True)
  parser.add_argument(
      '--label', help='Path of the labels file.', required = True)
  args = parser.parse_args()

  # Initialize engine.
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None

  # Initialize Threads
  ttx_t = Thread(target = text_to_speech,args = (result,args))
  button_t = Thread(target = hardware_interrupt,args = (ttx_t))

  # Initialize Hardware Interrupt
  button_t.start()
  with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()
    stream = io.BytesIO()
  while True:
    for foo in camera.capture(stream,format='rgb', use_video_port=True, resize=(width, height)): 
      stream.truncate()
      stream.seek(0)
      input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
      result = engine.DetectWithImage(input, threshold = 0.25, keep_aspect_ratio = True, relative_coord = False, top_k = 5)
      if results:
        # Start thread to run text to speech, when done, quit thread
        call_text_to_speech.start(result,args)

      # Sleep and check for hardware interrupt code
      start_ms = time.time()
      while True:	
        time.sleep(0.25)
        elapsed_ms = time.time() - start_ms
        button_mutex.acquire()
        if interrupt == 1:
          interupt = 0 
          button_mutex.release()
          break
        button_mutex.release() 
        if elapsed_ms > 50000:
          break

if __name__ == '__main__':
  main()
