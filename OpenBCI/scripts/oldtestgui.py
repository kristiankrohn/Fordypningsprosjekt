import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import os
import logging
import time as tme
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
import threading
from threading import Lock
from scipy import signal
import matplotlib.pyplot as plt
from numpy.random import randn


mutex = Lock()

#Helmetsetup
port = 'COM6'
baud = 115200
logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
logging.info('---------LOG START-------------')
board = bci.OpenBCIBoard(port=port, scaled_output=True, log=True, filter_data = False)
print("Board Instantiated")
board.ser.write('v')
#tme.sleep(10)

if not board.streaming:
	board.ser.write(b'b')
	board.streaming = True

print("Samplerate: %0.2fHz" %board.getSampleRate())

#Graph setup
app = QtGui.QApplication([])
p = pg.plot()
nPlots = 6
nSamples = 1800
p.setWindowTitle('pyqtgraph example: MultiPlotSpeedTest')
#p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
p.setLabel('bottom', 'Index', units='B')
#curves = [p.plot(pen=(i,nPlots*1.3)) for i in range(nPlots)]

curves = []
ptr = 0
lastTime = time()
fps = None
count = 0
data = [],[],[],[],[],[],[],[]
rawdata = [],[],[],[],[],[],[],[]
averagedata = [],[],[],[],[],[],[],[]
displayUV = []
df = 1

for i in range(nPlots):
	c = pg.PlotCurveItem(pen=(i,nPlots*1.3))
	p.addItem(c)
	c.setPos(0,i*100+200)
	curves.append(c)

#p.setYRange(0, nPlots*6)
p.setYRange(0, nPlots*100)
p.setXRange(0, nSamples)
p.resize(nSamples,1000)



print("Graphsetup finished")


#Filtersetup
#Notchfilter
window = 151

fs = 250.0
f0 = 50.0
Q = 50
w0 = f0/(fs/2)
notchB, notchA = signal.iirnotch(w0, Q) 


filtering = True
bandstopFilter = False
lowpassFilter = False
bandpassFilter = True


sample = board._read_serial_binary()
notchZi = np.zeros([8,2])
init = True

#Butterworth lowpass filter
N  = 4    # Filter order
fk = 30
Wn = fk/(fs/2) # Cutoff frequency
lowpassB, lowpassA = signal.butter(N, Wn, output='ba')
lowpassZi = np.zeros([8,N])


#FIR bandpass filter
hc = 45.0/(fs/2) #High cut
lc = 5.0/(fs/2)	#Low cut

bandpassB = signal.firwin(window, [lc, hc], pass_zero=False, window = 'hann') #Bandpass
bandpassA = 1.0 #np.ones(len(bandpassA))
bandpassZi = np.zeros([8, window-1])

highpassB = signal.firwin(window, lc, pass_zero=False, window = 'hann') #Bandpass
highpassA = 1.0
highpassZi = np.zeros([8, window-1])
print("Filtersetup finished")


def dataCatcher():
	global board
	board.start_streaming(printData)


def printData(sample):	
	global nPlots, data, df, init, averagedata, rawdata, threadFilter 

	with(mutex):

		for i in range(nPlots):
			avg = 0
			rawdata[i].append(sample.channel_data[i])

			for j in range(len(rawdata[0])-1):
				avg = avg + rawdata[i][j]

			average = avg / (len(rawdata[0]))

			if filtering:
				averagedata[i].append(sample.channel_data[i]-average)
				#averagedata[i].append(sample.channel_data[i])
			else:
				data[i].append(sample.channel_data[i])
				
		if len(data[0]) >= nSamples:
			for i in range(nPlots):
				data[i].pop(0)
				
				
		if len(rawdata[0]) > 1000:
			for i in range(nPlots):
				rawdata[i].pop(0)

		if len(averagedata[0]) >= window:					
			threadFilter = threading.Thread(target=notchFilter,args=())
			threadFilter.start()

def appendData(y, i):
	for j in range(len(y)):
		data[i].append(y[j]*df)

