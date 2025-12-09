import os
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from scipy import signal


# %%
@dataclass
class Pitch:
    positions: pd.DataFrame
    time_stamps: List[float]
    biomechanics_metrics: List[pd.DataFrame]
    timing_metrics: List[float]


@dataclass
class Session:
    pitches: List[Pitch]
    id: str


# %%
def get_data(file: str) -> List[Session]:
    df = pd.read_csv(file).groupby(["session_pitch"])
    pitch_ids = df.groups.keys()
    pitches: List[Pitch] = []
    sessions: List[Session] = []
    timing_cols = [
        "pkh_time",
        "fp_10_time",
        "fp_100_time",
        "MER_time",
        "BR_time",
        "MIR_time",
    ]

    session_id = list(pitch_ids)[0][:-2]
    for pitch_id in pitch_ids:
        data = df.get_group((pitch_id,))
        time_stamps = data["time"]
        timing_metrics = data[timing_cols].iloc[0, :]
        positions = data.drop(columns=timing_cols).iloc[:, 2:]
        positions = parse_joint_data(positions)
        pitch = Pitch(positions, time_stamps, [], timing_metrics)

        if pitch_id[:-2] == session_id:
            pitches.append(pitch)
        else:
            session = Session(pitches, session_id)
            sessions.append(session)

            pitches = []
            session_id = pitch_id[:-2]
            pitches.append(pitch)

    return sessions


# %%
def parse_joint_data(data: pd.DataFrame) -> List[pd.DataFrame]:
    measures = data.columns
    last_measure = measures[0][:-2]
    measure_data = pd.DataFrame()
    positions: List[pd.DataFrame] = []
    for measure in measures:
        this_measure = measure[:-2]
        if this_measure != last_measure:
            measure_data.columns = [
                col.replace("_jc", "") for col in measure_data.columns
            ]
            positions.append(measure_data)

            measure_data = pd.DataFrame()
            last_measure = this_measure
            measure_data = pd.concat([measure_data, data[measure]], axis=1)
        else:
            measure_data = pd.concat([measure_data, data[measure]], axis=1)

            # b/c it won't append to positions b/c it's at the end
            if this_measure == "centerofmass" and np.shape(measure_data)[1] == 3:
                positions.append(measure_data)

    return positions
