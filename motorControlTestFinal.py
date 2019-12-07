import serial
import time

ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

i = 0
message = ""
while(1):
#    if(direction == b'1'):
#    output = ser.readline()
#    print("serial line says: " + str(output))
#    print("writing direction: " + str(direction) + " to arduino.") 
    ser.write(b'1')
#    print("print1: " + str(ser.readline()))
#    print("print2: " + str(ser.readline()))
#    print("print3: " + str(ser.readline()))
#    time.sleep(4)
    ser.write(b'2') 
    time.sleep(1)
    ser.readline()
    if(ser.readline() == b'done\r\n'):
        break;
#    i = i + 1
#    while(ser.readline() != b'done\r\n'):
#        print("waiting")
#    output = ser.readline()
#    print(output)
#    ser.write(b'2')
#    time.sleep(5)
#    while (output != b'clockwise\r\n')
   # direction = b'0'
    #ser.write(direction)
    #if (direction == b'0'):
    #    direction = b'1'
    #    time.sleep(5)
            
#        direction = b'0' 
#        time.sleep(1)
#    else:
#        direction = b'1'
ser.write(b'3')

