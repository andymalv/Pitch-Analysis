from dataclasses import dataclass
from typing import List

import pandas as pd


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
