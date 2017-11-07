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
from numpy.random import randint
import Tkinter as tk
import testtkinter as ttk
from globalvar import *
#z = randn(2000)
#legends = []
#for i in range(2):
	#label = "Fp %d" %(i+1)
	#print(label)
	#label = tuple([label])
	#legend, = plt.plot(z, label=label)
	#legends.append(legend)
#plt.ylabel('uV')
#plt.xlabel('Sample')
#plt.legend(handles=legends)
#legends = []
#plt.show()

mutex = Lock()
board = None
root = None
graphVar = False
nPlots = 8

count = None
#Filtersetup
#Notchfilter
window = 151
curves = []
ptr = 0
#data = [],[],[],[],[],[],[],[]

rawdata = [],[],[],[],[],[],[],[]
averagedata = [],[],[],[],[],[],[],[]
p = None

init = True
exit = False
filtering = True
bandstopFilter = False
lowpassFilter = False
bandpassFilter = True
app = QtGui.QApplication([])
fs = 250.0
f0 = 50.0
Q = 50
w0 = f0/(fs/2)
notchB, notchA = signal.iirnotch(w0, Q) 

#sample = board._read_serial_binary()
notchZi = np.zeros([8,2])
print(notchB)
print(notchA)
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
#print(bandpassB)
highpassB = signal.firwin(window, lc, pass_zero=False, window = 'hann') #Bandpass
print("Filtersetup finished")

np.savetxt('bandpasscoeff.out', bandpassB)
np.savetxt('highpasscoeff.out', highpassB)

print("Saved coeff")

#GUI parameters
#size = 1000
#speed = 20
#ballsize = 30



def dataCatcher():
	global board
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
			threadFilter = threading.Thread(target=filter,args=())
			threadFilter.setDaemon(True)
			threadFilter.start()

def appendData(y, i):
	for j in range(len(y)):
		data[i].append(y[j])

def filter():
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
			init = False

			#TODO: init filters again when turned on
		for i in range(nPlots):
			x = averagedata[i]

			if bandstopFilter:
				x, notchZi[i] = signal.lfilter(notchB, notchA, x, zi=notchZi[i])

			if lowpassFilter:
				x, lowpassZi[i] = signal.lfilter(lowpassB, lowpassA, x, zi=lowpassZi[i])
			
			if bandpassFilter:
				x, bandpassZi[i] = signal.lfilter(bandpassB, bandpassA, x, zi=bandpassZi[i])


			appendData(x,i)


		averagedata = [],[],[],[],[],[],[],[]
		
def plot():
	with(mutex):
		while len(data[0]) > nSamples:
			for i in range(nPlots):
				data[i].pop(0)
		x = np.arange(0, len(data[1])/fs, 1/fs)
		legends = []
		for i in range(2):
			label = "Fp %d" %(i+1)
			#print(label)
			#label = tuple([label])
			legend, = plt.plot(x, data[i], label=label)
			legends.append(legend)
	plt.ylabel('uV')
	plt.xlabel('Seconds')
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
	global curves, data, ptr, p, lastTime, fps, nPlots, count, board
	count += 1
	string = ""
	with(mutex):
		for i in range(nPlots):
			curves[i].setData(data[i])
			if len(data[i])>100:
				string += '   Ch: %d ' % i
				string += ' = %0.2f uV ' % data[i][-1]

	ptr += nPlots
	#now = time()
	#dt = now - lastTime	
	#lastTime = now

	p.setTitle(string)
    #app.processEvents()  ## force complete redraw for every plot

def graph():
	#Graph setup
	global nPlots, nSamples, count, data, curves, p, QtGui, app
	#app = QtGui.QApplication([])
	p = pg.plot()

	p.setWindowTitle('pyqtgraph example: MultiPlotSpeedTest')
	#p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
	p.setLabel('bottom', 'Index', units='B')
	#curves = [p.plot(pen=(i,nPlots*1.3)) for i in range(nPlots)]

	
	
	lastTime = time()
	fps = None
	count = 0

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

	mw = QtGui.QMainWindow()
	mw.resize(800,800)
	
	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(0)

	print("Graphsetup finished")
	
	QtGui.QApplication.instance().exec_()


def keys():

	global board, bandstopFilter, filtering, lowpassFilter, bandpassFilter, graphVar
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
			exit = True
			if root != None:
				root.destroy()
			#print("Quit gui")
			if QtGui != None:
				QtGui.QApplication.quit()
			#print("Quit Graph")
			if board != None:
				print("Closing board")
				board.stop()
				board.disconnect()
			#print("Quit board")
			os._exit(0)
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
		elif string == "save":
			save()
		#elif string == "start":
			#threadDataCatcher = threading.Thread(target=dataCatcher,args=())
			#threadDataCatcher.setDaemon(True)
			#threadDataCatcher.start()
		elif string == "graph":
			graphVar = True

		elif string == "gui":
			threadGui = threading.Thread(target=gui, args=())
			threadGui.setDaemon(True)
			threadGui.start()
		elif string == "printdata":
			ttk.openFile()

def save():
	np.savetxt('data.out', data[1])

def gui():
	ttk.guiloop()



def main():
	global graphVar, exit

	print("Setup finished, starting threads")

	threadKeys = threading.Thread(target=keys,args=())
	threadKeys.setDaemon(True)
	threadKeys.start()
	threadDataCatcher = threading.Thread(target=dataCatcher,args=())
	threadDataCatcher.setDaemon(True)
	threadDataCatcher.start()
	#threadGui = threading.Thread(target=gui, args=())
	#threadGui.setDaemon(True)
	#threadGui.start()
	
	#thread2 = threading.Thread(target=QtGui.QApplication.instance().exec_(),args=())

	#thread2.start()
	
	#thread0.join()
	#thread1.join()
	#thread2.join()

	while not graphVar:
		pass

	if not exit:
		graph()	

	


if __name__ == '__main__':
	main()
