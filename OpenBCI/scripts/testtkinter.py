import Tkinter as tk
import time as tme
from numpy.random import randint
from globalvar import *
from threading import Lock
import threading
mutex = Lock()
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
		x1, y1, x2, y2 = self.canvas.bbox(self.id)

		if not center and ((right and (x1 <= (size/2) - ballsize)) 
						or (down and (y1 <= (size/2) - ballsize)) 
						or (left and (x2 >= (size/2) + ballsize)) 
						or (up and (y2 >= (size/2) + ballsize))):
			self.vx = 0
			self.vy = 0
			center = True
			endMove = tme.time()
			print("Movementtime= ")
			print(endMove - startMove)

			if right:
				cmd = 'right'
				threadSave = threading.Thread(target=saveData, args=(cmd))
				threadSave.setDaemon(True)
				threadSave.start()

			elif left:
				cmd = 'left'
				threadSave = threading.Thread(target=saveData, args=(cmd))
				threadSave.setDaemon(True)
				threadSave.start()

			elif up:
				cmd = 'up'
				threadSave = threading.Thread(target=saveData, args=(cmd))
				threadSave.setDaemon(True)
				threadSave.start()

			elif down:
				cmd = 'down'
				threadSave = threading.Thread(target=saveData, args=(cmd))
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
			cmd = 'center'
			threadSave = threading.Thread(target=saveData, args=(cmd))
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

def saveData(direction):
	global data, nSamples
	length = 100
	with(mutex):
		temp = data
	if len(temp[1]) > length:
		f = open('data.txt', 'a')
	
		if direction == 'left':
			f.write('l1')
		elif direction == 'right':
			f.write('r1')
		elif direction == 'up':
			f.write('u1')
		elif direction == 'down':
			f.write('d1')
		elif direction == 'center':
			f.write('c1')
		print("New save")
		start = len(temp[1])-length+5
		stop = len(temp[1])-5
		#print(start)
		#print(stop)
		for i in range(start, stop):
			f.write(',')
			num = temp[1][i]
			f.write(str(num))
			#print(i)
		f.write(':')
		f.close()

def saveleft():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	with(mutex):
		if len(data[1])>750:
			f.write('l1')
			print(len(data[1])-10)
			print(len(data[1])-1)
			for i in range(len(data[1])-750, len(data[1])-1):
				f.write(',')
				f.write(str(data[1][i]))
				print(i)
		
		f.write(':')
	f.close()
def saveright():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	with(mutex):
		if len(data[1])>750:
			f.write('r1')
			print(len(data[1])-10)
			print(len(data[1])-1)
			for i in range(len(data[1])-750, len(data[1])-1):
				f.write(',')
				f.write(str(data[1][i]))
				print(i)
	
		f.write(':')
	f.close()
def saveup():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	with(mutex):
		if len(data[1])>750:
			f.write('u1')
			print(len(data[1])-10)
			print(len(data[1])-1)
			for i in range(len(data[1])-750, len(data[1])-1):
				f.write(',')
				f.write(str(data[1][i]))
				print(i)
	
		f.write(':')
	f.close()
def savedown():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	with(mutex):
		if len(data[1])>750:
			f.write('d1')
			print(len(data[1])-10)
			print(len(data[1])-1)
			for i in range(len(data[1])-750, len(data[1])-1):
				f.write(',')
				f.write(str(data[1][i]))
				print(i)
				
		f.write(':')
	f.close()
def savecenter():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	with(mutex):
		if len(data[1])>750:	
			f.write('c1')
			print(len(data[1])-10)
			print(len(data[1])-1)
			for i in range(len(data[1])-750, len(data[1])-1):
				f.write(',')
				f.write(str(data[1][i]))
				print(i)
			
		f.write(':')
	f.close()

def openFile():
	
	file = open('data.txt', 'r')
	AllData = file.read()
	DataSet = []
	DataSet = AllData.split(':')
	#print(DataSet)
	for i in range(len(DataSet)):
		feature = []
		feature = DataSet[i].split(',')
		featuretype = feature[0]
		feature.pop(0)
		print("Featuretype = ")
		print(featuretype)
		print("Featuredata = ")
		print(feature)
		#Sort on featuretype and put feature in corresponding array