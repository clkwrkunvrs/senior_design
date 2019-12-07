from pyfirmata import Arduino, util
import time
board = Arduino("COM3")
stepsPerRev = 200
desiredSteps = 50 
#pin numbers to write
s1 = 8
s2 = 9
s3 = 10 
s4 = 11 
board.digital[s2].write(0)
board.digital[s3].write(0)
board.digital[s1].write(0)
board.digital[s4].write(0)
#take 50 steps
#for x in range(desiredSteps)):
while(1):
 # board.digital[8].write(1)
 # board.digital[9].write(1)
  #board.digital[8].write(1)
  #board.digital[9].write(0)
  #time.sleep(0.05)
  #board.digital[8].write(0)
  #time.sleep(0.05)
  #other way
  board.digital[11].write(1)
  board.digital[10].write(0)
  time.sleep(0.05)
 # board.digital[11].write(0)
 # time.sleep(0.05)
 # board.digital[10].write(0)
#while(1):
#    board.digital[13].write(1)
#    time.sleep(0.5)
#    board.digital[13].write(0)

