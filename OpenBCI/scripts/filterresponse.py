from scipy import signal
from scipy.signal import kaiserord, firwin
import numpy as np
import matplotlib.pyplot as plt

#window = 75
fs = 250.0
#f0 = 50.0
#Q = 50
#w0 = f0/(fs/2)
#b, a = signal.iirnotch(w0, Q)

nyq_rate = fs / 2.0
N = 151

# The cutoff frequency of the filter.
cutoff_hz = 3.0

# Use firwin with a Kaiser window to create a lowpass FIR filter.
#a = firwin(N, cutoff_hz/nyq_rate, pass_zero=False, window = 'hann')



#Bandpass
#a = firwin(N, [cutoff_hz/nyq_rate, 44/nyq_rate, 56/nyq_rate], pass_zero=False, window = 'hann')
bFir = firwin(N, 45/nyq_rate, pass_zero=True, window = 'hann')
bLong = np.repeat(1.0/1001, 1001)
bLong = np.repeat(1.0/50, 50)
bShort = np.repeat(1.0/25, 25)
bLong = -bLong
bShort = - bShort
bLong[0] = bLong[0] + 1
bShort[0] = bShort[0] + 1 
#bShort.resize(bLong.shape)
#bShortOne = bShort

#for i in range(len(bShortOne)):
	#if bShortOne[i] == 0:
		#bShortOne[i] = 1
#print(bShort)
N  = 30    # Filter order
fk = 45
Wn = fk/(fs/2) # Cutoff frequency
#b, a = signal.butter(N, Wn, output='ba')

xHat = signal.convolve(bLong, bShort, mode='full')
print(xHat)
#bTot = signal.convolve(1, -bShort)
bTot = signal.convolve(xHat, bFir, mode='full') 
#bTot = bShort
#bAvg1 = (1 - bShort - bLong)
#bAvgMul = bLong * bShortOne
#bAvg = bAvg1 + bAvgMul
#bFir.resize(bAvg.shape)
#bTot = bShort
#for i in range(len(bFir)):
	#if bFir[i] == 0:
		#bFir[i] = 1
#bTot = bAvg*bFir
#bTot = 1 - bLong
#print(bTot)
#Highpass
#a = signal.firwin(N, cutoff_hz/nyq_rate, pass_zero=False, window = 'hann') #Bandpass
#a = -a
#a[n/2] = a[n/2] + 1


#order = 2
#hc = 40.0/(fs/2)
#lc = 2.0/(fs/2)
#b, a = signal.butter(order, [lc, hc], btype='band', output='ba', analog=False)
#print(b)
#print(a)


def ampandphase(b, a = 1):
	w, h = signal.freqz(b, a)
	 # Generate frequency axis
	freq = w*fs/(2*np.pi)
	 # Plot
	fig, ax = plt.subplots(2, 1, figsize=(8, 6))
	ax[0].plot(freq, 20*np.log10(abs(h)), color='blue')
	ax[0].set_title("2 Step Average + Lowpass")
	ax[0].set_ylabel("Amplitude (dB)", color='blue')
	ax[0].set_xlim([0, 1])
	ax[0].set_ylim([-100, 10])
	ax[0].grid()
	ax[1].plot(freq, np.unwrap(np.angle(h))*180/np.pi, color='green')
	ax[1].set_ylabel("Angle (degrees)", color='green')
	ax[1].set_xlabel("Frequency (Hz)")
	ax[1].set_xlim([0, 100])
	ax[1].set_yticks([-7560, -6480, -5400, -4320, -3240, -2160, -1080, 0, 1080])
	ax[1].set_ylim([-8000, 1080])
	ax[1].grid()
	plt.show()


def plot_freqz(b,a=1):
	w,h = signal.freqz(b,a)
	h_dB = 20 * np.log10 (abs(h))
	plt.plot(w/np.pi, h_dB)
	plt.ylim([max(min(h_dB), -100) , 5])
	plt.ylabel('Magnitude (db)')
	plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
	plt.title(r'Amplitude response')

def plot_phasez(b, a=1):
	w,h = signal.freqz(b,a)
	h_Phase = np.unwrap(np.arctan2(np.imag(h),np.real(h)))
	plt.plot(w/np.pi, h_Phase)
	plt.ylabel('Phase (radians)')
	plt.xlabel(r'Normalized Frequency (x$\pi$rad/sample)')
	plt.title(r'Phase response')

def plot_impz(b, a = 1):
	if type(a)== int: #FIR
		l = len(b)
	else: # IIR
		l = 100
	impulse = np.repeat(0.,l); impulse[0] =1.
	x = np.arange(0,l)
	response = signal.lfilter(b, a, impulse)
	plt.stem(x, response, linefmt='b-', basefmt='b-', markerfmt='bo')
	plt.ylabel('Amplitude')
	plt.xlabel(r'n (samples)')
	plt.title(r'Impulse response')

def plot_stepz(b, a = 1):
	if type(a)== int: #FIR
		l = len(b)
	else: # IIR
		l = 100
	impulse = np.repeat(0.,l); impulse[0] =1.
	x = np.arange(0,l)
	response = signal.lfilter(b,a,impulse)
	step = np.cumsum(response)
	plt.plot(x, step)
	plt.ylabel('Amplitude')
	plt.xlabel(r'n (samples)')
	plt.title(r'Step response')

def plot_filterz(b, a=1):
	plt.subplot(221)
	plot_freqz(b, a)
	plt.subplot(222)
	plot_phasez(b, a)
	plt.subplot(223)
	plot_impz(b, a)
	plt.subplot(224)
	plot_stepz(b, a)
	plt.subplots_adjust(hspace=0.5, wspace = 0.3)

plot_filterz(bTot)
plt.show()
