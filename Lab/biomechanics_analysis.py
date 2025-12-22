from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.signal import resample


# %%
@dataclass
class Pitch:
    time_stamps: pd.Series
    timing_metrics: pd.DataFrame
    rear_ankle: pd.DataFrame
    rear_hip: pd.DataFrame
    elbow: pd.DataFrame
    hand: pd.DataFrame
    rear_knee: pd.DataFrame
    shoulder: pd.DataFrame
    wrist: pd.DataFrame
    lead_ankle: pd.DataFrame
    lead_hip: pd.DataFrame
    glove_elbow: pd.DataFrame
    glove_hand: pd.DataFrame
    lead_knee: pd.DataFrame
    glove_shoulder: pd.DataFrame
    glove_wrist: pd.DataFrame
    thorax_ap: pd.DataFrame
    thorax_dist: pd.DataFrame
    thorax_prox: pd.DataFrame
    CoM: pd.DataFrame
    torso: pd.DataFrame
    pelvis: pd.DataFrame


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
    timing_cols = [
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
        time_stamps = data["time"].reset_index(drop=True)
        timing_metrics = data[timing_cols].iloc[0, :].T
        timing_metrics.columns = timing_cols
        positions = data.drop(columns=timing_cols).iloc[:, 2:].reset_index(drop=True)
        positions = parse_joint_data(positions)
        pitch = pass_to_struct(positions, time_stamps, timing_metrics)

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


def parse_joint_data(data: pd.DataFrame) -> List[pd.DataFrame]:
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
    positions: List[pd.DataFrame],
    time_stamps: pd.Series,
    timing_metrics: pd.DataFrame,
) -> Pitch:
    pitch = Pitch(
        time_stamps,
        timing_metrics,
        positions[0],
        positions[1],
        positions[2],
        positions[3],
        positions[4],
        positions[5],
        positions[6],
        positions[7],
        positions[8],
        positions[9],
        positions[10],
        positions[11],
        positions[12],
        positions[13],
        positions[14],
        positions[15],
        positions[16],
        positions[17],
        pd.DataFrame(),
        pd.DataFrame(),
    )

    return pitch


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

    proximal_segment = proximal[:, 0:3] - joint[:, 0:3]
    distal_segment = joint[:, 0:3] - distal[:, 0:3]

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
    theta = calculate_joint_angle(
        proximal.to_numpy(), joint.to_numpy(), distal.to_numpy()
    )
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
    theta = calculate_segment_rotation(
        lead.to_numpy(), rear.to_numpy(), axis_of_rotation
    )
    omega = np.gradient(theta, dt, axis=0)
    alpha = np.gradient(omega, dt, axis=0)

    result = pd.DataFrame([theta, omega, alpha]).T
    result.columns = ["theta", "omega", "alpha"]

    return result


# %%
def calculate_metrics(pitch: Pitch) -> Pitch:
    dt = get_framerate(pitch)

    pitch.elbow = pd.concat(
        [
            pitch.elbow,
            get_angle_metrics(pitch.shoulder, pitch.elbow, pitch.wrist, dt),
        ],
        axis=1,
    )
    pitch.rear_knee = pd.concat(
        [
            pitch.rear_knee,
            get_angle_metrics(pitch.rear_hip, pitch.rear_knee, pitch.rear_ankle, dt),
        ],
        axis=1,
    )
    pitch.shoulder = pd.concat(
        [
            pitch.shoulder,
            get_angle_metrics(pitch.thorax_prox, pitch.shoulder, pitch.elbow, dt),
        ],
        axis=1,
    )
    pitch.wrist = pd.concat(
        [
            pitch.wrist,
            get_angle_metrics(pitch.elbow, pitch.wrist, pitch.hand, dt),
        ],
        axis=1,
    )
    pitch.glove_elbow = pd.concat(
        [
            pitch.glove_elbow,
            get_angle_metrics(
                pitch.glove_shoulder, pitch.glove_elbow, pitch.glove_wrist, dt
            ),
        ],
        axis=1,
    )
    pitch.lead_knee = pd.concat(
        [
            pitch.lead_knee,
            get_angle_metrics(pitch.lead_hip, pitch.lead_knee, pitch.lead_ankle, dt),
        ],
        axis=1,
    )
    pitch.glove_shoulder = pd.concat(
        [
            pitch.glove_shoulder,
            get_angle_metrics(
                pitch.thorax_dist, pitch.glove_shoulder, pitch.glove_elbow, dt
            ),
        ],
        axis=1,
    )
    pitch.glove_wrist = pd.concat(
        [
            pitch.glove_wrist,
            get_angle_metrics(
                pitch.glove_elbow, pitch.glove_wrist, pitch.glove_hand, dt
            ),
        ],
        axis=1,
    )
    pitch.torso = get_rotation_metrics(pitch.thorax_prox, pitch.thorax_dist, "z", dt)
    pitch.pelvis = get_rotation_metrics(pitch.lead_hip, pitch.rear_hip, "z", dt)

    return pitch


def get_metrics(df: List[Session]) -> List[Session]:
    num_sessions = len(df)

    for session in range(num_sessions):
        num_pitches = len(df[session].pitches)

        for pitch in range(num_pitches):
            this_pitch = df[session].pitches[pitch]
            this_pitch = calculate_metrics(this_pitch)

    return df


def save_as_parquet(df: List[Session]):
    data_dir = Path("Driveline")

    for session in df:
        session_dir = data_dir / session.id
        session_dir.mkdir(parents=True, exist_ok=True)

        for i, pitch in enumerate(session.pitches):
            pitch_dir = session_dir / f"pitch_{i + 1}"
            pitch_dir.mkdir(exist_ok=True)

            for field, value in vars(pitch).items():
                if isinstance(value, pd.Series):
                    pd.DataFrame({field: value}).to_parquet(
                        pitch_dir / f"{field}.parquet"
                    )
                else:
                    # print(f"Session: {session}, Pitch {i + 1}, Joint: {field}")
                    value.to_parquet(pitch_dir / f"{field}.parquet")


# %%
def main():
    df = get_data("landmarks.csv")
    df = get_metrics(df)
    save_as_parquet(df)


if __name__ == "__main__":
    main()
