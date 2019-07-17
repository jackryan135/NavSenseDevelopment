import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.output(3, GPIO.HIGH)
GPIO.output(11, GPIO.HIGH)

sleep(1)

GPIO.output(3, GPIO.LOW)
GPIO.output(3, GPIO.HIGH)

sleep(15)
GPIO.output(11, GPIO.LOW)
GPIO.output(11, GPIO.HIGH)

print("Finished")

