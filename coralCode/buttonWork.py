import RPi.GPIO as GPIO
import time

# Button interrupt function
def hardware_interrupt(channel):
    print("inference button was pressed")


def button_up(channel):
    print("UP")
    GPIO.remove_event_detect(channel)

    if GPIO.input(35):
        print("Volume up")
    else:
        print("speeking speed up")
    time.sleep(0.2)
    GPIO.add_event_detect(channel, GPIO.FALLING,
                          callback=button_up, bouncetime=300)

def button_down(channel):
    print("DOWN")
    GPIO.remove_event_detect(channel)
    if GPIO.input(35):
        print("volume down")
    else:
        print("speeking speed down")
    time.sleep(0.2)
    GPIO.add_event_detect(channel, GPIO.FALLING,
                          callback=button_down, bouncetime=300)


def power_off(channel):
    GPIO.remove_event_detect(channel)
    print("OFF")
    time.sleep(0.2)
    GPIO.add_event_detect(channel, GPIO.FALLING,
                          callback=button_down, bouncetime=300)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Start of button interrupt
GPIO.add_event_detect(
    3, GPIO.FALLING, callback=hardware_interrupt, bouncetime=300)
# Button up
GPIO.add_event_detect(
    11, GPIO.FALLING, callback=button_up, bouncetime=300)
# Button down
GPIO.add_event_detect(
    29, GPIO.FALLING, callback=button_down, bouncetime=300)
# Power off
GPIO.add_event_detect(
    32, GPIO.FALLING, callback=power_off, bouncetime=300)
# Switch up: 35
# Switch down: 38

while True:
    continue
