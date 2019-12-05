import vnakit
from pyfirmata import Arduino, util
import time
# import time
# import vnakit_ex.hidden
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy
import cmath
import math
import math
import random
import serial
'''
Calcs the average background freq domain response
'''

ser = serial.Serial('COM3', 9600, timeout=0)
timeout(2)
class vnaStuff():
    def constructor(self):
        self.an = null
        self.ax1 = null
        self.range_calc = null
        self.az_calc = null
        #THESE ARE AZIMUTH PARAMETERS FOR THE LAUNCHER. ADJUST THEM ACCORDINGLY
        self.left_theta_boundary = 0
        self.right_theta_boundary = 0
#        time.sleep(2)
    def calcBackground():
        N = 10
        bg,bg2,bg3,bg_final,bg_final2,bgfinal3 = []
        # Warm up
        for w_up in range(0, 2*N):
            vnakit.Record()
            junk = vnakit.GetRecordingResult()
        # Avg background noise
        for bgIndex in range(0, N):
            vnakit.Record()
            results = vnakit.GetRecordingResult()
            oneTrial,oneTrial2,oneTrial3 = []
            for sample_p4, sample_p2, sample_p5, sample_p6 in zip(results[4], results[2], results[5], results[6]):
                oneTrial2.append(sample_p5/sample_p2)
                oneTrial.append(sample_p4/sample_p2)
                oneTrial3.append(sample_p6/sample_p2)
            bg.insert(bgIndex, oneTrial)
            bg2.insert(bgIndex, oneTrial2)
            bg3.insert(bgIndex, oneTrial3)
        for i in range(0, len(bg[0])):
            freq_sum = freq_sum2 = freq_sum3 = 0 
            for j in range(0, N):
                freq_sum2 += bg2[j][i]
                freq_sum += bg[j][i]
                freq_sum3 += bg3[j][i]
            bg_final2.append(freq_sum2 / N)
            bg_final.append(freq_sum / N)
            bg_final3.append(freq_sum3 / N)

        return bg_final, bg_final2, bg_final3

    #not sure this 'i' is needed
    def animateTime(i, bg1, bg2, bg3):
        raw1,raw2,raw3 = []
        # Conducts test
        vnakit.Record()
        results = vnakit.GetRecordingResult()

        # Calc S21
        for sample_p4, sample_p2, sample_p5, sample_p6, bg_sample1, bg_sample2, bg_sample3\
                in zip(results[4], results[2], results[5], results[6], bg1, bg2, bg3):
            sample = sample_p4 / sample_p2
            sample2 = sample_p5 / sample_p2
            sample3 = sample_p6 / sample_p2
            raw2.append(sample2)# - bg_sample2)
            raw1.append(sample)# - bg_sample1)
            raw3.append(sample3)# - bg_sample3)

        # Retrieve time domain stuff
        freqs = freqs2 = freqs3 = vnakit.GetFreqVector_MHz() 
        #does this syntax work? What do these do?
        times2, waveform2 = calcTimeDomainModel(freqs2, raw2)
        times, waveform1 = calcTimeDomainModel(freqs, raw1)
        times3, waveform3 = calcTimeDomainModel(freqs3, raw3)

        # Calculate range and angle measurement based on returns for both horns.
        #Get return time for each horn
        range_time1 = times[numpy.argmax(waveform1)]
        range_time2 = times2[numpy.argmax(waveform2)]
        range_time3 = times3[numpy.argmax(waveform3)]
        print('======================================================')
        print(getPosition(waveform1, waveform2, waveform3, range_time1, range_time2, range_time3))
        print('======================================================')
    '''
    Takes a list of freqs and complex samples.
    Returns a time domain rep of data
    '''
    def calcTimeDomainModel(freqsMHz, samples):
        output = []
        freqs = freqsMHz
        for i in range(len(freqs)):
            freqs[i] = freqs[i] * math.pow(10, 6)
        #t = numpy.arange(12 * math.pow(10, -9), 16 * math.pow(10, -9), 2 * math.pow(10, -11))
        t = numpy.arange(30 * math.pow(10, -9), 75 * math.pow(10, -9), 2 * math.pow(10, -11))
        #t = numpy.arange(50 * math.pow(10, -9), 100 * math.pow(10, -9), 2 * math.pow(10, -11))
        for i in range(0, len(freqs)):
            this_cosine = numpy.real(samples[i]) * numpy.cos(2 * numpy.pi * freqs[i] * t + cmath.phase(samples[i]))
            output.append(this_cosine)

        net_cosine = numpy.abs(numpy.sum(output, axis=0))
        return t, net_cosine

    def meetsThreshold(wave):
        if max(wave) > 0.05:
            return True
        else:
            return False

    '''WIP/candidate for position calc/plot'''


    def getPosition(wave1, wave2, wave3, range1, range2, range3):
        result = ''
        light = 299792458 #lightspeed constant
        kposition of each antenna (guess for now, adjust to test setup)
        posLeft = -1
        posRight = 1
        yLeft = []
        yRight = []
        #to be determined
        # based upon horizontal plate results
        #scale = -0.1545 * math.pow(range, 2) + 2.0027*range - 3.47
        #diff_bound = 2
        #slope = 0.1
        if meetsThreshold(wave1) and meetsThreshold(wave2) and meetsThreshold(wave3):
            #Treat the time location of each max as radii of semicircles. Draw the semicircles and split to be in location of both receivers.
            #Plot these.
            #first find the range using the time bump on the center antenna (times3)
            self.range_calc = (light*range3)/4 - 2.97
            #find the range from each side receiver
            range1_calc = light*range1 - self.range_calc - 3.15
            range2_calc = light*range2 - self.range_calc - 3.15
            #calculate maximum/minimum x distance for each antenna
            minLeft = posLeft - range1_calc
            maxLeft = posLeft + range1_calc
            minRight = posRight - range2_calc
            maxRight = posRight + range2_calc
            #Form some arrays of values to plot a semicircle. This is mostly for graphing visuals.
            #y = sqrt((x-a)^2 - r^2), where a is the distance from transmitter of the receiver.
            xRangeLeft = numpy.linspace(minLeft, maxLeft, 100) #always do 100 points. Can adjust to make the plot look nicer.
            xRangeRight = numpy.linspace(minRight, maxRight, 100)
            x2 = 0
            y2 = 0
            h = a = d =0
            for i in range(len(xRangeLeft)): #form left function
                thisY = math.sqrt((xRangeLeft[i] - posLeft)**2 - range1_calc**2)
                yLeft.append(thisY)

            for i in range(len(xRangeRight)): #form right function
                thisY = math.sqrt((xRangeRight[i] - posRight)**2 - range2_calc**2)
                yRight.append(thisY)

            #calculate intersection of the created curves. Use the circle equation generated from each position/radius and take the
            #intersection which is not in quadrants 3 or 4.
            if (maxLeft == maxRight): #coincident circles
                result += "\nAntennas too close together!"
            if(maxLeft < minRight): #non intersecting
                result += "\nNo target detected!"
            else: #calculate intersection points. Starting y vals are 0, and remember that range1_calc/range2_calc are the radii of each circle.
                result += "\nRANGE: " + str(self.range_calc) + " meters (m)" #always output range
                if range1_calc > range2_calc:
                    d = range1_calc - range2_calc
                    a = (range1_calc**2 - range2_calc**2 + d**2) / (2*d)
                    h = math.sqrt(abs(range1_calc**2 - a**2))
                    x2 = range1_calc + a*(range2_calc - range1_calc)/d #only need 1 x calculation (yay)
                    y2 = -1 * h * (range2_calc - range1_calc) / d
                    if y2 < 0:  # if y2 < 0, we calculated the intersection in Q3/Q4 (behind the radar), so find the other and we're done.
                        y2 = h * (range2_calc - range1_calc) / d
                    self.az_calc = math.degrees(math.atan(y2 / x2))  # trig to find the azimuth
                    result += "AZIMUTH: " + str(self.az_calc) + " degrees (deg) LEFT of boresight."
                elif range2_calc > range1_calc:
                    d = range2_calc - range1_calc
                    a = (range2_calc ** 2 - range1_calc ** 2 + d ** 2) / (2 * d)
                    h = math.sqrt(abs(range2_calc ** 2 - a ** 2))
                    x2 = range2_calc + a * (range1_calc - range2_calc) / d  # only need 1 x calculation (yay)
                    y2 = -1 * h * (range1_calc - range2_calc) / d
                    if y2 < 0:  # if y2 < 0, we calculated the intersection in Q3/Q4 (behind the radar), so find the other and we're done.
                        y2 = h * (range2_calc - range1_calc) / d
                    self.az_calc = math.degrees(math.atan(y2 / x2))  # trig to find the azimuth
                    result += "AZIMUTH: " + str(self.az_calc) + " degrees (deg) RIGHT of boresight."
                else: #if equal, we're on boresight.
                    x2 = 1
                    y2 = 0
                    self.az_calc = 0
                    result += "AZIMUTH: 0 degrees, ON BORESIGHT."
            #plot left
            self.ax1.clear()
            self.ax1.plot(xRangeLeft, yLeft, c='r')
            #why is the label for both x and y the same???
            self.ax1.set_xlabel('Position, m')
            self.ax1.set_ylabel('Position, m')
            #draw position of receiver
            self.ax1.scatter(posLeft, 0, s=50, c='r')
            #plot right
            self.ax1.plot(xRangeRight, yRight, c='b')
            self.ax1.set_xlabel('Position, m')
            self.ax1.set_ylabel('Position, m')
            #draw receiver
            self.ax1.scatter(posRight, 0, s=50, c='b')
            #Draw transmitter
            self.ax1.scatter(0,0, s=50, c='m')
            #Draw point for intersection
            self.ax1.scatter(x2, y2, s=50, c='m')
            #plot a line between transmit and intersect
            self.ax1.plot([0, x2], [0, y2], c='m')
        else:
            result += '\nNo target detected!'
        #plot position
        plotPosition(self.az_calc,self.range_calc)
        #pull launcher trigger if in boresite
        pullTrigger()
        return result
    
    def plotPosition(currentTheta=0, currentR=0):
            #initialize theta and R
            #currentTheta = 0
            #currentR = 0
            #set up polar plt
            ax = plt.subplot(111, projection="polar")
            #axPos.set_ylim([0,30])
            #enable interactive mode so the plot doesn't close and open and is non-blocking
            plt.ion()
            plt.show()
            #just for demonstration
            countingUp = True
            #while(1):
            #***demo stuff***
            #currentTheta = random.randrange(0,359)
            currentTheta += 5 
            #currentR = random.randrange(0,10)
            if(currentR == 30):
                countingUp = False
            elif(currentR == 0):
                countingUp = True
            if(countingUp):
                currentR += 0.75
            else:
                currentR -= 0.75
            #***demo stuff end***
            #set theta and r
            theta = [0,math.radians(currentTheta)]
            r = [0,currentR]
            #clear plot and prep for redraw
            axPos.cla()
            #set limit on polar plot range
            axPos.set_ylim([0,30])
            #tell the user what the range is at the moment in the bottom left corner
            axPos.annotate('Range: {:0.2f}'.format(currentR) + " Feet",
                    xy=(currentTheta, currentR),  # theta, radius
                    xytext=(0.05, 0.05),    # fraction, fraction
                    textcoords='figure fraction',
            #        arrowprops=dict(facecolor='black', shrink=0.05),
                    horizontalalignment='left',
                    verticalalignment='bottom',
                    )
            #plot first a red diamond and then a red line, both for position
            axPos.plot(theta, r,'^r')
            axPos.plot(theta, r,'-r')
            #give the plot a moment to breathe and do its processing
            plt.pause(0.05)

    def pullTrigger():
       ser.write(b'1')
       time.sleep(2)
       while(self.ser.readline() != b'done\r\n'):
        print("waiting for launcher to reset")

""""--------------------------------------------------------------------------------------------------------------------
main
---------------------------------------------------------------------------------------------------------------------"""
if __name__ == '__main__':
    vnakit.Init()
    vnaStuff vnas
    '''
    settings in freq range (mhz),
    rbw (khz),
    power level (dbm),
    tx port,
    port setup to record
    '''
    settings = vnakit.recordingsettings(
        vnakit.frequencyrange(2500, 3000, 100),
        1,
        0,
        3,
        vnakit.vnakit_mode_two_ports
    )
    vnakit.ApplySettings(settings)
    #may need to move where this plot displays to avoid collision with the radar position plot 
    fig1 = plt.figure()
    sleep(0.001)
    vnas.ax1 = fig1.add_subplot(1, 1, 1)
    #does this work?
    backg = backg2 = backg3 = vnas.calcbackground()
    #animateTime calls getposition and plotposition
    vnas.an = ani.funcAnimation(fig1, vnas.animateTime, fargs=(backg, backg2, backg3), interval=50)
    plt.show()

