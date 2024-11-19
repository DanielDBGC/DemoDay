from time import time
from optparse import OptionParser
import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet, local_clock
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from utils.exp import get_possible_ssvep_freqs, init_flicker_stim, flicker_stimulus

# Argument parsing for duration
parser = OptionParser()
parser.add_option("-d", "--duration", dest="duration", type='int', default=300, help="duration of the recording in seconds.")
(options, args) = parser.parse_args()

# Create LSL stream for markers
marker_info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
marker_outlet = StreamOutlet(marker_info)
markernames = [1, 2]
start = time()

# EEG data stream setup with BrainFlow and LSL
# params = BrainFlowInputParams()
#arams.serial_port = 'COM3'  # Update with your Cyton board's port
# board = BoardShim(BoardIds.CYTON_BOARD.value, params)
# board.prepare_session()
# board.start_stream()

## Create an LSL stream for EEG data
# eeg_info = StreamInfo('Cyton_EEG', 'EEG', BoardShim.get_num_rows(BoardIds.CYTON_BOARD.value) - 1, 
#                       BoardShim.get_sampling_rate(BoardIds.CYTON_BOARD.value), 'float32', 'eeg_stream')
# eeg_outlet = StreamOutlet(eeg_info)

# Set up BrainFlow with SyntheticBoard (ID=BoardIds.SYNTHETIC_BOARD)
params = BrainFlowInputParams()
board_id = BoardIds.SYNTHETIC_BOARD.value
board = BoardShim(board_id, params)

# Prepare the board for streaming data
board.prepare_session()
board.start_stream()

# Set up an LSL outlet to mimic an EEG stream from BrainFlow
info = StreamInfo('BrainFlow_Synthetic_EEG', 'EEG', 16, BoardShim.get_sampling_rate(board_id), 'float32', 'synthetic_brainflow')
outlet = StreamOutlet(info)

# Variables for trials and stimuli
n_trials = 20
iti = 1.0
soa = 10.0
jitter = 0.4
record_duration = np.float32(options.duration)
stim_freq = np.random.binomial(1, 0.5, n_trials)
trials = DataFrame(dict(stim_freq=stim_freq, timestamp=np.zeros(n_trials)))

# Graphics setup
mywin = visual.Window([1920, 1200], monitor='testMonitor', units='deg', fullscr=True)
grating = visual.GratingStim(win=mywin, mask='circle', pos=[-10, 0], size=10, sf=0.2)
grating_neg = visual.GratingStim(win=mywin, mask='circle', pos=[-10, 0], size=10, sf=0.2, phase=0.5)
grating2 = visual.GratingStim(win=mywin, mask='circle', pos=[10, 0], size=10, sf=0.2)
grating2_neg = visual.GratingStim(win=mywin, mask='circle', pos=[10, 0], size=10, sf=0.2, phase=0.5)
fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0, 0], sf=0, color=[1, 0, 0], autoDraw=True)

# Set up stimuli
frame_rate = np.round(mywin.getActualFrameRate())  # Frame rate, in Hz
freqs = get_possible_ssvep_freqs(frame_rate, stim_type='reversal')
print(freqs)

stim_patterns = [init_flicker_stim(frame_rate, 2, soa),
                 init_flicker_stim(frame_rate, 3, soa)]

print('Flickering frequencies (Hz): {}\n'.format(
        [stim_patterns[0]['freq'], stim_patterns[1]['freq']]))

# EEG data streaming loop
print('Starting EEG data stream...')
try:
    for ii, trial in trials.iterrows():
        core.wait(iti + np.random.rand() * jitter)
        ind = trials['stim_freq'].iloc[ii]
        
        # Send marker for the stimulus onset
        timestamp = local_clock()
        marker_outlet.push_sample([markernames[ind]], timestamp)
        print(f"Marker {markernames[ind]} sent at timestamp {timestamp}")

        # Set up visual stimuli flicker
        grating.setAutoDraw(True)
        grating2.setAutoDraw(True)
        
        # Flickering stimulus based on the trial index
        if ind == 0:
            flicker_stimulus(grating, grating_neg, stim_patterns[ind])
        else:
            flicker_stimulus(grating2, grating2_neg, stim_patterns[ind])

        # Collect EEG data if available and send to LSL
        data = board.get_board_data()  # Fetch latest data from Cyton
        for sample in data.T:
            outlet.push_sample(sample.tolist()[:16], local_clock())
        
        # Break on exit key or time limit
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break
        event.clearEvents()

finally:
    # Stop and release BrainFlow session
    # Collect and send EEG data to the LSL outlet
    marker_outlet.push_sample([-1], local_clock())
    board.stop_stream()
    board.release_session()
    mywin.close()
    print('EEG and stimulus streams have ended.')
