# %%
import os
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd
from line_profiler import profile
from scipy import signal


# %%
@dataclass
class Pitch:
    positions: pd.DataFrame
    timeStamps: List[str]
    metrics: List[pd.DataFrame]


@dataclass
class Player:
    name: str
    pitches: List[Pitch]
    metrics: List[pd.DataFrame]


# %%
@profile
def get_data(directory: str) -> Player:
    name = directory[3:]
    print(f"Gathering data for {name}...\n")

    files: list[str] = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            files.append(os.path.join(directory, file))

    num_files = np.size(files)
    pitches: list[Pitch] = []

    for file in range(num_files):
        file_path = files[file]
        try:
            data = pd.read_json(file_path)
        except FileNotFoundError:
            print(f"File not found:  {file_path}")
        except pd.errors.JSONDecodeError:
            print(f"JSON decoding error in file: {file_path}")
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")

        frames = data["skeletalData"]["frames"]
        time_stamp = [str(frame["timeStamp"]) for frame in frames]
        positions = pd.json_normalize(
            frames, record_path=["positions", "joints"]
        ).set_index("id")

        pitch = Pitch(positions, time_stamp, [])
        pitches.append(pitch)

    player = Player(name, pitches, [])

    return player


def get_joint_id(joint: list[str] | str, side: str) -> list[int] | int:
    if isinstance(joint, str):
        joint = [joint]

    joint_lookup = {
        "nose": 0,
        "neck": 1,
        "eye_right": 15,
        "eye_left": 16,
        "shoulder_right": 2,
        "shoulder_left": 5,
        "elbow_right": 3,
        "elbow_left": 6,
        "wrist_right": 4,
        "wrist_left": 7,
        "thumb_right": 27,
        "thumb_left": 24,
        "pinky_right": 28,
        "pinky_left": 26,
        "hip_center": 8,
        "hip_right": 9,
        "hip_left": 12,
        "knee_right": 10,
        "knee_left": 13,
        "ankle_right": 11,
        "ankle_left": 14,
        "bigtoe_right": 22,
        "bigtoe_left": 19,
        "smalltoe_right": 23,
        "smalltoe_left": 20,
        "heel_right": 24,
        "heel_left": 21,
    }

    num_joints = np.size(joint)
    joint_id: list[int] = []

    for i in range(num_joints):
        try:
            if joint[i] == "nose" or joint[i] == "neck":
                this_joint = joint[i]
            else:
                this_joint = joint[i] + "_" + side

            joint_id.append(joint_lookup[this_joint])

        except KeyError:
            print(f"Joint {joint} and side {side} combination not found")
        except Exception:
            print("Error attempting to find joint grouping")

    return joint_id


@profile
def get_joint_data(pitch: Pitch, joint: int) -> pd.DataFrame:
    joint_data = pitch.positions.loc[joint].reset_index(drop=True)

    return joint_data


def get_throwing_hand(player: Player) -> str:
    right_id = get_joint_id("wrist", "right")
    left_id = get_joint_id("wrist", "left")

    right_data = get_joint_data(player.pitches[0], right_id)
    left_data = get_joint_data(player.pitches[0], left_id)

    side = ""
    try:
        if right_data.iloc[0, 1] > left_data.iloc[0, 1]:
            side = "right"
        elif left_data.iloc[0, 1] > right_data.iloc[0, 1]:
            side = "left"
    except IndexError:
        print(f"Could not determine pitching hand for {player.name} due to index error.")
    except ValueError:
        print(f"Could not determine pitching hand for {player.name} due to value error.")
    except Exception:
        print(f"Could not determine pitching hand for {player.name}")

    return side


def get_joint_group(joint: str) -> list[str]:
    extra = ""

    match joint.lower():
        case "elbow":
            proximal = "shoulder"
            distal = "wrist"
        case "shoulder":
            proximal = "neck"
            distal = "elbow"
            extra = "nose"
        case "knee":
            proximal = "hip"
            distal = "ankle"
        case _:
            print(f"Joint grouping not available for {joint}")

    if extra == "":
        joint_group = [proximal, joint, distal]
    else:
        joint_group = [proximal, joint, distal, extra]

    return joint_group


def get_framerate(pitch: Pitch) -> float:
    first = float(pitch.timeStamps[0][-10:-1])
    last = float(pitch.timeStamps[-1][-10:-1])

    if (last - first) < 0:
        last = 60 + last

    framerate = (last - first) / np.size(pitch.timeStamps)

    return framerate


