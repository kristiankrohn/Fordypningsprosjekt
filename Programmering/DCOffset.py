import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab

directoryName = 'C:\Users\Adrian Ribe\Desktop\BrainProgram\SavedData/'
fName = 'OpenBCI-RAW-2017-09-04_11-28-01.txt'

samplingFrequencyHz = 250.0
timeLimSeconds = [0.0, 350.0]



data = np.genfromtxt(directoryName + fName, delimiter = ', ', dtype= "|S5", skip_header = 6, skip_footer = 1)
eegDatauV = data[:, 1:(8 + 1)]
timeSeconds = np.arange(len(eegDatauV[:, 0])) / samplingFrequencyHz

nchan = 1  #normally 8 or 16
ncol = 1;
nrow = nchan / ncol
plt.figure(figsize=(ncol*10, nrow*5))
for Ichan in range(nchan):
    plt.subplot(nrow,ncol,Ichan+1)
    plt.plot(timeSeconds,eegDatauV[:, Ichan])
    plt.xlabel("Time (sec)")
    plt.ylabel("Raw EEG (uV)")
    plt.title("Channel " + str(Ichan+1))
    plt.xlim(timeLimSeconds)
    #plt.ylim([-1.5, 1.5])

plt.tight_layout()
plt.show()
