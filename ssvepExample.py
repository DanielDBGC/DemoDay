"""
Generate Steady-State Visually Evoked Potential (SSVEP)
=======================================================

Steady-State Visually Evoked Potential (SSVEP) stimulus presentation.

"""

from time import time
from optparse import OptionParser

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet, local_clock

parser = OptionParser()
parser.add_option("-d", "--duration",
                  dest="duration", type='int', default=400,
                  help="duration of the recording in seconds.")

(options, args) = parser.parse_args()

# Create markers stream outlet
info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
outlet = StreamOutlet(info)

markernames = [1, 2]
start = time()

# Set up trial parameters
n_trials = 20
iti = 1.0
soa = 10.0
jitter = 0.4
record_duration = np.float32(options.duration)

# Set up trial list
stim_freq = np.random.binomial(1, 0.5, n_trials)
trials = DataFrame(dict(stim_freq=stim_freq, timestamp=np.zeros(n_trials)))

# Set up graphics
mywin = visual.Window([1920, 1200], monitor='testMonitor', units='deg',
                      fullscr=True)
grating = visual.GratingStim(win=mywin, mask='circle', pos=[-10, 0], size = 10, sf=0.2)
grating_neg = visual.GratingStim(win=mywin, mask='circle', pos=[-10, 0], size = 10, sf=0.2,
                                 phase=0.5)
grating2 = visual.GratingStim(win=mywin, mask='circle', pos=[10, 0], size= 10, sf=0.2)
grating2_neg = visual.GratingStim(win=mywin, mask='circle', pos=[10, 0], size = 10, sf=0.2,
                                 phase=0.5)                                
fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0, 0], sf=0,
                              color=[1, 0, 0], autoDraw=True)


def get_possible_ssvep_freqs(frame_rate, stim_type='reversal'):
    """Get possible SSVEP stimulation frequencies for specified frequencies."""
    
    # Define target frequencies
    target_freqs = [8.5, 12.0]
    freqs = {}
    
    for f in target_freqs:
        # Calculate frames per cycle for target frequency
        total_frames = round(frame_rate / f)
        
        if stim_type == 'single':
            # Split frames equally between on and off for 'single' stimulus type
            on_frames = total_frames // 2
            off_frames = total_frames - on_frames  # Remaining frames for off period
            freqs[f] = [(on_frames, off_frames)]
        
        elif stim_type == 'reversal':
            # Use same on/off pattern (total_frames, total_frames) for 'reversal' type
            freqs[f] = [(total_frames, total_frames)]
    
    return freqs

def init_flicker_stim(frame_rate, frequency, soa, stim_type='single'):
    """Initialize flickering stimulus for specific frequency."""

    # Calculate frames per cycle
    total_frames = round(frame_rate / frequency)
    
    if stim_type == 'single':
        # Split frames for on/off periods
        on_frames = total_frames // 2
        off_frames = total_frames - on_frames
        cycle = (on_frames, off_frames)
    
    elif stim_type == 'reversal':
        # For pattern reversal, use symmetric on/off
        cycle = (total_frames, total_frames)
    
    # Calculate frequency and number of cycles
    stim_freq = frame_rate / sum(cycle)
    n_cycles = int(soa * stim_freq)
    
    return {
        'cycle': cycle,
        'freq': stim_freq,
        'n_cycles': n_cycles
    }



# Set up stimuli
frame_rate = np.round(mywin.getActualFrameRate())  # Frame rate, in Hz
freqs = get_possible_ssvep_freqs(frame_rate, stim_type='reversal')
print(freqs)

stim_patterns = [init_flicker_stim(frame_rate, 2, soa),
                 init_flicker_stim(frame_rate, 3, soa)]

print('Flickering frequencies (Hz): {}\n'.format(
        [stim_patterns[0]['freq'], stim_patterns[1]['freq']]))

for ii, trial in trials.iterrows():
    # Intertrial interval
    core.wait(iti + np.random.rand() * jitter)

    # Select stimulus frequency
    ind = trials['stim_freq'].iloc[ii]
    # Send start marker
    timestamp = local_clock()
    outlet.push_sample([markernames[ind]], timestamp)

    grating.setAutoDraw(True)
    grating2.setAutoDraw(True)

    # Present flickering stimulus
    if ind == 0:
        for _ in range(int(stim_patterns[ind]['n_cycles'])):
            grating.setAutoDraw(True)
            for _ in range(int(stim_patterns[ind]['cycle'][0])):
                mywin.flip()
            grating.setAutoDraw(False)
            grating_neg.setAutoDraw(True)
            for _ in range(int(stim_patterns[ind]['cycle'][1])):
                mywin.flip()
            grating_neg.setAutoDraw(False)
    else:
        for _ in range(int(stim_patterns[ind]['n_cycles'])):
            grating2.setAutoDraw(True)
            for _ in range(int(stim_patterns[ind]['cycle'][0])):
                mywin.flip()
            grating2.setAutoDraw(False)
            grating2_neg.setAutoDraw(True)
            for _ in range(int(stim_patterns[ind]['cycle'][1])):
                mywin.flip()
            grating2_neg.setAutoDraw(False)

    # offset
    mywin.flip()
    if len(event.getKeys()) > 0 or (time() - start) > record_duration:
        break
    event.clearEvents()

# Cleanup
mywin.close()