@profile
def get_joint_angle(
    proximal_data: pd.DataFrame,
    joint_data: pd.DataFrame,
    distal_data: pd.DataFrame,
    extra_data=None,
) -> pd.DataFrame:
    num_frames = np.shape(joint_data)[0]

    distal_segment = joint_data - distal_data

    if extra_data is not None and np.size(extra_data) == np.size(joint_data):
        intermediate_segment = joint_data - proximal_data
        extra_segment = extra_data - proximal_data
        proximal_segment = np.cross(extra_segment, intermediate_segment)
        proximal_segment = pd.DataFrame(proximal_segment)
    else:
        proximal_segment = proximal_data - joint_data

    theta = np.zeros([num_frames])

    for i in range(num_frames):
        proximal_vector = proximal_segment.iloc[i, :]
        distal_vector = distal_segment.iloc[i, :]

        theta[i] = np.atan2(
            np.linalg.norm(np.cross(proximal_vector, distal_vector)),
            np.dot(proximal_vector, distal_vector),
        )

    theta = np.rad2deg(theta)

    return theta


def get_elbow_angle(pitch: Pitch, side: str) -> pd.DataFrame:
    joint_group = get_joint_group("elbow")
    joint_ids = get_joint_id(joint_group, side)
    shoulder_data = get_joint_data(pitch, joint_ids[0])
    elbow_data = get_joint_data(pitch, joint_ids[1])
    wrist_data = get_joint_data(pitch, joint_ids[2])

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 10
    b, a = signal.butter(2, cutoff_freq / nyquist_freq)

    shoulder_data_filtered = shoulder_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    elbow_data_filtered = elbow_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    wrist_data_filtered = wrist_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )

    theta = get_joint_angle(
        shoulder_data_filtered, elbow_data_filtered, wrist_data_filtered
    )

    return theta


def get_knee_angle(pitch: Pitch, side: str) -> pd.DataFrame:
    joint_group = get_joint_group("knee")
    joint_ids = get_joint_id(joint_group, side)
    hip_data = get_joint_data(pitch, joint_ids[0])
    knee_data = get_joint_data(pitch, joint_ids[1])
    ankle_data = get_joint_data(pitch, joint_ids[2])

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 10
    b, a = signal.butter(2, cutoff_freq / nyquist_freq)

    hip_data_filtered = hip_data.apply(lambda col: signal.filtfilt(b, a, col.values))
    knee_data_filtered = knee_data.apply(lambda col: signal.filtfilt(b, a, col.values))
    ankle_data_filtered = ankle_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )

    theta = get_joint_angle(hip_data_filtered, knee_data_filtered, ankle_data_filtered)

    return theta


def get_shoulder_rotation(pitch: Pitch, side: str) -> pd.DataFrame:
    joint_group = get_joint_group("shoulder")
    joint_ids = get_joint_id(joint_group, side)
    neck_data = get_joint_data(pitch, joint_ids[0])
    shoulder_data = get_joint_data(pitch, joint_ids[1])
    elbow_data = get_joint_data(pitch, joint_ids[2])
    nose_data = get_joint_data(pitch, joint_ids[3])

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 10
    b, a = signal.butter(2, cutoff_freq / nyquist_freq)

    neck_data_filtered = neck_data.apply(lambda col: signal.filtfilt(b, a, col.values))
    shoulder_data_filtered = shoulder_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    elbow_data_filtered = elbow_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    nose_data_filtered = nose_data.apply(lambda col: signal.filtfilt(b, a, col.values))

    theta = get_joint_angle(
        neck_data_filtered,
        shoulder_data_filtered,
        elbow_data_filtered,
        nose_data_filtered,
    )

    return theta


@profile
def get_segment_rotation(
    point1_data: pd.DataFrame, point2_data: pd.DataFrame, axis_of_rotation: str
) -> pd.DataFrame:
    point1_data = np.array(point1_data)
    point2_data = np.array(point2_data)

    match axis_of_rotation.lower():
        case "x":
            rotation_axis = [1, 0, 0]
        case "y":
            rotation_axis = [0, 1, 0]
        case "z":
            rotation_axis = [0, 0, 1]
        case _:
            print(f"Error: invalid axis input: {axis_of_rotation}")

    num_frames = np.shape(point1_data)[0]
    theta = np.zeros(num_frames)

    start_axis1 = np.absolute(point1_data[0, :] - point2_data[0, :])
    start_axis2 = np.cross(rotation_axis, start_axis1)
    start_axis2 = start_axis2 / np.linalg.norm(start_axis2)

    for i in range(1, num_frames):
        axis1 = np.absolute(point1_data[i, :] - point2_data[i, :])
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


def get_pelvis_rotation(pitch: Pitch) -> pd.DataFrame:
    right_hip_id = get_joint_id("hip", "right")
    left_hip_id = get_joint_id("hip", "left")
    right_hip_data = get_joint_data(pitch, right_hip_id)
    left_hip_data = get_joint_data(pitch, left_hip_id)

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 10
    b, a = signal.butter(2, cutoff_freq / nyquist_freq)

    right_hip_filtered = right_hip_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    left_hip_filtered = left_hip_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )

    theta = get_segment_rotation(right_hip_filtered, left_hip_filtered, "z")

    return theta


