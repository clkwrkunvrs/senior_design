import serial
import time

arduino = serial.Serial('COM3', 9600)
print("arduino is: " + str(arduino))
time.sleep(2)

line  = arduino.readline(22)
#print ("Enter '1' to turn 'on' the LED and '0' to turn LED 'off'")
test = 0
while (1):

#    var = raw_input()
#    print "You Entered :", var

    if(test == 0):
        arduino.write(0)
#        print("LED turned on")
        test = 1
        time.sleep(4)
        
        
    if(test == 1):
        arduino.write(1)
        print("pull trigger")
        test = 0 
        time.sleep(4)

#    if(test == '2'):
#        arduino.write('2')
#        print("release trigger")
#        test = 0
#        time.sleep(4)

