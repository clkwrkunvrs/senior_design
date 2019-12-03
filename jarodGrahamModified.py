import vnakit
# import time
# import vnakit_ex.hidden
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy
import cmath
import math
'''
Calcs the average background freq domain response
'''
def calcBackground():
    N = 10
    bg = list()
    bg2 = list()
    bg3 = list()
    bg_final = list()
    bg_final2 = list()
    bg_final3 = list()
    # Warm up
    for w_up in range(0, 2*N):
        vnakit.Record()
        junk = vnakit.GetRecordingResult()
    # Avg background noise
    for bgIndex in range(0, N):
        vnakit.Record()
        results = vnakit.GetRecordingResult()
        oneTrial = list()
        oneTrial2 = list()
        oneTrial3 = list()
        for sample_p4, sample_p2, sample_p5, sample_p6 in zip(results[4], results[2], results[5], results[6]):
            oneTrial2.append(sample_p5/sample_p2)
            oneTrial.append(sample_p4/sample_p2)
            oneTrial3.append(sample_p6/sample_p2)
        bg.insert(bgIndex, oneTrial)
        bg2.insert(bgIndex, oneTrial2)
        bg3.insert(bgIndex, oneTrial3)
    for i in range(0, len(bg[0])):
        freq_sum = 0
        freq_sum2 = 0
        freq_sum3 = 0
        for j in range(0, N):
            freq_sum2 = freq_sum2 + bg2[j][i]
            freq_sum = freq_sum + bg[j][i]
            freq_sum3 = freq_sum3 + bg3[j][i]
        bg_final2.append(freq_sum2 / N)
        bg_final.append(freq_sum / N)
        bg_final3.append(freq_sum3 / N)

    return bg_final, bg_final2, bg_final3

def animateTime(i, bg1, bg2, bg3):
    raw1 = []
    raw2 = []
    raw3 = []
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
    freqs = vnakit.GetFreqVector_MHz()
    freqs2 = vnakit.GetFreqVector_MHz()
    freqs3 = vnakit.GetFreqVector_MHz()
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
    output = list()
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
    #position of each antenna (guess for now, adjust to test setup)
    posLeft = -1
    posRight = 1
    yLeft = list()
    yRight = list()
    #to be determined
    # based upon horizontal plate results
    #scale = -0.1545 * math.pow(range, 2) + 2.0027*range - 3.47
    #diff_bound = 2
    #slope = 0.1
    if meetsThreshold(wave1) and meetsThreshold(wave2) and meetsThreshold(wave3):
        #Treat the time location of each max as radii of semicircles. Draw the semicircles and split to be in location of both receivers.
        #Plot these.
        #first find the range using the time bump on the center antenna (times3)
        range_calc = (light*range3)/4 - 2.97
        #find the range from each side receiver
        range1_calc = light*range1 - range_calc - 3.15
        range2_calc = light*range2 - range_calc - 3.15
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
            result += "\nRANGE: " + str(range_calc) + " meters (m)" #always output range
            if range1_calc > range2_calc:
                d = range1_calc - range2_calc
                a = (range1_calc**2 - range2_calc**2 + d**2) / (2*d)
                h = math.sqrt(abs(range1_calc**2 - a**2))
                x2 = range1_calc + a*(range2_calc - range1_calc)/d #only need 1 x calculation (yay)
                y2 = -1 * h * (range2_calc - range1_calc) / d
                if y2 < 0:  # if y2 < 0, we calculated the intersection in Q3/Q4 (behind the radar), so find the other and we're done.
                    y2 = h * (range2_calc - range1_calc) / d
                az_calc = math.degrees(math.atan(y2 / x2))  # trig to find the azimuth
                result += "AZIMUTH: " + str(az_calc) + " degrees (deg) LEFT of boresight."
            elif range2_calc > range1_calc:
                d = range2_calc - range1_calc
                a = (range2_calc ** 2 - range1_calc ** 2 + d ** 2) / (2 * d)
                h = math.sqrt(abs(range2_calc ** 2 - a ** 2))
                x2 = range2_calc + a * (range1_calc - range2_calc) / d  # only need 1 x calculation (yay)
                y2 = -1 * h * (range1_calc - range2_calc) / d
                if y2 < 0:  # if y2 < 0, we calculated the intersection in Q3/Q4 (behind the radar), so find the other and we're done.
                    y2 = h * (range2_calc - range1_calc) / d
                az_calc = math.degrees(math.atan(y2 / x2))  # trig to find the azimuth
                result += "AZIMUTH: " + str(az_calc) + " degrees (deg) RIGHT of boresight."
            else: #if equal, we're on boresight.
                x2 = 1
                y2 = 0
                az_calc = 0
                result += "AZIMUTH: 0 degrees, ON BORESIGHT."
        #plot left
        ax1.clear()
        ax1.plot(xRangeLeft, yLeft, c='r')
        ax1.set_xlabel('Position, m')
        ax1.set_ylabel('Position, m')
        #draw position of receiver
        ax1.scatter(posLeft, 0, s=50, c='r')
        #plot right
        ax1.plot(xRangeRight, yRight, c='b')
        ax1.set_xlabel('Position, m')
        ax1.set_ylabel('Position, m')
        #draw receiver
        ax1.scatter(posRight, 0, s=50, c='b')
        #Draw transmitter
        ax1.scatter(0,0, s=50, c='m')
        #Draw point for intersection
        ax1.scatter(x2, y2, s=50, c='m')
        #plot a line between transmit and intersect
        ax1.plot([0, x2], [0, y2], c='m')
    else:
        result += '\nNo target detected!'
    return result
""""--------------------------------------------------------------------------------------------------------------------
Main
---------------------------------------------------------------------------------------------------------------------"""
vnakit.Init()
'''
Settings in freq range (MHz),
RBW (kHz),
power level (dBm),
Tx port,
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
fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1)
junk = 1
backg, backg2, backg3 = calcBackground()
an = ani.FuncAnimation(fig1, animateTime, fargs=(backg, backg2, backg3), interval=50)
plt.show()
