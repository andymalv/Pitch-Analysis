from dataclasses import fields
from typing import List

import numpy as np
import pandas as pd
from rich.progress import track

from models import Pitch, Session


# %%
def resample_data(df: List[Session]) -> List[Session]:
    resampled_df = []
    # for session in df:
    for i in track(range(len(df)), description="Resampling data..."):
        session = df[i]
        resample_rate = get_resample_rate(session)
        resampled_session = resample_session(session, resample_rate)
        resampled_df.append(resampled_session)

    return resampled_df


def resample_session(session: Session, resample_rate: int) -> Session:
    resampled_pitches = []
    for pitch in session.pitches:
        if len(pitch.time_stamps) == resample_rate:
            resampled_pitches.append(pitch)
        else:
            resampled_pitches.append(resample_pitch(pitch, resample_rate))

    resampled_session = Session(resampled_pitches, session.id)

    return resampled_session


def get_resample_rate(session: Session) -> int:
    samples = np.zeros(len(session.pitches))
    i = 0
    for pitch in session.pitches:
        samples[i] = len(pitch.time_stamps)
        i += 1

    return int(samples.min())


def resample_time(time_raw: pd.Series, resample_rate: int) -> pd.Series:
    resampled_time = np.linspace(time_raw.min(), time_raw.max(), resample_rate)

    return resampled_time


def resample_timing_metrics(timing_metrics: pd.DataFrame, resampled_time: pd.Series):
    resampled_timing_metrics = []
    for metric in timing_metrics:
        high_index = np.searchsorted(resampled_time, metric, side="left")
        if high_index >= len(resampled_time):
            high_index = len(resampled_time) - 1
        high_num = resampled_time[high_index]
        high_diff = np.abs(metric - high_num)

        low_num = resampled_time[high_index - 1]
        low_diff = np.abs(metric - low_num)

        if low_diff < high_diff:
            resampled_timing_metrics.append(low_num)
        else:
            resampled_timing_metrics.append(high_num)

    resampled_timing_metrics = pd.DataFrame(resampled_timing_metrics).T
    resampled_timing_metrics.columns = timing_metrics.columns

    return resampled_timing_metrics


def resample_pitch(pitch: Pitch, resample_rate: int) -> Pitch:
    raw_time = pitch.time_stamps
    resampled_time = resample_time(raw_time, resample_rate)
    resampled_timing_metrics = resample_timing_metrics(
        pitch.timing_metrics, resampled_time
    )
    resampled_joints = []
    for joint in fields(pitch):
        if joint.name == "time_stamps" or joint.name == "timing_metrics":
            pass
        else:
            joint_data = getattr(pitch, joint.name)
            resampled_data = resample_joint(joint_data, raw_time, resampled_time)
            resampled_data.columns = joint_data.columns
            resampled_joints.append(resampled_data)
            #     resample_joint(joint_data, raw_time, resampled_time)
            # )

    resampled_pitch = Pitch(
        pd.Series(resampled_time),
        resampled_timing_metrics,
        resampled_joints[0],
        resampled_joints[1],
        resampled_joints[2],
        resampled_joints[3],
        resampled_joints[4],
        resampled_joints[5],
        resampled_joints[6],
        resampled_joints[7],
        resampled_joints[8],
        resampled_joints[9],
        resampled_joints[10],
        resampled_joints[11],
        resampled_joints[12],
        resampled_joints[13],
        resampled_joints[14],
        resampled_joints[15],
        resampled_joints[16],
        resampled_joints[17],
        resampled_joints[18],
        resampled_joints[19],
    )

    return resampled_pitch


def resample_joint(
    joint: pd.DataFrame, raw_time: pd.Series, resampled_time: pd.Series
) -> pd.DataFrame:
    resampled_joint = pd.DataFrame()
    for col in joint.columns:
        resampled_values = pd.Series(np.interp(resampled_time, raw_time, joint[col]))
        resampled_joint = pd.concat([resampled_joint, resampled_values], axis=1)

    return resampled_joint
