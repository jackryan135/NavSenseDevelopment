"""NAVSENSE Object Detection Program

Created by:
Jack Ryan, Daniel Okazaki, Michael Dallow

Advisor:
Professor Behnam Dezfouli

In association with:
Andalo
Santa Clara University 
Frugal Innovation Hub

For use with the Coral Accelerator and the Raspberry Pi 3B+

Example:
	python3 obj_detection.py
"""

import platform
import subprocess
import time
import io
from picamera import PiCamera
import RPi.GPIO as GPIO
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from threading import Thread, Lock
import collections
import os 
import pyttsx3
import tfmini3
import serial

# Global Variables
speech = pyttsx3.init()
buttonMutex = Lock()
interrupt = 0
speakingSpeed = 150
volume = 1
waitTime = 5
ser = serial.Serial("/dev/ttyAMA0", 115200)

# Function to read labels from text files.
def read_label_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret

# Text to speech functions
def text_to_speech(result, labels):
    string = constructString(labels, result)
    speech.say(string)
    speech.runAndWait()

def constructString(dictionary, objs):
    global ser

    dist_str = ""
    distance = tfmini3.getTFminiData(ser)

    if distance == None:
        dist_str = ". "

    if distance > 100:
        dist_str += " in approximately " + str(distance/100) + " meters. "
    else:
        dist_str += " in approximately " + str(distance) + " centimeters. "

    string = 'There is '
    left, center, right = parse_objects(objs)
    lStr = count_items(dictionary, left) + 'to your left. '
    #cStr = count_items(dictionary, center) + 'straight ahead. 
    cStr = count_items(dictionary, center) + 'straight ahead' + dist_str
    rStr = count_items(dictionary, right) + 'to your right.'
    string += lStr + cStr + 'And ' + rStr
    return string

def parse_objects(obs):
    left = []
    center = []
    right = []
    # Parse Objects
    for o in obs:
        box = o.bounding_box.flatten().tolist()
        print(box)
        if box[0] < 640.0 and box[2] < 640.0:
            left.append(o.label_id)
        elif box[0] > 1280.0 and box[2] < 1920.0:
            right.append(o.label_id)
        else:
            center.append(o.label_id)
    return left, center, right

def count_items(dictionary, arr):
    counter = collections.Counter(arr)
    c = dict(counter)
    str = multiples(dictionary, c)
    return str

def multiples(dictionary, arr):
    st = ''
    if len(arr) != 0:
        for key, value in arr.items():
            if value == 1:
                st += 'one ' + dictionary[key] + ', '
            if value <= 5 and value > 1:
                st += str(value) + ' '
                if key != 1:
                    st += dictionary[key] + 's, '
                else:
                    st += 'people, '
            if value > 5:
                st += 'several '
                if key != 1:
                    st += dictionary[key] + 's, '
                else:
                    st += 'people, '
    else:
        st = 'Nothing '
    return st

# Button interrupt function
def hardware_interrupt(channel):
    global interrupt
    global buttonMutex
    global ser
    
    GPIO.remove_event_detect(channel)

    print("button was pressed")
    # if button pressed again within 0.5 seconds, shutdown
    time.sleep(1)
    stop = time.time() + 0.5
    while time.time() < stop:
        if not GPIO.input(channel):
            ser.close()
            print("shutting down device")
            GPIO.cleanup()
            save_settings()
            if os.path.exists('image.jpg'):
                os.remove("image.jpg")
            speech.say("Device Turning Off")
            speech.runAndWait()
            os.system("sudo shutdown -h now")
    buttonMutex.acquire()
    interrupt = 1
    buttonMutex.release()
    GPIO.add_event_detect(channel, GPIO.FALLING, callback=hardware_interrupt, bouncetime=300)
    print("end of interrupt")

# Helper functions
def set_speaking_speed():
    global speakingSpeed
    speech.setProperty('rate', speakingSpeed)


def set_volume():
    global volume
    speech.setProperty('volume', volume)


# Read device settings from file
def parse_settings():
    global speakingSpeed
    global volume

    exists = os.path.exists('settings.txt')
    if not exists:
        file = open('settings.txt', 'w')
        file.write(str(150) + '\n')
        file.write(str(1))
        file.close()
        speakingSpeed = 150
        volume = 1
    else:
        file = open("settings.txt",'r')
        speakingSpeed = int(file.readline())
        volume = int(file.readline())
        file.close()
        print('_______________________________________')
        print(speakingSpeed)
        print(volume)
        print('_______________________________________')


def save_settings():
    global speakingSpeed
    global volume

    file = open('settings.txt', 'w')
    file.write(str(speakingSpeed) + '\n')
    file.write(str(volume))
    file.close()
 

def main():
    global speakingSpeed
    global volume
    global interrupt
    global waitTime

	# Models and label path directories
    model = 'models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    label = 'models/coco_labels.txt'

    # Retrieve speaking speed and volume settings from file
    parse_settings()
    
    # set speaking speed and volume
    set_speaking_speed()
    set_volume()

    speech.say('Welcome to NavSense')
    speech.runAndWait()

    # Initialize engine.
    speech.say('Loading Object Recognition Models')
    speech.runAndWait()
    engine = DetectionEngine(model)
    labels = read_label_file(label)
    result = None

    # Initialize Camera
    camera = PiCamera()
    camera.rotation = 180    

    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    speech.say("Device Is Ready To Use")
    speech.runAndWait()

    # Start of button interrupt 
    GPIO.add_event_detect(3, GPIO.FALLING,callback=hardware_interrupt,bouncetime = 300)

    while True:
        camera.capture('image.jpg')
        image = Image.open('image.jpg')
        #image.show()

        result = engine.DetectWithImage(
            image, threshold=0.25, keep_aspect_ratio=True, relative_coord=False, top_k=10)
        if result:
            # Start thread to run text to speech, when done, quit thread
            text_to_speech(result, labels)
        else:
            speech.say("No object detected")
            speech.runAndWait()
        # Sleep and check for hardware interrupt code
        start_ms = time.time()
        while True:
            print('loop')
            time.sleep(0.25)
            buttonMutex.acquire()
            if interrupt == 1:
                interrupt = 0
                buttonMutex.release()
                print("overriding loop")
                break
            buttonMutex.release()
            elapsed_ms = time.time() - start_ms

			# Wait time in between inferences
            if elapsed_ms > waitTime:
                break


if __name__ == '__main__':
    try:
        if ser.is_open == False:
            ser.open()

    except KeyboardInterrupt:
        if ser != None:
            ser.close()

    main()
