"""
This module contains functions to get the timing attributes for multiple pieces
by averaging the timing attributes for each beat of a meter.

@Author: Joris Monnet
@Date: 2024-03-26
"""
from src.timing_for_one_piece import get_average_timing_one_piece


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


if __name__ == "__main__":
    path = "data/annotations"
    print(get_phrase_boundaries(path))
