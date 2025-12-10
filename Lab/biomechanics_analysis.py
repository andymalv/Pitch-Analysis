import os
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from scipy import signal


# %%
# @dataclass
# class pd.DataFrame:
#     x: List[float]
#     y: List[float]
#     z: List[float]
#     velo: List[float]
#     acc: List[float]
#     theta: List[float]
#     omega: List[float]
#     alpha: List[float]


@dataclass
class Pitch:
    # positions: pd.DataFrame
    time_stamps: List[float]
    # biomechanics_metrics: List[pd.DataFrame]
    timing_metrics: List[float]
    rear_ankle: pd.DataFrame
    read_knee: pd.DataFrame
    rear_hip: pd.DataFrame
    elbow: pd.DataFrame
    hand: pd.DataFrame
    shoulder: pd.DataFrame
    wrist: pd.DataFrame
    lead_ankle: pd.DataFrame
    lead_knee: pd.DataFrame
    lead_hip: pd.DataFrame
    glove_elbow: pd.DataFrame
    glove_han: pd.DataFrame
    glove_shoulder: pd.DataFrame
    glove_wrist: pd.DataFrame
    thorax_ap: pd.DataFrame
    thorax_dist: pd.DataFrame
    thorax_prox: pd.DataFrame
    CoM: pd.DataFrame


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
        # pitch = Pitch(positions, time_stamps, [], timing_metrics)
        pitch = Pitch
        pitch = pass_to_struct(pitch, positions, time_stamps, timing_metrics)

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
def parse_joint_data(data: List[pd.DataFrame]) -> List[pd.DataFrame]:
    joints = data.columns
    last_joint = joints[0][:-2]
    joint_data = pd.DataFrame()
    positions: List[pd.DataFrame] = []
    for joint in joints:
        this_joint = joint[:-2]
        if this_joint != last_joint:
            joint_data.columns = [
                # col.replace("_jc_", "") for col in joint_data.columns
                col.replace(last_joint + "_", "")
                for col in joint_data.columns
            ]
            positions.append(joint_data)

            joint_data = pd.DataFrame()
            last_joint = this_joint
            joint_data = pd.concat([joint_data, data[joint]], axis=1)
        else:
            joint_data = pd.concat([joint_data, data[joint]], axis=1)

            # b/c it won't append to positions b/c it's at the end
            if this_joint == "centerofmass" and np.shape(joint_data)[1] == 3:
                joint_data.columns = [
                    # col.replace("_jc_", "") for col in joint_data.columns
                    col.replace(last_joint + "_", "")
                    for col in joint_data.columns
                ]
                positions.append(joint_data)

    return positions


def pass_to_struct(
    pitch: Pitch,
    positions: List[pd.DataFrame],
    time_stamps: List[float],
    timing_metrics: List[float],
) -> Pitch:
    pitch.rear_ankle = positions[0]
    pitch.rear_hip = positions[1]
    pitch.elbow = positions[2]
    pitch.hand = positions[3]
    pitch.rear_knee = positions[4]
    pitch.shoulder = positions[5]
    pitch.wrist = positions[6]
    pitch.lead_ankle = positions[7]
    pitch.lead_hip = positions[8]
    pitch.glove_elbow = positions[9]
    pitch.glove_hand = positions[10]
    pitch.lead_knee = positions[11]
    pitch.glove_shoulder = positions[12]
    pitch.glove_wrist = positions[13]
    pitch.thorax_ap = positions[14]
    pitch.throax_dist = positions[15]
    pitch.thorax_prox = positions[16]
    pitch.CoM = positions[17]

    pitch.time_stamps = time_stamps
    pitch.timing_metrics = timing_metrics

    return pitch


def get_joint_group(joint: str) -> List[str]:
    match joint.lower():
        case "lead_knee":
            proximal = "lead_hip"
            distal = "lead_ankle"
        case "elbow":
            proximal = "shoulder"
            distal = "wrist"
        case "shoulder":
            proximal = "thorax_prox"
            distal = "elbow"
        case _:
            print(f"Joint group not available for {joint}")

    joint_group = [proximal, joint, distal]

    return joint_group


def get_framerate(pitch: Pitch) -> float:
    first = pitch.time_stamps[0]
    last = pitch.time_stamps[-1]

    framerate = (last - first) / np.size(pitch.time_stamps)

    return framerate


def get_joint_angle(
    proximal=pd.DataFrame, joint=pd.DataFrame, distal=pd.DataFrame
) -> pd.DataFrame:
    num_frames = np.shape(joint)[0]
    theta = np.zeros([num_frames])

    proximal_segment = proximal - joint
    distal_segment = joint - distal

    for i in range(num_frames):
        proximal_vector = proximal_segment.iloc[i, :]
        distal_vector = distal_segment.iloc[i, :]

        theta[i] = np.atan2(
            np.linalg.norm(np.cross(proximal_vector, distal_vector)),
            np.dot(proximal_vector, distal_vector),
        )

    theta = np.rad2deg(theta)

    return theta


def get_elbow_angle(pitch: Pitch) -> pd.DataFrame:
    joint_group = get_joint_group("elbow")
