import Tkinter as tk
import time as tme
from numpy.random import randint
from globalvar import *
#from threading import Lock
import threading
import matplotlib.pyplot as plt

#mutex = Lock()


size = 1000
speed = 30
ballsize = 30
startButton = None
w = None
root = None
sleeping = False
startMove = tme.time()
endMode = tme.time()


class Alien(object):
	def __init__(self, canvas, *args, **kwargs):
		global center, right, left, up, down, startSleep, startMove, endMove
		self.canvas = canvas
		self.id = canvas.create_oval(*args, **kwargs)
		#self.canvas.coords(self.id, [20, 260, 120, 360])
		self.vx = speed
		self.vy = 0
		center = False
		right = False
		left = False
		up = False
		down = False
		startSleep = 0

	def move(self):
		global size, speed, center, right, left, up, down, startSleep, sleeping, startMove, endMove
		global timestamp
		x1, y1, x2, y2 = self.canvas.bbox(self.id)

		if not center and ((right and (x1 <= (size/2) - ballsize)) 
						or (down and (y1 <= (size/2) - ballsize)) 
						or (left and (x2 >= (size/2) + ballsize)) 
						or (up and (y2 >= (size/2) + ballsize))):
			self.vx = 0
			self.vy = 0
			center = True
			#endMove = tme.time()
			#print("Movementtime= ")
			#print(tme.time())

			cmd = 0
			if right:
				cmd = 6
				
			elif left:
				cmd = 4

			elif up:
				cmd = 8

			elif down:
				cmd = 2

			
			threadSave = threading.Thread(target=saveTempData, args=(cmd,))
			threadSave.setDaemon(True)
			threadSave.start()

			right = False
			left = False
			up = False
			down = False
			startSleep = tme.time()
			sleeping = True
			#tme.sleep(4)

		if sleeping and (tme.time() > startSleep + 5):
			cmd = 5
			endMove = tme.time()
			#print("Movementtime= ")
			#print(tme.time())
			threadSave = threading.Thread(target=saveTempData, args=(cmd,))
			threadSave.setDaemon(True)
			threadSave.start()
			z = randint(0,4)
			sleeping = False
			#print(z)
			startMove = tme.time()
			if z == 0:
				self.vx = -speed
				self.vy = 0
			elif z == 1:
				self.vx = speed
				self.vy = 0
			elif z == 2:
				self.vx = 0
				self.vy = -speed
			else:
				self.vx = 0
				self.vy = speed

		if x2 > size:
			self.vx = 0
			right = True
			center = False
			#tme.sleep(1)
			self.vx = -speed

		if x1 < 0:
			self.vx = 0
			left = True
			center = False
			#tme.sleep(1)
			self.vx = speed

		if y2 > size:
			self.vy = 0
			down = True
			center = False
			#tme.sleep(1)
			self.vy = -speed
			
		if y1 < 0:
			self.vy = 0
			up = True
			center = False
			#tme.sleep(1)
			self.vy = speed

		self.canvas.move(self.id, self.vx, self.vy)


class Ball(object):
	def __init__(self, master, **kwargs):
		self.master = master
		self.canvas = tk.Canvas(self.master, width=size, height=size)
		self.canvas.pack()
		self.aliens = Alien(self.canvas, (size/2) - ballsize, (size/2) - ballsize, (size/2) + ballsize, (size/2) + ballsize, outline='white', fill='red')
		self.canvas.pack()
		self.master.after(0, self.animation)


	def animation(self):
		#for alien in self.aliens:
		self.aliens.move()
		self.master.after(12, self.animation)

	def close_window(self):
		self.destroy()

def startgui():
	global startButton, w, root
	w.pack_forget()
	startButton.pack_forget()
	Ball(root)

def guiloop():
	global startButton, w, root
	root = tk.Tk()
	root.title("Training GUI")
	w = tk.Label(root, text="Look at the red dot, press start when ready!")
	w.pack()
	startButton = tk.Button(root, text='Start', width=25, command=startgui)
	startButton.pack()
	exitButton = tk.Button(root, text='Exit', width=25, command=root.destroy)
	exitButton.pack()
	#root = tk.Tk()
	#app = App(root)
	root.mainloop()

def saveTempData(direction):
	global data, nSamples
	global timeData
	global mutex
	length = 500

	startTime = tme.time() + 0.25
	ready = False

	while not ready:
		if timeData[1][-1] > startTime:
			ready = True

	#print("Found correct timestamp")
	#print(startTime)
	#print(timeData[1][-1])

	with(mutex):
		temp = data
		tempTime = timeData

	if len(temp[1]) > length:
		f = open('temp.txt', 'a')
		good = True
		if direction == 4:
			f.write('l1')
		elif direction == 6:
			f.write('r1')
		elif direction == 8:
			f.write('u1')
		elif direction == 2:
			f.write('d1')
		elif direction == 5:
			f.write('c1')
		else:
			good = False
		#print("New save")

		#stopindex = tempTime[1].index(startTime)
		stopindex = len(temp[1])-5

		for i in range(len(tempTime[1])-1, 0, -1):
			if tempTime[1][i]<=startTime:
				stopindex = i
				break

		#if stopindex + 50 < len(temp[1])-1:
			#stop = stopindex + 50
		#else:
		stop = stopindex
		
		start = stop - length

		#start = len(temp[1])-length+5
		#print(len(temp[1]))
		#print(len(tempTime[1]))
		#print(stop)
		#print(start)
		#print("Saving from time: ")
		#print(startTime)
		#print(timeData[1][stop])
		if good:
			for i in range(start, stop):
				f.write(',')
				#print(i)
				#print(stop)
				num = temp[1][i]
				f.write(str(num))
				#print(i)
			f.write(':')
		f.close()



def openFile():
	
	file = open('data.txt', 'r')
	AllData = file.read()
	DataSet = []
	DataSet = AllData.split(':')
	#print(DataSet)
	file.close()
	for i in range(len(DataSet)):
		feature = []
		feature = DataSet[i].split(',')
		featuretype = feature[0]
		feature.pop(0)

		featureData = map(float, feature)
		plt.plot(featureData, label=featuretype)
		
		plt.ylabel('uV')
		plt.xlabel(featuretype)
		
		plt.show()
	

def saveData():
	tempfile = open('temp.txt', 'r')
	tempData = tempfile.read()
	tempfile.close()
	permfile = open('data.txt', 'a')
	permfile.write(tempData)
	permfile.close()
	tempfile = open('temp.txt', 'w')
	tempfile.truncate(0)
	tempfile.close()
	print("Saved")

def clearTemp():
	tempfile = open('temp.txt', 'w')
	tempfile.truncate(0)
	tempfile.close()
	print("Temp is cleared")

def clearData():
	tempfile = open('data.txt', 'w')
	tempfile.truncate(0)
	tempfile.close()
	print("Data is deleted")