import time as tme
from threading import Lock
global data
global nSamples
global timeData
global timestamp
global avgLength
data = [],[],[],[],[],[],[],[]
timeData = [],[],[],[],[],[],[],[]
#nSamples = 1000
nSamples = 1800
avgLength = 1000
timestamp = tme.time()

mutex = Lock()