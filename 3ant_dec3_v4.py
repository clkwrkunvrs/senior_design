import vnakit
from pyfirmata import Arduino, util
import time
import vnakit_ex.hidden
import matplotlib.pyplot as plt
import numpy
import cmath
import math

class vnaStuff():
    def __init__(self):
        self.an = None
        self.ax1 = None
        self.axPolar = None
        self.axTime = []
        self.range_calc = 0
        # THESE ARE AZIMUTH PARAMETERS FOR THE LAUNCHER. ADJUST THEM ACCORDINGLY
        self.az_calc = 0
        self.left_theta_boundary = 0
        self.right_theta_boundary = 0

    @staticmethod
    def generateEllipse(dist, separation):
        a = dist - separation
        c = separation / 2
        b = numpy.sqrt(a ** 2 - c ** 2)
        x = numpy.linspace(-1 * a, a, 200)
        y = numpy.sqrt(b ** 2 * (1 - (x / a) ** 2))
        return x, y

    def findIntersection(self, x1, y1, x2, y2):
        x_pts = []
        y_pts = []


        tol = 0.075
        # find x subset
        x_min = max(x1[0], x2[0])
        x_max = min(x1[-1], x2[-1])
        # find y_subset
        y_max = min(max(y1), max(y2))
        y_min = 0
        # print(y_max)
        ind = 1
        for x1_i in range(len(x1)):
            for x2_i in range(len(x2)):
                # Test if x points are about equal
                if abs(x1[x1_i] - x2[x2_i]) < tol:
                    # Test if corresponding y points are about equal
                    if abs(y1[x1_i] - y2[x2_i]) < tol:
                        x_pts.append(x1[x1_i])
                        x_pts.append(x2[x2_i])
                        y_pts.append(y1[x1_i])
                        y_pts.append(y2[x2_i])
        if len(x_pts) > 0 and len(y_pts) > 0:
            return numpy.mean(x_pts), numpy.mean(y_pts)
        else:
            return 0, -1

    def calcBackground(self):
        N = 10
        bg, bg2, bg3, bg_final, bg_final2, bg_final3 = ([] for i in range(6))
        # Warm up
        for w_up in range(0, 2 * N):
            vnakit.Record()
            junk = vnakit.GetRecordingResult()
        # Avg background noise
        for bgIndex in range(0, N):
            vnakit.Record()
            results = vnakit.GetRecordingResult()
            oneTrial, oneTrial2, oneTrial3 = ([] for i in range(3))
            for sample_p4, sample_p2, sample_p5, sample_p6 in zip(results[4], results[2], results[5], results[6]):
                oneTrial2.append(sample_p5 / sample_p2)
                oneTrial.append(sample_p4 / sample_p2)
                oneTrial3.append(sample_p6 / sample_p2)
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

    # not sure this 'i' is needed
    def animateTime(self, bg1, bg2, bg3):
        raw1, raw2, raw3 = ([] for i in range(3))
        # Conducts test
        vnakit.Record()
        results = vnakit.GetRecordingResult()
        #print('location3')
        # Calc S21
        for sample_p4, sample_p2, sample_p5, sample_p6, bg_sample1, bg_sample2, bg_sample3 \
                in zip(results[4], results[2], results[5], results[6], bg1, bg2, bg3):
            sample = sample_p4 / sample_p2
            sample2 = sample_p5 / sample_p2
            sample3 = sample_p6 / sample_p2
            raw2.append(sample2 - bg_sample2)
            raw1.append(sample - bg_sample1)
            raw3.append(sample3 - bg_sample3)

        # Retrieve time domain stuff
        freqs = vnakit.GetFreqVector_MHz()
        freqs3 = vnakit.GetFreqVector_MHz()
        freqs2 = vnakit.GetFreqVector_MHz()
        # does this syntax work? What do these do? Yes
        # left horn
        times, waveform1 = vnaStuff.calcTimeDomainModel(freqs, raw1)
        # right horn
        times2, waveform2 = vnaStuff.calcTimeDomainModel(freqs2, raw2)
        # Ice cream cone
        times3, waveform3 = vnaStuff.calcTimeDomainModel(freqs3, raw3)

        # Calculate range and angle measurement based on returns for both horns.
        # Get return time for each horn
        range_time1 = times[numpy.argmax(waveform1)]
        range_time2 = times2[numpy.argmax(waveform2)]
        range_time3 = times3[numpy.argmax(waveform3)]
        print('======================================================')
        print(self.getPosition(waveform1, waveform2, waveform3, range_time1, range_time2, range_time3))
        print('======================================================')
        self.plotTimeDomain(times, waveform1, waveform2, waveform3)
    '''
    Takes a list of freqs and complex samples.
    Returns a time domain rep of data
    '''
    @staticmethod
    def calcTimeDomainModel(freqsMHz, samples):
        output = []
        freqs = freqsMHz
        for i in range(len(freqs)):
            freqs[i] = freqs[i] * math.pow(10, 6)
        # t = numpy.arange(12 * math.pow(10, -9), 16 * math.pow(10, -9), 2 * math.pow(10, -11))
        t = numpy.arange(40 * math.pow(10, -9), 160 * math.pow(10, -9), 2 * math.pow(10, -11))
        # t = numpy.arange(50 * math.pow(10, -9), 100 * math.pow(10, -9), 2 * math.pow(10, -11))
        for i in range(0, len(freqs)):
            this_cosine = numpy.real(samples[i]) * numpy.cos(2 * numpy.pi * freqs[i] * t + cmath.phase(samples[i]))
            output.append(this_cosine)
        net_cosine = numpy.abs(numpy.sum(output, axis=0))
        return t, net_cosine

    def meetsThreshold(self, wave):
        if max(wave) > 0.065:
            return True
        else:
            return False

    '''WIP/candidate for position calc/plot'''
    def getPosition(self, wave1, wave2, wave3, range1, range2, range3):
        #wave1, range1: left horn amp, peak time
        #wave2, range2: right horn amp, peak time
        #wave3, range3: cone amp, peak time
        #___________________________________________Everything is in meters_____________________________________________
        result = ''
        M2FT = 3.28084
        light = 299792458  # lightspeed constant
        #position of each antenna(guess for now, adjust to test setup)
        posLeft = -1
        posRight = 1
        yLeft = []
        yRight = []
        #print('location2')
        # If true, uses cone for range, pt comparison for angle
        if self.meetsThreshold(wave1) and self.meetsThreshold(wave2) and self.meetsThreshold(wave3):
            # Treat the time location of each max as radii of semicircles. Draw the semicircles and split to be in location of both receivers.
            # Plot these.
            # first find the range using the time bump on the center antenna (times3)
            self.range_calc = (light * range3) / 4 - 2.97
            # find the range from each side receiver
            range1_calc = light * range1 - self.range_calc - 16.5
            range2_calc = light * range2 - self.range_calc - 16.2
            # calculate maximum/minimum x distance for each antenna
            minLeft = posLeft - range1_calc
            maxLeft = posLeft + range1_calc
            minRight = posRight - range2_calc
            maxRight = posRight + range2_calc
            # Form some arrays of values to plot a semicircle. This is mostly for graphing visuals.
            # y = sqrt((x-a)^2 - r^2), where a is the distance from transmitter of the receiver.
            xRangeLeft = numpy.linspace(minLeft, maxLeft, 200)  # always do 100 points. Can adjust to make the plot look nicer.
            xRangeRight = numpy.linspace(minRight, maxRight, 200)
            x2 = 0
            y2 = 0
            h = a = d = 0
            for i in range(len(xRangeLeft)):  # form left function
                thisY = math.sqrt(abs((xRangeLeft[i] - posLeft) ** 2 - range1_calc ** 2))
                yLeft.append(thisY)

            for i in range(len(xRangeRight)):  # form right function
                thisY = math.sqrt(abs((xRangeRight[i] - posRight) ** 2 - range2_calc ** 2))
                yRight.append(thisY)

            # calculate intersection of the created curves. Use the circle equation generated from each position/radius and take the
            # intersection which is not in quadrants 3 or 4.
            if (maxLeft == maxRight):  # coincident circles
                result += "\nAntennas too close together!"
            if (maxLeft < minRight):  # non intersecting
                print('maxLeft/right condition')
                result += "\nNo target detected!"
            else:  # calculate intersection points. Starting y vals are 0, and remember that range1_calc/range2_calc are the radii of each circle.
                result += "\nRANGE: " + str(self.range_calc) + " meters (m)"  # always output range
                # Change to point comparison for angle
                x_tar, y_tar = self.findIntersection(xRangeLeft, yLeft, xRangeRight, yRight)
                self.az_calc = (numpy.pi/2 - numpy.arctan(y_tar/x_tar)) * 180/numpy.pi
                result += ' Azimuth: ' + str(self.az_calc) + ' degrees'
                ''' Algebraic solution
                if range1_calc > range2_calc:
                    d = range1_calc - range2_calc
                    a = (range1_calc ** 2 - range2_calc ** 2 + d ** 2) / (2 * d)
                    h = math.sqrt(abs(range1_calc ** 2 - a ** 2))
                    x2 = range1_calc + a * (range2_calc - range1_calc) / d  # only need 1 x calculation (yay)
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
                else:  # if equal, we're on boresight.
                    x2 = 1
                    y2 = 0
                    self.az_calc = 0
                    result += "AZIMUTH: 0 degrees, ON BORESIGHT."
                '''
            # plot left
            # _____________Plotting stuff_____________________________________
            self.ax1.cla()
            self.ax1.plot(xRangeLeft, yLeft, c='r')
            # why is the label for both x and y the same???
            self.ax1.set_xlabel('Position, m')
            self.ax1.set_ylabel('Position, m')
            # draw position of receiver
            self.ax1.scatter(posLeft, 0, s=50, c='r')
            # plot right
            self.ax1.plot(xRangeRight, yRight, c='b')
            self.ax1.set_xlabel('Position, m')
            self.ax1.set_ylabel('Position, m')
            # draw receiver
            self.ax1.scatter(posRight, 0, s=50, c='b')
            # Draw transmitter
            self.ax1.scatter(0, 0, s=50, c='m')
            # Draw point for intersection
            self.ax1.scatter(x2, y2, s=50, c='m')
            # plot a line between transmit and intersect
            self.ax1.plot([0, x2], [0, y2], c='m')
            self.ax1.set_ylim([0, 10])
            self.ax1.set_xlim([-10, 10])
            self.ax1.set_title('Intersection Plot (Cone Mode)')
        # If true, means out of cone for range, uses bistatic method to calc range + angle
        elif self.meetsThreshold(wave1) and self.meetsThreshold(wave2) and not self.meetsThreshold(wave3):
            # May need to tune this number
            range_adj = 20
            range1_calc = (light * range1) - range_adj
            range2_calc = (light * range2) - range_adj
            xLeft, yLeft = vnaStuff.generateEllipse(range1_calc, abs(posLeft))
            xLeft = xLeft + posLeft/2
            xRight, yRight = vnaStuff.generateEllipse(range2_calc, posRight)
            xRight = xRight + posRight/2
            x_tar, y_tar = self.findIntersection(xLeft, yLeft, xRight, yRight)
            if y_tar is not -1:
                self.range_calc = numpy.sqrt(x_tar**2 + y_tar**2)
                self.az_calc = (numpy.pi/2 - numpy.arctan(y_tar/x_tar)) * 180/numpy.pi
                result = 'Range: {} feet\nAzimuth: {}'.format(self.range_calc*M2FT, self.az_calc)
                # _________________________________________Plot stuff___________________________________________________
                self.ax1.cla()
                self.ax1.plot(xLeft, yLeft, c='r')
                self.ax1.plot(xRight, yRight, c='b')
                self.ax1.scatter(posLeft, 0, c='r')
                self.ax1.scatter(posRight, 0, c='b')
                self.ax1.scatter(0, 0, c='m')
                self.ax1.set_ylim([0, 10])
                self.ax1.set_xlim([-10, 10])
                self.ax1.set_title('Intersection Plot (Bistatic Mode)')
            else:
                result = 'No intersection :('
        # If true, Extreme right angle, as left horn can see but right cannot
        elif self.meetsThreshold(wave1) and not self.meetsThreshold(wave2):
            result = 'Extreme angle right of boresight!'
        elif self.meetsThreshold(wave2) and not self.meetsThreshold(wave1):
            result = 'Extreme angle left of boresight!'
        else:
            result += '\nNo target detected! (weak return)'
        # __________________________plot position______________________________
        self.plotPosition(self.az_calc, self.range_calc*M2FT)
        # pull launcher trigger if in boresight
        # if(pullTrigger()):
        #    releaseTrigger()
        return result

    def plotPosition(self, currentTheta=0, currentR=0):
        '''
        # initialize theta and R
        # currentTheta = 0
        # currentR = 0
        # set up polar plt
        #axPos = plt.subplot(211, projection="polar")
        # axPos.set_ylim([0,30])
        # enable interactive mode so the plot doesn't close and open and is non-blocking
        #plt.ion()
        #plt.show()
        # just for demonstration
        countingUp = True
        # while(1):
        # ***demo stuff***
        # currentTheta = random.randrange(0,359)
        # currentTheta += 5
        # currentR = random.randrange(0,10)
        '''
        '''
        if (currentR == 30):
            countingUp = False
        elif (currentR == 0):
            countingUp = True
        if (countingUp):
            currentR += 0.75
        else:
            currentR -= 0.75
        '''
        # ***demo stuff end***
        # set theta and r
        offest_theta = 9
        rotation = 90
        theta = [0, math.radians(currentTheta+rotation-offest_theta)]
        thetaLeft = [0, math.radians(currentTheta-5+rotation-offest_theta)]
        thetaRight = [0, math.radians(currentTheta+5+rotation-offest_theta)]
        r = [0, currentR]
        # clear plot and prep for redraw
        self.axPolar.cla()
        self.axPolar.set_title('Object Position')
        # set limit on polar plot range
        self.axPolar.set_ylim([0, 8])
        # tell the user what the range is at the moment in the bottom left corner
        self.axPolar.annotate('Range: {:0.2f}'.format(currentR) + " Feet\nAngle: {:0.2f}".format(currentTheta) + ' degrees',
                       xy=(currentTheta, currentR),  # theta, radius
                       xytext=(0.05, 0.05),  # fraction, fraction
                       textcoords='figure fraction',
                       #        arrowprops=dict(facecolor='black', shrink=0.05),
                       horizontalalignment='left',
                       verticalalignment='bottom',
                       )
        # plot first a red diamond and then a red line, both for position
        self.axPolar.plot(theta, r, '^r')
        self.axPolar.plot(theta, r, '-r')
        #self.axPolar.plot(thetaLeft, r, '^b')
        self.axPolar.plot(thetaLeft, r, '-b')
        #self.axPolar.plot(thetaRight, r, '^g')
        self.axPolar.plot(thetaRight, r, '-g')
        # give the plot a moment to breathe and do its processing
        #plt.pause(0.05)


    def plotTimeDomain(self, times, leftHornWave, rightHornWave, coneWave):
        # Assumes that same time range was used for all, may need to give different intervals for cone vs horns
        for axis in self.axTime:
            axis.cla()
        self.axTime[0].set_title('Left Horn Signal')
        self.axTime[1].set_title('Right Horn Signal')
        self.axTime[2].set_title('Cone Signal')
        self.axTime[0].plot(times, leftHornWave)
        self.axTime[1].plot(times, rightHornWave)
        self.axTime[2].plot(times, coneWave)
        self.axTime[2].set_xlabel('time, seconds')

    def pullTrigger(self):
        triggerPulled = False
        if ((self.az_calc > self.left_theta_boundary) and (self.az_calc < self.right_theta_boundary)):
            board = Arduino("COM3")
            # full revolution is 200 steps
            stepsPerRev = 200
            desiredSteps = int(stepsPerRev / 4)
            # pin numbers to write
            pins = [8, 9, 10, 11]
            i = 0
            while i < len(pins):
                board.digital[i].write(0)
            # take 50 steps
            for x in range(desiredSteps):
                board.digital[pins[0]].write(1)
            time.sleep(0.005)
            board.digital[pins[0]].write(0)
            time.sleep(0.005)
            triggerPulled = True
        return triggerPulled

    def releaseTrigger(self):
        board = Arduino("COM3")
        # full revolution is 200 steps
        stepsPerRev = 200
        desiredSteps = int(stepsPerRev / 4)
        # pin numbers to write
        pins = [8, 9, 10, 11]
        i = 0
        while i < len(pins):
            board.digital[i].write(0)
        # take 50 steps
        for x in range(desiredSteps):
            board.digital[pins[2]].write(1)
        time.sleep(0.005)
        board.digital[pins[2]].write(0)
        time.sleep(0.005)


