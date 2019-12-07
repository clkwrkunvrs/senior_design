import serial
import time

ser = serial.Serial('COM3', 9600,timeout=0)
time.sleep(2)
ser.write(b'H')
time.sleep(2)
ser.write(b'L')
time.sleep(2)
ser.write(b'H')
time.sleep(2)
ser.close()
