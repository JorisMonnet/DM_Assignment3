from music21 import converter, note, chord

def extract_pitches_from_midi(file_path):
    score = converter.parse(file_path)
    pitches = []
    
    for element in score.recurse():
        if isinstance(element, note.Note):
            pitches.append(element.pitch.midi)
        elif isinstance(element, chord.Chord):
            pitches.extend([p.midi for p in element.pitches])
    
    return pitches

def extract_pitches_and_intervals(midi_file_path):
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

def find_repeated_patterns(data_list, pattern_length=8):
    pattern_dict = defaultdict(int)
    for i in range(len(data_list) - pattern_length + 1):
        pattern = tuple(data_list[i:i + pattern_length])
        pattern_dict[pattern] += 1
    return pattern_dict

def filter_subpatterns(repeated_patterns):
    patterns = list(repeated_patterns.keys())
    filtered_patterns = set(patterns)

    for i, pattern1 in enumerate(patterns):
        for pattern2 in patterns[i+1:]:
            if len(pattern1) < len(pattern2):
                if any(pattern1 == pattern2[j:j+len(pattern1)] for j in range(len(pattern2) - len(pattern1) + 1)):
                    filtered_patterns.discard(pattern1)
                    break

    return {pattern: repeated_patterns[pattern] for pattern in filtered_patterns}

def get_filtered_patterns(data_list, direction='forward'):
    all_repeated_patterns = defaultdict(int)
    
    if direction == 'forward':
        for pattern_length in range(9, 20):
            print(f"Checking forward patterns of length {pattern_length}:")
            repeated_patterns = find_repeated_patterns(data_list, pattern_length)
            for pattern, count in repeated_patterns.items():
                if count > 1:
                    all_repeated_patterns[pattern] = count
                    print(f'Pattern {pattern} occurs {count} times.')
    elif direction == 'backward':
        for pattern_length in range(8, 19):
            print(f"Checking backward patterns of length {pattern_length}:")
            repeated_patterns = find_repeated_patterns(data_list, pattern_length)
            for pattern, count in repeated_patterns.items():
                if count > 1:
                    all_repeated_patterns[pattern] = count
                    print(f'Pattern {pattern} occurs {count} times.')
    
    filtered_patterns = filter_subpatterns(all_repeated_patterns)
    
    return filtered_patterns

def merge_and_filter_patterns(patterns1, patterns2):
    merged_patterns = patterns1.copy()
    for pattern, count in patterns2.items():
        if pattern in merged_patterns:
            merged_patterns[pattern] += count
        else:
            merged_patterns[pattern] = count
    return merged_patterns


