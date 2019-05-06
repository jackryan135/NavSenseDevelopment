import RPi.GPIO as GPIO
import serial
import time

class MB1040:
    # This function should only run once, when device starts
    def __init__(self):
        
        self.bit_delay = 104
        self.half_bit_delay =  52
        self.num_bytes = 5

        GPIO.setmode(GPIO.BOARD)
        self.rx = 10
        self.tx = 8

        GPIO.setup(self.rx, GPIO.IN)
        GPIO.setup(self.tx, GPIO.OUT)

        GPIO.output(self.tx, GPIO.HIGH)

        self.ser = serial.Serial('/dev/ttyAMA0')
        self.usleep = lambda x: time.sleep(x/1000000.0)
       

    def getDistance(self):
        data = []
        invalid_reading = self.readSonar(data)
        
        if not invalid_reading:
            self.printSonarMessage(data)

        self.usleep(100) 


    def end(self):
        self.ser.close()
        GPIO.cleanup()


    def readSonar(self, data):
        i = 0
        invalid = False

        data.append(self.readSonarByte())        

        if (data[0] == 'R'):
            for i in range(0, self.num_bytes):
                data.append(self.readSonarByte())
        else:
            invalid = True

        return invalid


    def readSonarByte(self):
        char = 0
        print(self.ser.read())

        while self.ser.read() == 0: 
            print("Waiting...")
        
        
        if self.ser.read() == GPIO.HIGH:
            self.usleep(self.half_bit_delay)

            for bit_shift in range(0, 7):
                self.usleep(self.bit_delay)
                char |= ((not self.ser.read()) << bit_shift)

            self.usleep(self.bit_delay)

        return char


    def printSonarMessage(self, msg):
        msg[self.num_bytes] = 0
        print(msg)


    def printSonarData(self, data):
        print("\tchar\thex\tdec\tbin")

        for i in range(0, self.num_bytes):
            print(i, "\t", data[i], "\t", end="") #char
            
            #hex
            data_hex = ''.join([hex(ord(x))[2:].zfill(2) for x in data[i]])
            print(data_hex, "\t", end="")
            
            print(ord(data[i]), "\t", end="") #decimal
           
            #binary
            data_bin = ''.join(format(ord(x), 'b') for x in data[i])
            print(data_bin)


mb = MB1040()
mb.getDistance()
#getDistance()
