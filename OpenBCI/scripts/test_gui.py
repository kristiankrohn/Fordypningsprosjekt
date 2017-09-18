import sys; sys.path.append('..') # help python find open_bci_v3.py relative to scripts folder
import open_bci_v3 as bci
import os
import logging
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
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

	xs.append(sample.id)
	ys.append(sample.channel_data[0])
	print(xs)
	#ax1.clear()
	#ax1.plot(xs, ys)
	#ani = animation.FuncAnimation(fig, animate, interval=1000)
	#plt.show()	


if __name__ == '__main__':
	port = 'COM6'
	#port = '/dev/tty.OpenBCI-DN008VTF'
	#port = '/dev/tty.OpenBCI-DN0096XA'
	baud = 115200
	logging.basicConfig(filename="test.log",format='%(asctime)s - %(levelname)s : %(message)s',level=logging.DEBUG)
	logging.info('---------LOG START-------------')
	board = bci.OpenBCIBoard(port=port, scaled_output=False, log=True)
	print("Board Instantiated")

	board.ser.write('v')
	time.sleep(10)

	
	style.use('fivethirtyeight')
	xs = []
	ys = []
	fig = plt.figure()
	ax1 = fig.add_subplot(1,1,1)

	board.start_streaming(printData)
	#board.print_bytes_in()



