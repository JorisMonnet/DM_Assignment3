from music21 import converter, note, chord
from collections import defaultdict

def extract_pitches_and_intervals(midi_file_path):
    """
    Extract pitches and intervals from a MIDI file.
    """
    midi_data = music21.converter.parse(midi_file_path)

    pitches = []
    for note in midi_data.recurse().notes:
        if note.isNote:
            pitches.append(note.pitch.midi)

    # Calculate the interval (difference) between pitches
    intervals = []
    for i in range(1, len(pitches)):
        interval = pitches[i] - pitches[i-1]
        intervals.append(interval)

    return pitches, intervals

def find_repeated_patterns(data_dict, pattern_length=8):
    """
    Find repeated patterns of a given length in a dictionary of data.
    The dictionary keys are onsets (times) and values are pitches.
    """
    pattern_dict = defaultdict(list)
    data_list = list(data_dict.values())
    onsets = list(data_dict.keys())

    for i in range(len(data_list) - pattern_length + 1):
        pattern = tuple(data_list[i:i + pattern_length])
        onset_pattern = tuple(onsets[i:i + pattern_length])
        pattern_dict[pattern].append(onset_pattern)
    
    pattern_dict = {k: v for k, v in pattern_dict.items() if len(v) > 1}
    return pattern_dict

def filter_subpatterns(repeated_patterns):
    """
    Filter out subpatterns from a dictionary of repeated patterns.
    """
    patterns = list(repeated_patterns.keys())
    filtered_patterns = set(patterns)

    for i, pattern1 in enumerate(patterns):
        for pattern2 in patterns[i+1:]:
            if len(pattern1) < len(pattern2):
                if any(pattern1 == pattern2[j:j+len(pattern1)] for j in range(len(pattern2) - len(pattern1) + 1)):
                    filtered_patterns.discard(pattern1)
                    break

    return {pattern: repeated_patterns[pattern] for pattern in filtered_patterns}

def get_filtered_patterns(data_dict, direction='forward', min_length=9, max_length=350):
    """
    Get filtered patterns from a dictionary of data.
    The dictionary keys are onsets (times) and values are pitches.
    """
    all_repeated_patterns = defaultdict(list)
    
    for pattern_length in range(min_length, max_length):
        # print(f"Checking patterns of length {pattern_length}:")
        repeated_patterns = find_repeated_patterns(data_dict, pattern_length)
        if not repeated_patterns:
          print(f"No more repeated patterns found at length {pattern_length}. Exiting loop.")
          break
        for pattern, onsets in repeated_patterns.items():
            if len(onsets) > 1:
                all_repeated_patterns[pattern] = onsets
                # print(f'Pattern {pattern} occurs {len(onsets)} times at onsets {onsets}.')
    
    filtered_patterns = filter_subpatterns(all_repeated_patterns)
    
    return filtered_patterns

def extract_onsets(midi_file_path):
    """
    Extract onsets from a MIDI file and return a sorted list of onset times.
    
    Parameters:
    midi_file_path (str): Path to the MIDI file
    
    Returns:
    List[float]: Sorted list of onset times
    """
    midi_data = converter.parse(midi_file_path)
    onsets = []
    
    for element in midi_data.flat.notes:
        if isinstance(element, note.Note) or isinstance(element, chord.Chord):
            onsets.append(element.offset)
    
    # Sort the onsets to ensure they are in order
    onsets = sorted(onsets)
    durations = [round(float(onsets[i+1] - onsets[i]), 2) for i in range(len(onsets) - 1)]
    
    return onsets,durations

def extract_onset_pitch_dict(midi_file_path):
    """
    Extract a dictionary from a MIDI file where keys are onset times and values are pitches.
    
    Parameters:
    midi_file_path (str): Path to the MIDI file
    
    Returns:
    dict: Dictionary with onset times as keys and pitches as values
    """
    midi_data = converter.parse(midi_file_path)
    onset_pitch_dict = {}

    for element in midi_data.flat.notes:
        if isinstance(element, note.Note):
            onset_pitch_dict[element.offset] = element.pitch.midi
        elif isinstance(element, chord.Chord):
            for pitch in element.pitches:
                onset_pitch_dict[element.offset] = pitch.midi

    return onset_pitch_dict

def extract_onset_duration_dict(midi_file_path):
    """
    Extract a dictionary from a MIDI file where keys are onset times and values are the durations of the notes or chords.
    
    Parameters:
    midi_file_path (str): Path to the MIDI file
    
    Returns:
    dict: Dictionary with onset times as keys and durations as values
    """
    midi_data = converter.parse(midi_file_path)
    onset_duration_dict = {}

    for element in midi_data.flat.notes:
        if element.offset not in onset_duration_dict:
            # Store the duration for the first occurrence of this offset
            onset_duration_dict[element.offset] = element.duration.quarterLength

    return onset_duration_dict

def list_midi_files(base_path):
    midi_paths = []
    # Specify exact filenames to search for
    target_files = ['midi_score.mid', 'midi_score.midi']
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file in target_files:
                midi_paths.append(os.path.join(root, file))
    return midi_paths

def process_folder(base_path):
    midi_files = list_midi_files(base_path)
    pitch_pattern_counts = {}
    duration_pattern_counts = {}
    
    for midi_file in midi_files:
        onset_duration_dict = extract_onset_duration_dict(midi_file)
        onset_pitches_dict = extract_onset_pitch_dict(midi_file)
        
        duration_patterns = get_filtered_patterns(onset_duration_dict)
        pitches_patterns = get_filtered_patterns(onset_pitches_dict)
        
        # Create a key using the basename and parent directory name
        parent_dir = os.path.basename(os.path.dirname(midi_file))
        key_name = f"{parent_dir}/{os.path.basename(midi_file)}"
        
        duration_pattern_counts[key_name] = len(duration_patterns)
        pitch_pattern_counts[key_name] = len(pitches_patterns)
        
        print(f"Processed {midi_file}:")
        print('Here are duration patterns')
        for pattern, onsets in duration_patterns.items():
            print(f'length is {len(pattern)}')
            print(f'Pattern{pattern}  occurs {len(onsets)} at onsets {onsets}')
        print('Here are pitches patterns')
        for pattern, onsets in pitches_patterns.items():
            print(f'length is {len(pattern)}')
            print(f'Pattern{pattern} occurs {len(onsets)} at onsets {onsets}')
    
    return duration_pattern_counts, pitch_pattern_counts

def plot_pattern_counts(pattern_counts, title):
    """ Plots the counts of patterns from the dictionary """
    # Names of the files
    names = list(pattern_counts.keys())
    # Count of patterns
    counts = list(pattern_counts.values())
    
    # Creating the bar chart
    plt.figure(figsize=(10, 8))  # Size of the figure
    plt.barh(names, counts, color='skyblue')
    plt.xlabel('Count of Patterns')
    plt.ylabel('MIDI Files')
    plt.title(title)
    plt.gca().invert_yaxis()  # Invert the y-axis to have the highest counts at the top
    plt.show()


  


