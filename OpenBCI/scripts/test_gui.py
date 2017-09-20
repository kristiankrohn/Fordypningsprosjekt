import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import os
import logging
import time
#import matplotlib.pyplot as plt
#import matplotlib.animation as animation
#from matplotlib import style
import pyqtgraph
from streamplot import PlotManager


i = 0

def printData(sample):
	#os.system('cls')
	#print "----------------"
	#print("%f" %(sample.id))
	#print sample.channel_data
	#print sample.channel_data[0]
	#print sample.channel_data[1]
	#print sample.channel_data[2]
	#print sample.channel_data[3]
	#print sample.channel_data[4]
	#print sample.channel_data[5]
	#print sample.channel_data[6]
	#print sample.channel_data[7]
	#print sample.channel_data[8]
	#print sample.aux_data
	#print "----------------"
	global i
	global plt_mgr
	print(i)
	plt_mgr.add(name="Channel 1", x=i, y=sample.channel_data[0])
	plt_mgr.add(name="Channel 2", x=i, y=sample.channel_data[1])
	plt_mgr.add(name="Channel 3", x=i, y=sample.channel_data[2])
	plt_mgr.add(name="Channel 4", x=i, y=sample.channel_data[3])
	plt_mgr.add(name="Channel 5", x=i, y=sample.channel_data[4])
	plt_mgr.add(name="Channel 6", x=i, y=sample.channel_data[5])
	plt_mgr.add(name="Channel 7", x=i, y=sample.channel_data[6])
	plt_mgr.add(name="Channel 8", x=i, y=sample.channel_data[7])
	plt_mgr.update()
	i = i + 1

#def main():
port = 'COM6'
baud = 115200
logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
logging.info('---------LOG START-------------')
board = bci.OpenBCIBoard(port=port, scaled_output=False, log=True)
print("Board Instantiated")
board.ser.write('v')
time.sleep(10)

plt_mgr = PlotManager(title="Hello plot")

board.start_streaming(printData)
plt_mgr.close()

#if __name__ == '__main__':
	#main()