from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

window = 75
fs = 250.0
f0 = 50.0
Q = 50
w0 = f0/(fs/2)
b, a = signal.iirnotch(w0, Q)


#N  = 30    # Filter order
#fk = 30
#Wn = fk/(fs/2) # Cutoff frequency
#b, a = signal.butter(N, Wn, output='ba')


#order = 2
#hc = 40.0/(fs/2)
#lc = 2.0/(fs/2)
#b, a = signal.butter(order, [lc, hc], btype='band', output='ba', analog=False)
#print(b)
#print(a)



w, h = signal.freqz(b, a)
 # Generate frequency axis
freq = w*fs/(2*np.pi)
 # Plot
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
ax[0].plot(freq, 20*np.log10(abs(h)), color='blue')
ax[0].set_title("Notch filter")
ax[0].set_ylabel("Amplitude (dB)", color='blue')
ax[0].set_xlim([0, 100])
ax[0].set_ylim([-25, 10])
ax[0].grid()
ax[1].plot(freq, np.unwrap(np.angle(h))*180/np.pi, color='green')
ax[1].set_ylabel("Angle (degrees)", color='green')
ax[1].set_xlabel("Frequency (Hz)")
ax[1].set_xlim([0, 100])
ax[1].set_yticks([-90, -60, -30, 0, 30, 60, 90])
ax[1].set_ylim([-90, 90])
ax[1].grid()
plt.show()