import serial
import time

ser = serial.Serial("/dev/ttyAMA0", 115200)

def getTFminiData():
    while True:
        time.sleep(5)
        count = ser.in_waiting

        if count > 8:
            recv = ser.read(9)
            ser.reset_input_buffer()

            if recv[0] == 0x59 and recv[1] == 0x59:
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                print('(', distance, ',', strength, ')')
                ser.reset_input_buffer()

            if recv[0] == 'Y' and recv[1] == 'Y':
                lowD = int(recv[2].encode('hex'), 16)
                highD = int(recv[3].encode('hex'), 16)
                lowS = int(recv[4].encode('hex'), 16)
                highS = int(recv[5].encode('hex'), 16)
                distance = lowD + highD * 256
                strength = lowS + highS * 256

                print(distance, strength)


if __name__ == '__main__':
    try:
        if ser.is_open == False:
            ser.open()

        getTFminiData()

    except KeyboardInterrupt:
        if ser != None:
            ser.close()
