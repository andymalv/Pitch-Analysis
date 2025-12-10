import os
from dataclasses import dataclass, fields
from typing import List

import numpy as np
import pandas as pd
from scipy import signal


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
    glove_han: pd.DataFrame
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
) -> Pitch:
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

    return pitch


# %%
def get_framerate(pitch: Pitch) -> float:
    first = pitch.time_stamps[0]
    last = pitch.time_stamps.iloc[-1]

    framerate = (last - first) / np.size(pitch.time_stamps)

    return framerate


def get_joint_angle(
    proximal=pd.DataFrame, joint=pd.DataFrame, distal=pd.DataFrame
) -> pd.DataFrame:
    num_frames = np.shape(joint)[0]
    theta = np.zeros([num_frames])

    proximal_segment = proximal.iloc[:, :3] - joint.iloc[:, :3]
    distal_segment = joint.iloc[:, :3] - distal.iloc[:, :3]

    for i in range(num_frames):
        proximal_vector = proximal_segment.iloc[i, :]
        distal_vector = distal_segment.iloc[i, :]

        theta[i] = np.atan2(
            np.linalg.norm(np.cross(proximal_vector, distal_vector)),
            np.dot(proximal_vector, distal_vector),
        )

    theta = np.rad2deg(theta)
    theta = pd.DataFrame(theta)
    theta.columns = ["theta"]

    return theta


def get_elbow_angle(pitch: Pitch):
    shoulder = pitch.shoulder
    elbow = pitch.elbow
    wrist = pitch.wrist

    theta = get_joint_angle(shoulder, elbow, wrist)

    pitch.elbow = pd.concat([pitch.elbow, pd.Series(theta)], axis=1)


def get_lead_knee_angle(pitch: Pitch):
    hip = pitch.lead_hip
    knee = pitch.lead_knee
    ankle = pitch.lead_ankle

    theta = get_joint_angle(hip, knee, ankle)

    pitch.lead_knee = pd.concat([pitch.lead_knee, pd.Series(theta)], axis=1)


def get_shoulder_rotation(pitch: Pitch):
    thorax = pitch.thorax_prox
    shoulder = pitch.shoulder
    elbow = pitch.elbow

    theta = get_joint_angle(thorax, shoulder, elbow)

    pitch.shoulder = pd.concat([pitch.shoulder, pd.Series(theta)], axis=1)


# %%
def get_segment_rotation(
    point1: pd.DataFrame, point2: pd.DataFrame, axis_of_rotation: str
) -> pd.DataFrame:
    match axis_of_rotation.lower():
        case "x":
            rotation_axis = [1, 0, 0]
        case "y":
            rotation_axis = [0, 1, 0]
        case "z":
            rotation_axis = [0, 0, 1]
        case _:
            print(f"Error: invalid axis input: {axis_of_rotation}")

    point1 = np.array(point1)
    point2 = np.array(point2)

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
    theta = pd.DataFrame(theta)
    theta.columns = ["theta"]

    return theta


def get_pelvis_rotation(pitch: Pitch):
    lead_hip = pitch.lead_hip
    rear_hip = pitch.rear_hip

    theta = get_segment_rotation(lead_hip, rear_hip, "z")
    # theta.columns = ["theta"]

    pitch.pelvis = theta


def get_trunk_rotation(pitch: Pitch):
    lead_shoulder = pitch.glove_shoulder
    rear_shoulder = pitch.shoulder[["x", "y", "z"]]

    theta = get_segment_rotation(lead_shoulder, rear_shoulder, "z")
    # theta.columns = ["theta"]

    pitch.trunk = theta


# %%
def get_gradient(data: pd.DataFrame, dt: float) -> pd.DataFrame:
    # if np.shape(data)[1] == 1:
    #     gradient = np.gradient(data, dt)
    # else:
    #     gradient = np.gradient(data.iloc[:, -1], dt)
    # gradient = np.gradient(data.iloc[:, -1], dt)
    gradient = pd.DataFrame(np.gradient(data, dt))

    variable = data.columns[0]
    match variable:
        case "theta":
            col = "omega"
        case "omega":
            col = "alpha"
        case "v":
            col = "a"

    gradient.columns = [col]

    # out = pd.concat([data, pd.Series(gradient)], axis=1)

    return gradient


# %%
def get_metrics(pitch: Pitch):
    pitch.elbow = pd.concat(
        [pitch.elbow, get_joint_angle(pitch.shoulder, pitch.elbow, pitch.wrist)], axis=1
    )
    pitch.elbow = pd.concat([pitch.elbow, get_gradient(pitch.elbow[["theta"]])], axis=1)
    pitch.lead_knee = pd.concat(
        [
            pitch.lead_knee,
            get_joint_angle(pitch.lead_hip, pitch.lead_knee, pitch.lead_ankle),
        ],
        axis=1,
    )
    pitch.shoulder = pd.concat(
        [
            pitch.shoulder,
            get_joint_angle(pitch.thorax_prox, pitch.shoulder, pitch.elbow),
        ],
        axis=1,
    )

    pitch.pelvis = get_segment_rotation(pitch.lead_hip, pitch.rear_hip, "z")
    pitch.trunk = get_segment_rotation(pitch.glove_shoulder, pitch.shoulder, "z")