def get_trunk_rotation(pitch: Pitch) -> pd.DataFrame:
    right_shoulder_id = get_joint_id("shoulder", "right")
    left_shoulder_id = get_joint_id("shoulder", "left")
    right_shoulder_data = get_joint_data(pitch, right_shoulder_id)
    left_shoulder_data = get_joint_data(pitch, left_shoulder_id)

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 10
    b, a = signal.butter(2, cutoff_freq / nyquist_freq)

    right_shoulder_filtered = right_shoulder_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    left_shoulder_filtered = left_shoulder_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )

    theta = get_segment_rotation(right_shoulder_filtered, left_shoulder_filtered, "z")

    return theta


def get_hand_path(pitch: Pitch, side: str) -> pd.DataFrame:
    shoulder_id = get_joint_id("shoulder", side)
    wrist_id = get_joint_id("wrist", side)
    shoulder_data = get_joint_data(pitch, shoulder_id)
    wrist_data = get_joint_data(pitch, wrist_id)

    dt = get_framerate(pitch)
    nyquist_freq = 1 / (dt * 2)
    cutoff_freq = 15
    b, a = signal.butter(4, cutoff_freq / nyquist_freq)
    shoulder_data_filtered = shoulder_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )
    wrist_data_filtered = wrist_data.apply(
        lambda col: signal.filtfilt(b, a, col.values)
    )

    num_frames = np.shape(shoulder_data_filtered)[0]

    hand_path = np.array(shoulder_data_filtered - wrist_data_filtered)
    theta = np.zeros(num_frames)

    for i in range(1, num_frames):
        path_prev = hand_path[i - 1, 0:2]
        path_current = hand_path[i, 0:2]

        if np.linalg.norm(path_prev) > 0.1 and np.linalg.norm(path_current) > 0.1:
            path_prev = path_prev / np.linalg.norm(path_prev)
            path_current = path_current / np.linalg.norm(path_current)

            dot_product = np.dot(path_prev, path_current)
            cross_product = (
                path_prev[0] * path_current[1] - path_prev[1] * path_current[0]
            )
            d_theta = np.atan2(cross_product, dot_product)

            theta[i] = theta[i - 1] + d_theta
        else:
            theta[i] = theta[i - 1]

    theta = np.rad2deg(theta)

    return theta


def get_metrics(player: Player) -> None:
    arm = get_throwing_hand(player)
    if arm == "right":
        leg = "left"
    elif arm == "left":
        leg = "right"

    print(f"Calcualting metrics for {player.name}...\n")

    num_pitches = np.size(player.pitches)
    num_frames = len(player.pitches[0].timeStamps)
    hold_theta = pd.DataFrame(np.zeros([num_frames, 6]))
    hold_omega = pd.DataFrame(np.zeros([num_frames, 6]))
    for i in range(num_pitches):
        pitch = player.pitches[i]
        dt = get_framerate(pitch)

        metrics_theta = {
            "knee": get_knee_angle(pitch, leg),
            "elbow": get_elbow_angle(pitch, arm),
            "shoulder": get_shoulder_rotation(pitch, arm),
            "pelvis": get_pelvis_rotation(pitch),
            "trunk": get_trunk_rotation(pitch),
            "hand": get_hand_path(pitch, arm),
        }
        metrics_omega = {
            "knee": np.gradient(metrics_theta["knee"], dt),
            "elbow": np.gradient(metrics_theta["elbow"], dt),
            "shoulder": np.gradient(metrics_theta["shoulder"], dt),
            "pelvis": np.gradient(metrics_theta["pelvis"], dt),
            "trunk": np.gradient(metrics_theta["trunk"], dt),
            "hand": np.gradient(metrics_theta["hand"], dt),
        }
        metrics_theta = pd.DataFrame(metrics_theta)
        metrics_omega = pd.DataFrame(metrics_omega)

        if np.shape(metrics_theta)[0] != np.shape(hold_theta)[0]:
            diff = np.shape(metrics_theta)[0] - np.shape(hold_theta)[0]
            print(
                f"Frames mismatch: removing {diff} frames from {player.name} pitch {i + 1}\n"
            )
            metrics_theta = metrics_theta.iloc[diff:, :].reset_index(drop=True)
            metrics_omega = metrics_omega.iloc[diff:, :].reset_index(drop=True)

        if i == 0:
            hold_theta.columns = metrics_theta.columns
            hold_omega.columns = metrics_omega.columns

        hold_theta = (hold_theta + metrics_theta) / 2
        hold_omega = (hold_omega + metrics_omega) / 2

        pitch.metrics = [metrics_theta, metrics_omega]

    player.metrics = [hold_theta, hold_omega]

    return


# %%
def main() -> None:
    player1 = get_data("../player1")
    player2 = get_data("../player2")

    get_metrics(player1)
    get_metrics(player2)


if __name__ == "__main__":
    main()
