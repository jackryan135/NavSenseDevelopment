import RPi.GPIO as GPIO
import time

start_pin = 3
end_pin = 11

GPIO.setmode(GPIO.BOARD)
GPIO.setup(start_pin, GPIO.OUT, initial=1)
GPIO.setup(end_pin, GPIO.OUT, initial=1)

GPIO.cleanup()
