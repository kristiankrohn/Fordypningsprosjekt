import Tkinter as tk
import time as tme
from numpy.random import randint
from globalvar import *
size = 1000
speed = 30
ballsize = 30
startButton = None
w = None
root = None

class Alien(object):
    def __init__(self, canvas, *args, **kwargs):
    	global center, right, left, up, down
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

    def move(self):
    	global size, speed, center, right, left, up, down
        x1, y1, x2, y2 = self.canvas.bbox(self.id)

        if not center and ((right and (x1 <= (size/2) - ballsize)) 
        				or (down and (y1 <= (size/2) - ballsize)) 
        				or (left and (x2 >= (size/2) + ballsize)) 
        				or (up and (y2 >= (size/2) + ballsize))):
        	self.vx = 0
        	self.vy = 0
        	center = True

        	if right:
        		saveright()
        		print("Right")
        	elif left:
        		saveleft()
        		print("Left")
        	elif up:
        		saveup()
        		print("Up")
        	elif down:
        		savedown()
        		print("Down")

        	right = False
        	left = False
        	up = False
        	down = False
        	tme.sleep(4)
        	savecenter()
        	z = randint(0,4)
        	#print(z)
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


def saveleft():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	f.write('l1')
	
	for i in range(nSamples-750, nSamples):
		f.write(',')
		f.write(data[1][i])
		
	f.write(':')
	f.close()
def saveright():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	f.write('r1')
	
	for i in range(nSamples-750, nSamples):
		f.write(',')
		f.write(str(data[1][i]))
		
	f.write(':')
	f.close()
def saveup():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	f.write('u1')
	
	for i in range(nSamples-750, nSamples):
		f.write(',')
		f.write(str(data[1][i]))
		
	f.write(':')
	f.close()
def savedown():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	f.write('d1')
	
	for i in range(nSamples-750, nSamples):
		f.write(',')
		f.write(str(data[1][i]))
		
	f.write(':')
	f.close()
def savecenter():
	global data, nSamples
	#print(data[1])
	f = open('data.txt', 'a')
	f.write('c1')
	
	for i in range(nSamples-750, nSamples):
		f.write(',')
		f.write(str(data[1][i]))
		
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