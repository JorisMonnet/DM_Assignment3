"""
This module contains functions to get the timing attributes for multiple pieces
by averaging the timing attributes for each beat of a meter.

@Author: Joris Monnet
@Date: 2024-03-26
"""
from src.timing_for_one_piece import get_average_timing_one_piece
import music21
from music21 import converter, meter, stream
import matplotlib.pyplot as plt


def get_tempo_map_db(symbolic_to_performed_times: dict) -> dict and list[int]:
    """
    Get the tempo map from the symbolic to the performed times
    Compute the tempo ratio for each beat
    :param symbolic_to_performed_times:
    :return: dict
    """
    result = {}
    indexes = []
    for i in range(len(symbolic_to_performed_times) - 1):
        beat_type = symbolic_to_performed_times[i]["performed"]["beat_type"]
        if beat_type == "db":
            indexes.append(i)
        onset = symbolic_to_performed_times[i]["performed"]["onset"]
        next_onset = symbolic_to_performed_times[i + 1]["performed"]["onset"]
        duration_performed = float(next_onset) - float(onset)
        onset_symbolic = symbolic_to_performed_times[i]["symbolic"]["onset"]
        next_onset_symbolic = symbolic_to_performed_times[i + 1]["symbolic"]["onset"]
        duration_symbolic = float(next_onset_symbolic) - float(onset_symbolic)
        result[i] = duration_symbolic / duration_performed
    if symbolic_to_performed_times[len(symbolic_to_performed_times) - 1]["performed"]["beat_type"] == "db":
        indexes.append(len(symbolic_to_performed_times) - 1)
    return result, indexes


def get_phrase_boundaries(path: str):
    average = get_average_timing_one_piece(path)
    tempo_map, indexes_db = get_tempo_map_db(average)

    phrase_boundaries = []
    for i in range(len(tempo_map)):
        if i in indexes_db:
            current_index = indexes_db.index(i)
            if current_index == 0:
                phrase_boundaries.append(i)
                continue
            last_db = indexes_db[current_index - 1]
            if current_index == len(indexes_db) - 1:
                phrase_boundaries.append(i)
                continue
            next_db = indexes_db[current_index + 1]
            last_measure = list(tempo_map.values())[last_db:i]
            next_measure = list(tempo_map.values())[i:next_db]
            # -1 if the tempo is decreasing, 1 if the tempo is increasing inside the measure
            last_measure_change = 0
            for j in range(len(last_measure) - 1):
                last_measure_change += last_measure[j + 1] - last_measure[j]
            last_measure_change = last_measure_change / len(last_measure)
            next_measure_change = 0
            for j in range(len(next_measure) - 1):
                next_measure_change += next_measure[j + 1] - next_measure[j]
            next_measure_change = next_measure_change / len(next_measure)
            # Check if sign of tempo change is different
            if last_measure_change * next_measure_change < 0:
                # Phrase boundary if the tempo is increasing inside the new measure
                if next_measure_change > 0:
                    phrase_boundaries.append(i)
    boundaries_time = get_time_of_phrase_boundaries(phrase_boundaries, average)
    return phrase_boundaries, boundaries_time


def get_time_of_phrase_boundaries(phrase_boundaries: list[int], average: dict):
    boundaries_time = []
    for boundary in phrase_boundaries:
        boundaries_time.append(float(average[boundary]["performed"]["onset"]))
    return boundaries_time


def get_times_volumes_measures(midi_file_path):
    """
    Extracts the start times, velocity values (volume), and measure numbers of each note from a MIDI file.

    Parameters:
    midi_file_path (str): The path to the input MIDI file.
    
    Returns:
    times (list of float): A list containing the start times of all the notes in the MIDI file.
    volumes (list of int): A list containing the velocity values of all the notes in the MIDI file.
    measures (list of int): A list containing the measure numbers of all the notes in the MIDI file.
    """
    # MIDIファイルを読み込む
    midi_data = music21.converter.parse(midi_file_path)
    
    # 開始時間、音量、小節番号のリストを保存するリスト
    times = []
    volumes = []
    measures = []

    # MIDIパートを処理する
    for part in midi_data.parts:
        for element in part.flatten().notesAndRests:
            if isinstance(element, music21.note.Note):
                start_time = element.offset
                velocity = element.volume.velocity
                measure_number = element.measureNumber
                times.append(start_time)
                volumes.append(velocity)
                measures.append(measure_number)
            elif isinstance(element, music21.chord.Chord):
                start_time = element.offset
                velocity = element.volume.velocity
                measure_number = element.measureNumber
                times.append(start_time)
                volumes.append(velocity)
                measures.append(measure_number)

    return times, volumes, measures

def get_scaled_differences_in_volumes(list_volume_performed):
    """
    Calculates the squared differences in volume between consecutive elements
    in the input list, and scales these differences to the range [0, 1].

    Parameters:
    list_volume_performed (list of int or float): A list of volume values.

    Returns:
    list_volume_differences_scaled (list of float): A list of scaled squared differences in volume, 
                                                     where the values are normalized to the range [0, 1].
    """
    list_volume_differences = [abs(list_volume_performed[i] - list_volume_performed[i+1]) **2
                               for i in range(len(list_volume_performed) - 1)]
    max_difference = max(list_volume_differences)
    list_volume_differences_scaled = [x / max_difference for x in list_volume_differences]
    return list_volume_differences_scaled


def get_times_threshold(list_time, list_volume_differences_scaled, threshold):
    for i in range(len(list_time)):
        indices_above_threshold = [index for index, value in enumerate(list_volume_differences_scaled) if value > threshold]
        times_above_threshold = [list_time[index] for index in indices_above_threshold]
    return times_above_threshold


def offset_to_seconds(offset, tempo):
    quarter_note_duration = 60 / tempo
    return offset * quarter_note_duration

def plot_volume_and_possibilities(list_volume_performed, filtered_data, list_time):
    list_time_second = [offset_to_seconds(x, tempo) for x in list_time]
    list_filtered_second = [offset_to_seconds(x, tempo) for x in filtered_data]
    list_volume_differences_scaled = get_scaled_differences_in_volumes(list_volume_performed)
    plt.figure(figsize=(10, 6))
    plt.plot(list_time_second[:-2], list_volume_differences_scaled, linestyle='-', color='b')
    for x in list_filtered_second:
        plt.axvline(x=x, color='y', linestyle='--')
    plt.xlabel('Time[s]')
    plt.ylabel('Volume Differences Scaled ')
    plt.title('Volume Differences Scaled')
    plt.show()



if __name__ == "__main__":
    path = "data/annotations"
    print(get_phrase_boundaries(path))