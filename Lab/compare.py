import os
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

import biomechanics_analysis as biomech
import gold_standard as gold


# %%
def load_gold():
    path = Path("Driveline/gold")

    df = []
    sessions = os.listdir(path)
    for session in sessions:
        this = load_session(path, session)
        df.append(this)

    return df


def load_session(path: Path, session_id: str):
    # session_dir = path / subdir / session_id
    session_dir = path / session_id

    pitches = []
    num_pitches = len(os.listdir(session_dir))
    for i in range(num_pitches):
        pitch_dir = session_dir / f"pitch{i + 1}"

        pitch_data = {}
        for file in pitch_dir.glob("*.parquet"):
            joint = file.name
            df = pd.read_parquet(file)

            pitch_data[joint] = df

        pitches.append(gold.Pitch(**pitch_data))

    session = gold.Session(pitches=pitches, id=session_id)

    return session