""""--------------------------------------------------------------------------------------------------------------------
main
---------------------------------------------------------------------------------------------------------------------"""
if __name__ == '__main__':
    vnakit.Init()
    vnas = vnaStuff()
    '''
    settings in freq range (mhz),
    rbw (khz),
    power level (dbm),
    tx port,
    port setup to record
    '''
    settings = vnakit.RecordingSettings(
        vnakit.FrequencyRange(2500, 3000, 100),
        1,
        0,
        3,
        vnakit.VNAKIT_MODE_TWO_PORTS
    )
    vnakit.ApplySettings(settings)
    # may need to move where this plot displays to avoid collision with the radar position plot
    plt.pause(0.001)
    fig1 = plt.figure()
    fig2 = plt.figure()
    fig3 = plt.figure()
    vnas.ax1 = fig1.add_subplot(1, 1, 1)
    vnas.axPolar = fig2.add_subplot(1, 1, 1, projection="polar")
    vnas.axTime.append(fig3.add_subplot(3, 1, 1))
    vnas.axTime.append(fig3.add_subplot(3, 1, 2))
    vnas.axTime.append(fig3.add_subplot(3, 1, 3))
    # does this work? Yes
    backg, backg2, backg3 = vnas.calcBackground()
    # animatetime calls getposition and plotposition
    junk = 1
    #print('location1')
    plt.ion()
    plt.show()
    while(1):
        vnas.animateTime(backg, backg2, backg3)
        plt.pause(0.01)
