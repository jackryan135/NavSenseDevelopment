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
import csv
from picamera import PiCamera
import RPi.GPIO as GPIO
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
from threading import Thread, Lock
import collections
import os 
import pyttsx3

# Global Variables
speech = pyttsx3.init()
buttonMutex = Lock()
interrupt = 0
speakingSpeed = 150
volume = 1


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


def count_items(dictionary, arr):
    counter = collections.Counter(arr)
    c = dict(counter)
    str = multiples(dictionary, c)
    return str


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


def constructString(dictionary, objs):
    string = 'There is '
    left, center, right = parse_objects(objs)
    lStr = count_items(dictionary, left) + 'to your left. '
    cStr = count_items(dictionary, center) + 'straight ahead. '
    rStr = count_items(dictionary, right) + 'to your right.'
    string += lStr + cStr + 'And ' + rStr
    return string

# Function to read labels from text files.


def read_label_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    ret = {}
    for line in lines:
        pair = line.strip().split(maxsplit=1)
        ret[int(pair[0])] = pair[1].strip()
    return ret


def hardware_interrupt(channel):
    global interrupt

    # if button pressed again within 2 seconds, shutdown
    stop = time.time() + 2
    GPIO.remove_event_detect(3)
    while time.time() < stop:
        if GPIO.input(3):
            GPIO.cleanup()
            save_settings()
            os.remove("image.jpg")
            speech.say("Device Turning Off")
            speech.runAndWait()
            call("sudo shutdown -h now")
    buttonMutex.acquire()
    interrupt = 1
    buttonMutex.release()
    GPIO.add_event_detect(3, GPIO.FALLING, callback=hardware_interrupt, bouncetime=300)



def text_to_speech(result, labels):
    # Jack's Code
    string = constructString(labels, result)
    speech.say(string)
    speech.runAndWait()


def set_speaking_speed():
    global speakingSpeed
    speech.setProperty('rate', speakingSpeed)


def set_volume():
    global volume
    speech.setProperty('volume', volume)


def parse_settings():
    global speakingSpeed
    global volume

    exists = os.path.isfile('settings.csv')
    if not exists:
        with open('settings.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_NONE)
            writer.writerow('150')
            writer.writerow('1')
            speakingSpeed = 150
            volume = 1
    else:
        with open('settings.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            speakingSpeed = int(next(reader))
            volume = int(next(reader))
            print('_______________________________________')
            print(speakingSpeed)
            print(volume)
            print('_______________________________________')


def save_settings():
    global speakingSpeed
    global volume

    with open('settings.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimeter=' ', quoting=csv.QUOTE_NONE)
        writer.writerow(speakingSpeed)
        writer.writerow(volume)


def main():
    global speakingSpeed
    global volume
    global interrupt

    parse_settings()

    set_speaking_speed()
    set_volume()

    speech.say('Welcome to NavSense')
    speech.runAndWait()
    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model', help='Path of the detection model.', required=True)
    parser.add_argument(
        '--label', help='Path of the labels file.', required=True)
    args = parser.parse_args()

    # Initialize engine.
    speech.say('Loading Object Recognition Models')
    speech.runAndWait()
    engine = DetectionEngine(args.model)
    labels = read_label_file(args.label) if args.label else None
    result = None
    camera = PiCamera()
    camera.rotation = 180    
    # Initialize GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(3, GPIO.FALLING,callback=hardware_interrupt,bouncetime = 300)

    speech.say("Device Is Ready To Use")
    speech.runAndWait()
    while True:
        camera.capture('image.jpg')
        image = Image.open('image.jpg')
        image.show()

        result = engine.DetectWithImage(
            image, threshold=0.25, keep_aspect_ratio=True, relative_coord=False, top_k=10)
        if result:
            # Start thread to run text to speech, when done, quit thread
            text_to_speech(result, labels)

        # Sleep and check for hardware interrupt code
        start_ms = time.time()
        while True:
            print('loop')
            time.sleep(0.25)
            elapsed_ms = time.time() - start_ms
            buttonMutex.acquire()
            if interrupt == 1:
                interupt = 0
                buttonMutex.release()
                break

            buttonMutex.release()
            if elapsed_ms > 5:
                break


if __name__ == '__main__':
    main()
