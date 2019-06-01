import RPi.GPIO as GPIO

# Button interrupt function
def hardware_interrupt(channel):
    print("inference button was pressed")


def button_up(channel):
    print("UP")
    if not GPIO.input(35):
        print("Volume up")
    elif not GPIO.input(38):
        print("speeking speed up")


def button_down(channel):
    print("DOWN")
    if not GPIO.input(35):
        print("volume down")
    if not GPIO.input(38):
        print("speeking speed down")


def power_off(channel):
    print("OFF")


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(32, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(35, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(38, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
