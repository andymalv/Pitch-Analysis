from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd


# %%
@dataclass
class Pitch:
    time_stamps: List[float]
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
    glove_hand: pd.DataFrame
    glove_shoulder: pd.DataFrame
    glove_wrist: pd.DataFrame
    thorax_ap: pd.DataFrame
    thorax_dist: pd.DataFrame
    thorax_prox: pd.DataFrame
    CoM: pd.DataFrame
    trunk: pd.DataFrame
    pelivs: pd.DataFrame


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


def parse_joint_data(data: List[pd.DataFrame]) -> List[pd.DataFrame]:
    joints = data.columns
    last_joint = joints[0][:-2]
    joint_data = pd.DataFrame()
    positions: List[pd.DataFrame] = []
    for joint in joints:
        this_joint = joint[:-2]
        if this_joint != last_joint:
            joint_data.columns = [
                col.replace(last_joint + "_", "") for col in joint_data.columns
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
                    col.replace(last_joint + "_", "") for col in joint_data.columns
                ]
                positions.append(joint_data)

    return positions


def pass_to_struct(
    pitch: Pitch,
    positions: List[pd.DataFrame],
    time_stamps: List[float],
    timing_metrics: List[float],
):
    pitch.rear_ankle = positions[0].reset_index(drop=True)
    pitch.rear_hip = positions[1].reset_index(drop=True)
    pitch.elbow = positions[2].reset_index(drop=True)
    pitch.hand = positions[3].reset_index(drop=True)
    pitch.rear_knee = positions[4].reset_index(drop=True)
    pitch.shoulder = positions[5].reset_index(drop=True)
    pitch.wrist = positions[6].reset_index(drop=True)
    pitch.lead_ankle = positions[7].reset_index(drop=True)
    pitch.lead_hip = positions[8].reset_index(drop=True)
    pitch.glove_elbow = positions[9].reset_index(drop=True)
    pitch.glove_hand = positions[10].reset_index(drop=True)
    pitch.lead_knee = positions[11].reset_index(drop=True)
    pitch.glove_shoulder = positions[12].reset_index(drop=True)
    pitch.glove_wrist = positions[13].reset_index(drop=True)
    pitch.thorax_ap = positions[14].reset_index(drop=True)
    pitch.throax_dist = positions[15].reset_index(drop=True)
    pitch.thorax_prox = positions[16].reset_index(drop=True)
    pitch.CoM = positions[17].reset_index(drop=True)

    pitch.time_stamps = time_stamps.reset_index(drop=True)
    pitch.timing_metrics = timing_metrics.reset_index(drop=True)

    return


# %%
def get_framerate(pitch: Pitch) -> float:
    first = pitch.time_stamps[0]
    last = pitch.time_stamps.iloc[-1]

    framerate = (last - first) / np.size(pitch.time_stamps)

    return framerate


# %%
def calculate_joint_angle(
    proximal: np.ndarray, joint: np.ndarray, distal: np.ndarray
) -> np.ndarray:
    num_frames = np.shape(joint)[0]
    theta = np.zeros([num_frames])

    proximal_segment = proximal - joint
    distal_segment = joint - distal

    for i in range(num_frames):
        proximal_vector = proximal_segment[i, :]
        distal_vector = distal_segment[i, :]

        theta[i] = np.atan2(
            np.linalg.norm(np.cross(proximal_vector, distal_vector)),
            np.dot(proximal_vector, distal_vector),
        )

    theta = np.rad2deg(theta)

    return theta


def get_angle_metrics(
    proximal: pd.DataFrame, joint: pd.DataFrame, distal: pd.DataFrame, dt: float
) -> pd.DataFrame:
    proximal = np.array(proximal[["x", "y", "z"]])
    joint = np.array(joint[["x", "y", "z"]])
    distal = np.array(distal[["x", "y", "z"]])

    theta = calculate_joint_angle(proximal, joint, distal)
    omega = np.gradient(theta, dt, axis=0)
    alpha = np.gradient(omega, dt, axis=0)

    result = pd.DataFrame([theta, omega, alpha]).T
    result.columns = ["theta", "omega", "alpha"]

    return result


# %%
def calculate_segment_rotation(
    point1: np.ndarray, point2: np.ndarray, axis_of_rotation: str
) -> np.ndarray:
    match axis_of_rotation.lower():
        case "x":
            rotation_axis = [1, 0, 0]
        case "y":
            rotation_axis = [0, 1, 0]
        case "z":
            rotation_axis = [0, 0, 1]
        case _:
            print(f"Error: invalid axis input: {axis_of_rotation}")

    num_frames = np.shape(point1)[0]
    theta = np.zeros(num_frames)

    start_axis1 = np.absolute(point1[0, :] - point2[0, :])
    start_axis2 = np.cross(rotation_axis, start_axis1)
    start_axis2 = start_axis2 / np.linalg.norm(start_axis2)

    for i in range(1, num_frames):
        axis1 = np.absolute(point1[i, :] - point2[i, :])
        axis2 = np.cross(rotation_axis, axis1)
        current_axis2 = axis2 / np.linalg.norm(axis2)

        dot_product = np.dot(start_axis2[0:1], current_axis2[0:1])
        cross_product = (
            start_axis2[0] * current_axis2[1] - start_axis2[1] * current_axis2[0]
        )
        d_theta = np.atan2(cross_product, dot_product)

        theta[i] = theta[i - 1] + d_theta
        start_axis2 = current_axis2

    theta = np.rad2deg(theta)

    return theta


def get_rotation_metrics(
    lead: pd.DataFrame, rear: pd.DataFrame, axis_of_rotation: str, dt: float
) -> pd.DataFrame:
    lead = np.array(lead[["x", "y", "z"]])
    rear = np.array(rear[["x", "y", "z"]])

    theta = calculate_segment_rotation(lead, rear, axis_of_rotation)
    omega = np.gradient(theta, dt, axis=0)
    alpha = np.gradient(omega, dt, axis=0)

    result = pd.DataFrame([theta, omega, alpha]).T
    result.columns = ["theta", "omega", "alpha"]

    return result


# %%
def get_metrics(pitch: Pitch):
    dt = get_framerate(pitch)

    pitch.lead_knee = pd.concat(
        [
            pitch.lead_knee,
            get_angle_metrics(pitch.lead_hip, pitch.lead_knee, pitch.lead_ankle, dt),
        ],
        axis=1,
    )

    pitch.pelvis = get_rotation_metrics(pitch.lead_hip, pitch.rear_hip, "z", dt)
