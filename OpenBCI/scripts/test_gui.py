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
board = bci.OpenBCIBoard(port=port, scaled_output=False, log=True, filter_data = False)
print("Board Instantiated")
board.ser.write('v')
tme.sleep(10)
if not board.streaming:
	board.ser.write(b'b')
	board.streaming = True



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
df = 0.01

for i in range(nPlots):
	c = pg.PlotCurveItem(pen=(i,nPlots*1.3))
	p.addItem(c)
	c.setPos(0,i*100+100)
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
bandstopFilter = True
#print("B: ", b)
#print("A: ", a)
sample = board._read_serial_binary()
zi = np.array([[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]])
#zi = np.array([[0],[0],[0],[0],[0],[0],[0],[0]])
init = True


print("Filtersetup finished")

def convtouV(input):
	return (input * 0.02235)

def dataCatcher():
	global board
	board.start_streaming(printData)


def printData(sample):	

	global nPlots, data, df, init, averagedata, rawdata 


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
			if bandstopFilter:
				averagedata[i].append(sample.channel_data[i]-average)
				#print(averagedata[i])
			else:
				data[i].append((sample.channel_data[i]-average) * df)
			#displayUV[i] = (sample.channel_data[i]-average) * 0.02235

		if len(data[0]) >= 1800:
			for i in range(nPlots):
				data[i].pop(0)
				
				
		if len(rawdata[0]) > 2000:
			for i in range(nPlots):
				rawdata[i].pop(0)

		if len(averagedata[0]) >= window:
			thread3 = threading.Thread(target=notchFilter,args=())
			thread3.start()



def notchFilter():
	global b, a, zi, averagedata, data, window, init
	with(mutex):

		for i in range(nPlots):
			#print(averagedata[i][0])
			if init == True:
				zi[i] = signal.lfilter_zi(b, a) * averagedata[i][0]
				init = False
			#print(zi)
			y, zi[i] = signal.lfilter(b, a, averagedata[i], zi=zi[i])
			#print(zo)
			for j in range(len(y)):
				data[i].append(y[j]*df)
			#print("Start data")
			#print(y)
		averagedata = [],[],[],[],[],[],[],[]
		#print(len(averagedata[0]))
		#if len(averagedata[0]) > window:
		#if init == 0:
			#print(sample.channel_data)
			#zi = []
			#print(zi[0])
			#print(zi.shape)
			#for i in range(nPlots):
				#print(i)
				#zi[i] = signal.lfilter_zi(b, a) * averagedata[i]
			#print(zi)
			#init = 1
		
		#for i in range(nPlots):
			#print("Length zi: ", len(zi[i]))
			#y, zi[i] = signal.lfilter(b, a, averagedata[i], zi[i])
			#print(y)
			#data[i].append(y*df)
			#averagedata = [0],[0],[0],[0],[0],[0],[0],[0]
	#x = (sample.channel_data[i]-average) * df
	#y, zi[i] = signal.lfilter(b, a, x, zi[i])
	#data[i].append(y)

def update():
	global curve, data, ptr, p, lastTime, fps, nPlots, count, board
	count += 1

	with(mutex):
		for i in range(nPlots):
		#curves[i].setData(data[(ptr+i)%data.shape[0]])
			curves[i].setData(data[i])
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
	p.setTitle('%0.2f fps' % fps)

    #app.processEvents()  ## force complete redraw for every plot


def main():

	#mw = QtGui.QMainWindow()
	#mw.resize(800,800)
	
	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(0)

	#while True:
		#sample = board._read_serial_binary()
		#data = sample.channel_data
		#print(sample.channel_data)		
		#update()
	print("Setup finished, starting threads")
	#thread3 = threading.Thread(target=notchFilter,args=())
	#thread3.start()
	thread1 = threading.Thread(target=dataCatcher,args=())
	thread1.start()
	thread2 = threading.Thread(target=QtGui.QApplication.instance().exec_(),args=())
	thread2.start()
	
	#thread3.join()
	#thread1.join()
	#thread2.join()
	
	#QtGui.QApplication.instance().exec_()
	print("Enter loop")
	while True:

		if raw_input() == "c":
			thread1.stop()
			thread2.stop()
			board.stop()
			board.disconnect()
	


if __name__ == '__main__':
	main()
	#import sys
	#if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		#QtGui.QApplication.instance().exec_()