from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

import biomechanics_analysis as biomech


# %%
def resample_data(df: List[biomech.Session]):
    for session in df:
        resample_rate = get_resample_rate(session)

        for pitch in session.pitches:
            time_resampled = resample_time(pitch.time_stamps, resample_rate)
            timing_metrics_resampled = resample_timing_metrics(
                pitch.timing_metrics, time_resampled
            )


def get_resample_rate(session: biomech.Session) -> int:
    samples = np.zeros(len(session.pitches))
    i = 0
    for pitch in session.pitches:
        samples[i] = len(pitch.time_stamps)
        i += 1

    return samples.min()


def resample_time(time_raw: pd.Series, resample_rate: int) -> pd.Series:
    resampled_time = np.linspace(time_raw.min(), time_raw.max(), resample_rate)

    return resampled_time


def resample_timing_metrics(timing_metrics: pd.DataFrame, resampled_time: pd.Series):
    resampled_timing_metrics = []
    for metric in timing_metrics:
        high_index = np.searchsorted(resampled_time, metric, side="left")
        high_num = resampled_time[high_index]
        high_diff = np.abs(metric - high_num)

        low_num = resampled_time[high_index - 1]
        low_diff = np.abs(metric - low_num)

        if low_diff < high_diff:
            resampled_timing_metrics.append(low_num)
        else:
            resampled_timing_metrics.append(high_num)

    resampled_timing_metrics = pd.DataFrame(resampled_timing_metrics)
    resampled_timing_metrics.columns = timing_metrics.columns

    return resampled_timing_metrics


# %%
def main():
    path = "landmarks.csv"
    df = biomech.get_data(path)
    df = biomech.get_metrics(df)


if __name__ == "__main__":
    main()
