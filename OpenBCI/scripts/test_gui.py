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
mutex = Lock()

#Helmetsetup
port = 'COM6'
baud = 115200
logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
logging.info('---------LOG START-------------')
board = bci.OpenBCIBoard(port=port, scaled_output=True, log=True, filter_data = False)
print("Board Instantiated")
board.ser.write('v')
tme.sleep(10)

if not board.streaming:
	board.ser.write(b'b')
	board.streaming = True

print("Samplerate: %0.2fHz" %board.getSampleRate())

#Graph setup
app = QtGui.QApplication([])
p = pg.plot()
nPlots = 8
nSamples = 500
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
p.resize(1000,1000)

#rgn = pg.LinearRegionItem([nSamples/5.,nSamples/3.])
#p.addItem(rgn)

#sample = board._read_serial_binary()
#data = sample.channel_data





print("Graphsetup finished")


#Filtersetup
window = 125
fs = 250.0
f0 = 50.0
Q = 30
w0 = f0/(fs/2)
b, a = signal.iirnotch(w0, Q) 
filtering = True
bandstopFilter = True
lowpassFilter = True
#print("B: ", b)
#print("A: ", a)
sample = board._read_serial_binary()
zi = np.array([[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]])
#zi = np.array([[0],[0],[0],[0],[0],[0],[0],[0]])
init = True

# First, design the Buterworth filter
N  = 5    # Filter order
fk = 20
Wn = fk/(fs/2) # Cutoff frequency
B, A = signal.butter(N, Wn, output='ba')
ZI = np.array([[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]])

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
			#print("Kanal: ", i)
			#print("Offset: ", (average * 0.02235))
			#print("Rawdata: ", sample.channel_data[i] * 0.02235)
			#print("Data: ", (sample.channel_data[i]-average) * 0.02235)
			#print("Length of array: ", len(rawdata[0]))
			if filtering:
				averagedata[i].append(sample.channel_data[i]-average)
				#print(averagedata[i])

			else:
				data[i].append((sample.channel_data[i]-average) * df)
				
			#displayUV[i] = (sample.channel_data[i]-average) * 0.02235

		if len(data[0]) >= 2000:
			for i in range(nPlots):
				data[i].pop(0)
				
				
		if len(rawdata[0]) > 500:
			for i in range(nPlots):
				rawdata[i].pop(0)

		if len(averagedata[0]) >= window:
					
			threadFilter = threading.Thread(target=notchFilter,args=())
			threadFilter.start()



def notchFilter():
	global b, a, zi, averagedata, data, window, init, bandstopFilter, lowpassFilter, B, A, ZI
	with(mutex):
		for i in range(nPlots):
			if init == True: #Gjor dette til en funksjon, input koeff, return zi
				zi[i] = signal.lfilter_zi(b, a) * averagedata[i][0]
				ZI[i] = signal.lfilter_zi(B, A) * averagedata[i][0]
				init = False

		if bandstopFilter and not lowpassFilter:
			for i in range(nPlots):
				y, zi[i] = signal.lfilter(b, a, averagedata[i], zi=zi[i])
				#print(bp)
				for j in range(len(y)):
					data[i].append(y[j]*df)

		elif lowpassFilter and not bandstopFilter:
			for i in range(nPlots):
				y, ZI[i] = signal.lfilter(B, A, averagedata[i], zi=ZI[i])
				#print(lp)
				for j in range(len(y)):
					data[i].append(y[j]*df)

		elif lowpassFilter and bandstopFilter:
			for i in range(nPlots):
				x, zi[i] = signal.lfilter(b, a, averagedata[i], zi=zi[i])
				y, ZI[i] = signal.lfilter(B, A, x, zi=ZI[i])
				for j in range(len(y)):
					data[i].append(y[j]*df)
				#print(bp and lp)
		else:
			for i in range(nPlots):
				y = averagedata[i]

		#for i in range(nPlots):
			#for j in range(len(y)):
				#data[i].append(y[j]*df)
			#print("Start data")
			#print(y)
		averagedata = [],[],[],[],[],[],[],[]



def update():
	global curve, data, ptr, p, lastTime, fps, nPlots, count, board
	count += 1
	string = ""
	with(mutex):
		for i in range(nPlots):
		#curves[i].setData(data[(ptr+i)%data.shape[0]])
			curves[i].setData(data[i])
			if len(data[i])>100:
				string += '   Ch: %d ' % i
				string += ' = %0.2f uV ' % data[i][-1]
			
			#curves[i].setData(averagedata[i])
		#print(data[i][count-1])
    #print "   setData done."
	ptr += nPlots
	now = time()
	dt = now - lastTime	
	lastTime = now
	if fps is None:
		fps = 1.0/dt
	else:
		s = np.clip(dt*3., 0, 1)
		fps = fps * (1-s) + (1.0/dt) * s
	#p.setTitle('%0.2f fps' % fps)
	p.setTitle(string)
    #app.processEvents()  ## force complete redraw for every plot

def keys():
	#global thread1, thread2
	global board, bandstopFilter, filtering, lowpassFilter
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

		elif string == "exit":
			print("Initiating exit sequence")
			#thread1.stop()
			#thread2.stop()
			board.stop()
			board.disconnect()
			QtGui.QApplication.quit()
			sys.exit()



def main():

	#mw = QtGui.QMainWindow()
	#mw.resize(800,800)
	
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
	#import sys
	#if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		#QtGui.QApplication.instance().exec_()