def notchFilter():
	global highpassB, highpassA, highpassZi
	global lowpassB, lowpassA, lowpassZi 
	global bandpassB, bandpassA, bandpassZi
	global notchB, notchA, notchZi 
	global averagedata, data, window, init, initNotch, initLowpass, initBandpass
	global bandstopFilter, lowpassFilter, bandpassFilter
	
	with(mutex):
		
		if init == True: #Gjor dette til en funksjon, input koeff, return zi
			for i in range(nPlots):
				notchZi[i] = signal.lfilter_zi(notchB, notchA) * averagedata[i][0]
				lowpassZi[i] = signal.lfilter_zi(lowpassB, lowpassA) * averagedata[i][0]
				bandpassZi[i] = signal.lfilter_zi(bandpassB, bandpassA) * averagedata[i][0]
				highpassZi[i] = signal.lfilter_zi(highpassB, highpassA) * averagedata[i][0]
			init = False

			#TODO: init filters again when turned on
		for i in range(2):
			x = averagedata[i]
			x, bandpassZi[i] = signal.lfilter(bandpassB, bandpassA, x, zi=bandpassZi[i])	
			appendData(x,i)
		
		for i in range(2):
			x = averagedata[i+2]
			x, notchZi[i] = signal.lfilter(notchB, notchA, x, zi=notchZi[i])
			x, highpassZi[i] = signal.lfilter(highpassB, highpassA, x, zi=highpassZi[i])
			appendData(x,i+2)
		for i in range (2):
			x = averagedata[i+4]
			x, notchZi[i+2] = signal.lfilter(notchB, notchA, x, zi=notchZi[i+2])
			appendData(x,i+4)
		averagedata = [],[],[],[],[],[],[],[]

def plot():
	legends = []
	plt.figure(1)
	for i in range(2):
		label = "BP Fp %d" %(i+1)
		#print(label)
		#label = tuple([label])
		plt.subplot(311)
		legend, = plt.plot(data[i], label=label)
		legends.append(legend)

	for i in range(2):
		label = "Notch + HP Fp %d" %(i+1)
		#print(label)
		#label = tuple([label])
		plt.subplot(312)
		legend, = plt.plot(data[i+2], label=label)
		legends.append(legend)

	for i in range(2):
		label = "Notch Fp %d" %(i+1)
		#print(label)
		#label = tuple([label])
		plt.subplot(313)
		legend, = plt.plot(data[i+4], label=label)
		legends.append(legend)

	plt.ylabel('uV')
	plt.xlabel('Sample')
	#TODO: x axis in seconds
	plt.legend(handles=legends)
	legends = []
	plt.show()

def plotAll():
	legends = []
	for i in range(nPlots):
		label = "Channel %d" %(i+1)
		#print(label)
		#label = tuple([label])
		legend, = plt.plot(data[i], label=label)
		legends.append(legend)
	plt.ylabel('uV')
	plt.xlabel('Sample')
	plt.legend(handles=legends)
	legends = []
	plt.show()

def update():
	global curve, data, ptr, p, lastTime, fps, nPlots, count, board
	count += 1
	string = ""
	with(mutex):
		for i in range(nPlots):
			curves[i].setData(data[i])
			if len(data[i])>100:
				string += '   Ch: %d ' % i
				string += ' = %0.2f uV ' % data[i][-1]

	ptr += nPlots
	now = time()
	dt = now - lastTime	
	lastTime = now

	p.setTitle(string)
    #app.processEvents()  ## force complete redraw for every plot

def keys():

	global board, bandstopFilter, filtering, lowpassFilter, bandpassFilter
	while True:
		string = raw_input()
		if string == "notch=true":
			bandstopFilter = True
		elif string == "notch=false":
			bandstopFilter = False
		elif string == "filter=true":
			filtering = True
			print(filtering)
		elif string == "filter=false":
			filtering = False
			print(filtering)
		elif string == "lowpass=true":
			lowpassFilter = True
		elif string == "lowpass=false":
			lowpassFilter = False
		elif string == "bandpass=true":
			bandpassFilter = True
		elif string == "bandpass=false":
			bandpassFilter = False
		elif string == "exit":
			print("Initiating exit sequence")
			board.stop()
			board.disconnect()
			QtGui.QApplication.quit()
			sys.exit()
		elif string == "plot":
			plot()
			#plotThread = threading.Thread(target=plot,args=())
			#plotThread.start()
			#plotthread.join()
		elif string == "plotall":
			plotAll()
			#plotAllThread = threading.Thread(target=plotAll,args=())
			#plotAllThread.start()
			#plotAllThread.join()

def main():

	mw = QtGui.QMainWindow()
	mw.resize(800,800)
	
	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(0)

	print("Setup finished, starting threads")

	thread0 = threading.Thread(target=keys,args=())
	thread1 = threading.Thread(target=dataCatcher,args=())
	thread0.start()
	thread1.start()	
	
	#thread2 = threading.Thread(target=QtGui.QApplication.instance().exec_(),args=())

	#thread2.start()
	
	#thread0.join()
	#thread1.join()
	#thread2.join()
	
	QtGui.QApplication.instance().exec_()

	


if __name__ == '__main__':
	main()