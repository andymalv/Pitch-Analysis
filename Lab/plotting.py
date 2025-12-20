# %%
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import biomechanics_analysis as biomech
import gold_standard as gs


# %%
def load() -> List[biomech.Session]:
    file = "landmarks.csv"
    df = biomech.get_data(file)
    df = biomech.get_metrics(df)

    # gold = gs.get_data("joint_angles.csv")

    # return df, gold
    return df


# %%
def get_session(df: List[biomech.Session]) -> biomech.Session:
    session_ids = []
    for i in range(len(df)):
        session_id = df[i].id
        session_ids.append(session_id)
    session_choice = st.selectbox("Select a session: ", session_ids)
    session_index = session_ids.index(session_choice)

    return df[session_index]


def get_pitch(session: biomech.Session) -> biomech.Pitch:
    pitch_num = len(session.pitches)
    pitch_choice = st.selectbox("Select a pitch: ", range(1, pitch_num + 1))
    pitch_index = int(pitch_choice) - 1

    return session.pitches[pitch_index]


def get_joint(pitch: biomech.Pitch) -> pd.DataFrame:
    joint_list = ["Lead Knee"]
    joint_choice = st.selectbox("Select a joint: ", joint_list)

    match joint_choice:
        case "Lead Knee":
            joint_data = pitch.lead_knee

    return joint_data


def get_metric(joint: pd.DataFrame) -> Tuple[pd.Series, str]:
    metric_list = ["Joint Angle"]
    metric_choice = st.selectbox("Select a metric: ", metric_list)

    match metric_choice:
        case "Joint Angle":
            metric_data = joint.theta
            y_label = "Degrees"

    return metric_data, y_label


# %%
def main():
    if "df" not in vars():
        df = load()

    session = get_session(df)
    pitch = get_pitch(session)
    joint = get_joint(pitch)
    metric, y_label = get_metric(joint)

    clicked = st.button("Load plot")

    if clicked:
        y = metric
        x = range(len(y))

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set(title="hold", ylabel=y_label)
        st.pyplot(fig)


# %%
if __name__ == "__main__":
    main()
