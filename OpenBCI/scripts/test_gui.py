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

mutex = Lock()

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


port = 'COM6'
baud = 115200
logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
logging.info('---------LOG START-------------')
board = bci.OpenBCIBoard(port=port, scaled_output=False, log=True)
print("Board Instantiated")
board.ser.write('v')
tme.sleep(10)
if not board.streaming:
	board.ser.write(b'b')
	board.streaming = True

def dataCatcher():
	global board
	board.start_streaming(printData)
def printData(sample):	
	#print("fallos")
	global nPlots, data 
	
	with(mutex):
		for i in range(nPlots):
			avg = 0
			for j in range(len(data[0])-1):
				avg = avg + data[i][j]

			average = avg / len(data)
			data[i].append((sample.channel_data[i]/1000)-average)
	
		if len(data[0]) >= 1800:
			for i in range(nPlots):
				data[i].pop(0)
	
def update():
	global curve, data, ptr, p, lastTime, fps, nPlots, count, board
	count += 1

	#sample = board._read_serial_binary()
	#data.append(sample.channel_data)
	#print("penis")
	#for i in range(nPlots):
		#avg = 0
		#for j in range(len(data[0])-1):
			#avg = avg + data[i][j]

		#average = avg / len(data)
		#data[i].append((sample.channel_data[i]/1000)-average)
		#print(i)



	#if count >= 1800:
		#for i in range(nPlots):
			#data[i].pop(0)
	#print(len(data[0]))	
	#data = np.append(data, sample.channel_data)
	#if data.shape[0] >= nSamples:
	#	data = np.delete(data, data[0:7:1])
	#	print("delete")
	#print(data[0])
	#print(data.shape[0])
    #print "---------", count
	with(mutex):
		for i in range(nPlots):
		#curves[i].setData(data[(ptr+i)%data.shape[0]])
			curves[i].setData(data[i])
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

	sample = board._read_serial_binary()
	data = sample.channel_data




	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(0)

	#while True:
		#sample = board._read_serial_binary()
		#data = sample.channel_data
		#print(sample.channel_data)		
		#update()
	
	thread2 = threading.Thread(target=dataCatcher,args=())
	thread2.start()
	thread1 = threading.Thread(target=QtGui.QApplication.instance().exec_(),args=())
	thread1.start()
	thread1.join()
	thread2.join()
	#QtGui.QApplication.instance().exec_()
	#while True:
		#print("pikk")
	#thread1.stop()
	#thread2.stop()
if __name__ == '__main__':
	main()
	#import sys
	#if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		#QtGui.QApplication.instance().exec_()