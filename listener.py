import os
os.chdir("C:/Users/danie_13ucdo4/OneDrive/Desktop/ITAM/Neuro/SSVEP_EXP/data")
import csv
from pylsl import StreamInlet, resolve_stream
import time

# Resolve the EEG data stream
print("Looking for EEG stream...")
eeg_streams = resolve_stream('type', 'EEG')
eeg_inlet = StreamInlet(eeg_streams[0])

# Resolve the Marker stream
print("Looking for Marker stream...")
marker_streams = resolve_stream('type', 'Markers')
marker_inlet = StreamInlet(marker_streams[0])

# File names
eeg_file = "eeg_data.csv"
marker_file = "markers.csv"

# Open files to write data
with open(eeg_file, mode='w', newline='') as eeg_csv, \
     open(marker_file, mode='w', newline='') as marker_csv:
    
    eeg_writer = csv.writer(eeg_csv)
    marker_writer = csv.writer(marker_csv)
    
    # Write headers
    eeg_writer.writerow(['timestamp'] + [f'channel_{i+1}' for i in range(16)])
    marker_writer.writerow(['timestamp', 'marker'])

    print("Starting data collection. Press Ctrl+C to stop.")
    try:
        while True:
            # Pull EEG data
            eeg_sample, eeg_timestamp = eeg_inlet.pull_sample(timeout=0.0)
            if eeg_sample:
                eeg_writer.writerow([eeg_timestamp] + eeg_sample)

            # Pull Marker data
            marker_sample, marker_timestamp = marker_inlet.pull_sample(timeout=0.0)
            if marker_sample:
                marker_writer.writerow([marker_timestamp, marker_sample[0]])

    except KeyboardInterrupt:
        print("Data collection stopped.")
    finally:
        print("Files saved:")
        print(f"EEG data: {eeg_file}")
        print(f"Marker data: {marker_file}")
