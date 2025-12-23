from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from biomechanics_analysis import save_as_parquet

# %%
@dataclass
class Pitch:
    rear_ankle: pd.DataFrame
    elbow: pd.DataFrame
    rear_hip: pd.DataFrame
    rear_knee: pd.DataFrame
    shoulder: pd.DataFrame
    wrist: pd.DataFrame
    pelvis: pd.DataFrame
    lead_ankle: pd.DataFrame
    glove_elbow: pd.DataFrame
    lead_hip: pd.DataFrame
    lead_knee: pd.DataFrame
    glove_shoulder: pd.DataFrame
    glove_wrist: pd.DataFrame
    torso: pd.DataFrame
    # torso_pelvis: pd.DataFrame # need to figure out why this isn't being passed


@dataclass
class Session:
    pitches: List[Pitch]
    id: str


# %%
def get_data(path: str) -> List[Session]:
    with open(path, "r") as file:
        df = pd.read_csv(file).groupby(["session_pitch"])
    pitch_ids = list(df.groups.keys())
    pitches: List[Pitch] = []
    sessions: List[Session] = []
    cut_cols = [
        "session_pitch",
        "time",
        "pkh_time",
        "fp_10_time",
        "fp_100_time",
        "MER_time",
        "BR_time",
        "MIR_time",
    ]

    session_id = str(pitch_ids[0])[:-2]
    for pitch_id in pitch_ids:
        data = df.get_group((pitch_id,))
        angles = pd.DataFrame(data.drop(columns=cut_cols).reset_index(drop=True))
        angles = parse_joint_angles(angles)
        pitch = pass_to_struct(angles)

        if str(pitch_id)[:-2] == session_id:
            pitches.append(pitch)
            pitch = None
        else:
            session = Session(pitches, session_id)
            sessions.append(session)

            pitches = []
            session_id = str(pitch_id)[:-2]
            pitches.append(pitch)
            pitch = None

    return sessions


def parse_joint_angles(data: pd.DataFrame) -> List[pd.DataFrame]:
    joints = data.columns
    last_joint = joints[0][:-2]
    joint_data = pd.DataFrame()
    angles: List[pd.DataFrame] = []
    for joint in joints:
        this_joint = joint[:-2]
        if this_joint != last_joint:
            joint_data.columns = [
                col.replace(last_joint, "theta") for col in joint_data.columns
            ]
            angles.append(joint_data)

            joint_data = pd.DataFrame()
            last_joint = this_joint
            joint_data = pd.concat([joint_data, data[joint]], axis=1)
        else:
            joint_data = pd.concat([joint_data, data[joint]], axis=1)

            # b/c it won't append to angles b/c it's at the end
            if this_joint == "torso_pelvis" and np.shape(joint_data)[1] == 3:
                joint_data.columns = [
                    col.replace(last_joint, "theta") for col in joint_data.columns
                ]
                angles.append(joint_data)

    return angles


def pass_to_struct(
    angles: List[pd.DataFrame],
) -> Pitch:
    pitch = Pitch(
        angles[0],
        angles[1],
        angles[2],
        angles[3],
        angles[4],
        angles[5],
        angles[6],
        angles[7],
        angles[8],
        angles[9],
        angles[10],
        angles[11],
        angles[12],
        angles[13],
        # angles[14], # need to figure out why this isn't getting passed
    )

    return pitch

# %%
def main():
    path = "joint_angles.csv"
    df = get_data(path)
    save_as_parquet(df, "gold")

if __name__ == "__main__":
    main()
