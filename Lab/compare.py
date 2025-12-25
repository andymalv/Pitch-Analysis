import os
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

# import biomechanics_analysis as biomech
import gold_standard as gold


# %%
def load_data(path: Path) -> List[gold.Session]:
    # path = Path(path)

    df = []
    sessions = os.listdir(path)
    for session in sessions:
        this = load_session(path, session)
        df.append(this)

    return df


def load_session(path: Path, session_id: str) -> gold.Session:
    # session_dir = path / subdir / session_id
    session_dir = path / session_id

    pitches = []
    num_pitches = len(os.listdir(session_dir))
    for i in range(num_pitches):
        pitch_dir = session_dir / f"pitch_{i + 1}"

        pitch_data = load_pitch(pitch_dir)

        # pitches.append(gold.Pitch(**pitch_data))
        pitches.append(
            gold.Pitch(
                pitch_data["rear_ankle"],
                pitch_data["elbow"],
                pitch_data["rear_hip"],
                pitch_data["rear_knee"],
                pitch_data["shoulder"],
                pitch_data["wrist"],
                pitch_data["pelvis"],
                pitch_data["lead_ankle"],
                pitch_data["glove_elbow"],
                pitch_data["lead_hip"],
                pitch_data["lead_knee"],
                pitch_data["glove_shoulder"],
                pitch_data["glove_wrist"],
                pitch_data["torso"],
            )
        )

    session = gold.Session(pitches=pitches, id=session_id)

    return session


def load_pitch(dir: Path) -> dict:
    pitch_data = {}
    for file in dir.glob("*.parquet"):
        joint = file.name.replace(".parquet", "")
        df = pd.read_parquet(file)

        pitch_data[joint] = df

    return pitch_data


# %%
def main():
    gold = load_data(Path("Driveline/gold"))
    mine = load_data(Path("Driveline/raw"))


if __name__ == "__main__":
    main()
