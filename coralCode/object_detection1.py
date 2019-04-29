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

mutex = Lock()
interrupt = 0

# Function to read labels from text files.
def ReadLabelFile(file_path):
  with open(file_path, 'r') as f:
    lines = f.readlines()
  ret = {}
  for line in lines:
    pair = line.strip().split(maxsplit=1)
    ret[int(pair[0])] = pair[1].strip()
  return ret

def hardware_interrupt():
  times_pressed = 0
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(3,GPIO.IN)
  while(1):
    i,times_pressed = GPIO.input(3)
    time.sleep(0.2)
    times_pressed = times_pressed + GPIO.input(3)
    if(times_pressed == 1):
      mutex.acquire()
      try:
        interrupt = 1 
      finally:
        mutex.release()
    elif(times_pressed == 2):
      mutex.acquire()
      try:
        interrupt = 2
      finally:
        mutex.release()
    time.sleep(0.25)

def text_to_speech():
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
  button_t = Thread(target = hardware_interrupt)
  text_to_speech_t = Thread(target = text_to_speech)

  button_t.start()
  with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 30
    _, width, height, channels = engine.get_input_tensor_shape()
    try:
      stream = io.BytesIO()
      while(1):
        for foo in camera.capture(stream,format='rgb', use_video_port=True, resize=(width, height)): 
          stream.truncate()
          stream.seek(0)
          input = np.frombuffer(stream.getvalue(), dtype=np.uint8)
          result = engine.DetectWithImage(input, threshold = 0.25, keep_aspect_ratio = True, relative_coord = False, top_k = 5)
          if results:
            # Start thread to run text to speech, when done, quit thread
            call_text_to_speech.start()

        # Button Hardware Interrupt Code
        start_ms = time.time()
        while(1):	
          time.sleep(0.25)
          elapsed_ms = time.time() - start_ms
          mutex.acquire()
          try:
            if(interrupt == 2):
              call("sudo shutdown -h now")
            elif(interrupt == 1):
              interupt = 0 
              mutex.release()
              break
          finally:
            mutex.release() 
          if(elapsed_ms > 50000) :
            break

if __name__ == '__main__':
  main()
