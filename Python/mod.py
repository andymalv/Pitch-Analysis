# %%
import os
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd


# %%
@dataclass
class Pitch:
    position: List[pd.DataFrame]
    timeStamp: List[str]
    metrics: List[pd.DataFrame]


@dataclass
class Player:
    name: str
    pitches: List[Pitch]
    metrics: List[pd.DataFrame]


# %%
def get_data(directory):
    name = directory[3:]
    print(f"Gathering data for", name, "...\n")

    files = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            files.append(os.path.join(directory, file))

    num_files = np.size(files)
    pitches = []

    for file in range(num_files):
        try:
            file_path = files[file]
            data = pd.read_json(file_path)
        except:
            print(f"Error reading file: ", file_path)

        num_frames = np.size(data["skeletalData"]["frames"])
        time_stamp = []
        positions = []

        for frame in range(num_frames):
            time_stamp.append(data["skeletalData"]["frames"][frame]["timeStamp"])
            blah = pd.DataFrame(
                data["skeletalData"]["frames"][frame]["positions"][0]["joints"]
            )
            positions.append(blah)

        pitch = Pitch(positions, time_stamp, [])
        pitches.append(pitch)

    player = Player(name, pitches, [])

    return player
