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
import time
import io
from picamera import PiCamera
import RPi.GPIO as GPIO
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from threading import Thread, Lock
from espeak import espeak

button_mutex = Lock()
ttx_mutex = Lock()
interrupt = 0
# Exit ttx function when set to 1
stop_ttx = 0

def multiples(dictionary, arr):
    st = ''
    if len(arr) != 0:
        for key, value in arr.items():
            if value == 1:
                s = str(key)
                st += 'one ' + dictionary[s] + ', '
            if value <= 5 and value > 1:
                st += str(value) + ' '
                if key != 1:
                    s = str(key)
                    st += dictionary[s] + 's, '
                else:
                    st += 'people, '
            if value > 5:
                st += 'several '
                if key != 1:
                    s = str(key)
                    st += dictionary[s] + 's, '
                else:
                    st += 'people, '
    else:
        st = 'Nothing '
    return st

def countItems(dictionary, arr):
    counter = collections.Counter(arr)
    c = dict(counter)
    str = multiples(dictionary, c)
    return str

def parseObjects(obs):
    left = []
    center = []
    right = []
    # Parse Objects
    for o in objs:
        if o[1] < 100 and o[3] < 100:
            left.append(o[0])
        #if it creeps into center mark it as center
        elif (o[1] >= 100 and o[1] <= 200) or (o[3] >= 100 and o[3] <= 200):
            center.append(o[0])
        elif o[1] > 200 and o[3] < 300:
            right.append(o[0])
    return left, center, right

def constructString(dictionary, objs):
    string = 'There is '
    left, center, right = parseObjects(objs)
    lStr = countItems(dictionary, left) + 'to your left. '
    cStr = countItems(dictionary, center) + 'straight ahead. '
    rStr = countItems(dictionary, right) + 'to your right.'
    string += lStr + cStr + 'And ' + rStr
    return string

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
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(3,GPIO.IN,pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(3,GPIO.RISING)
  while True:
    if GPIO.event_detected(3):
      # if button pressed again within 2 seconds, shutdown
      stop = time.time() + 2
      while time.time() < stop:
        if GPIO.event_detected(3):
         GPIO.cleanup()
         call("sudo shutdown -h now")
      button_mutex.acquire()
      interrupt = 1
      button_mutex.release()

def text_to_speech(result,labels):
  # Jack's Code
  print("Running Text To Speech")
  string = constructString(labels, result)
  espeak.synth(string)

def main():
  espeak.synth('Welcome to NavSense')
  # Parse Arguments
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--model', help='Path of the detection model.', required=True)
  parser.add_argument(
      '--label', help='Path of the labels file.', required = True)
  args = parser.parse_args()

  # Initialize engine.
  espeak.synth('Loading Object Recognition Models')
  engine = DetectionEngine(args.model)
  labels = ReadLabelFile(args.label) if args.label else None
  result = None
  camera = PiCamera()
  # Initialize Threads
  button_t = Thread(target = hardware_interrupt)

  # Initialize Hardware Interrupt
  button_t.start()

  while True:
    camera.capture('/home/pi/NavSense/coralCode/image.jpg')
    image = Image.open('image.jpg')

    result = engine.DetectWithImage(image, threshold = 0.25, keep_aspect_ratio = True, relative_coord = False, top_k = 5)
    if result:
      # Start thread to run text to speech, when done, quit thread
      text_to_speech(result, labels)

    # Sleep and check for hardware interrupt code
    start_ms = time.time()
    while True:
      print("loop")
      time.sleep(0.25)
      elapsed_ms = time.time() - start_ms
      button_mutex.acquire()
      if interrupt == 1:
        interupt = 0
        button_mutex.release()
        break

      button_mutex.release()
      if elapsed_ms > 5:
        break

if __name__ == '__main__':
  main()
