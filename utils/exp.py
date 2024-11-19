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

def flicker_stimulus(grating, grating_neg, stim_pattern):
    """
    Flicker a visual stimulus on and off according to the specified pattern.

    Parameters:
    grating (visual.GratingStim): The primary grating stimulus.
    grating_neg (visual.GratingStim): The negative-phase grating stimulus.
    stim_pattern (dict): Dictionary containing the flickering pattern, with:
                         - 'n_cycles' (int): Number of cycles to repeat.
                         - 'cycle' (tuple): Number of frames for each on/off period (e.g., (on_frames, off_frames)).
    """
    # Extract the number of cycles and frames per cycle
    n_cycles = stim_pattern['n_cycles']
    on_frames, off_frames = stim_pattern['cycle']
    
    # Loop through the cycles
    for _ in range(n_cycles):
        # Show the primary grating for the "on" period
        grating.setAutoDraw(True)
        for _ in range(on_frames):
            grating.win.flip()  # Update the window display

        # Hide the primary grating and show the negative-phase grating for the "off" period
        grating.setAutoDraw(False)
        grating_neg.setAutoDraw(True)
        for _ in range(off_frames):
            grating.win.flip()  # Update the window display

        # Hide the negative-phase grating to reset before the next cycle
        grating_neg.setAutoDraw(False)