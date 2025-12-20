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
    session = df[session_index]

    return session


def get_pitch(
    session: biomech.Session,
) -> Tuple[biomech.Pitch, str]:
    pitch_num = len(session.pitches)
    pitch_choice = st.selectbox("Select a pitch: ", range(1, pitch_num + 1))
    pitch_index = int(pitch_choice) - 1
    pitch = session.pitches[pitch_index]

    return pitch, pitch_choice


def get_joint(pitch: biomech.Pitch) -> Tuple[pd.DataFrame, str]:
    joint_list = ["Lead Knee"]
    joint_choice = st.selectbox("Select a joint: ", joint_list)

    match joint_choice:
        case "Lead Knee":
            joint_data = pitch.lead_knee

    return joint_data, joint_choice


def get_metric(joint: pd.DataFrame) -> Tuple[pd.Series, str]:
    metric_list = ["Joint Angle", "Joint Veolcity"]
    metric_choice = st.selectbox("Select a metric: ", metric_list)

    match metric_choice:
        case "Joint Angle":
            metric_data = joint.theta
        case "Joint Velocity":
            metric_data = joint.omega

    return metric_data, metric_choice


def get_y_label(metric_choice: str) -> str:
    match metric_choice:
        case "Joint Angle":
            units = "(°)"
        case "Joint Velocity":
            units = "(m/s)"

    y_label = metric_choice + " " + units

    return y_label


# %%
def main():
    if "df" not in vars():
        df = load()

    col1, col2 = st.columns(2)

    with col1:
        session = get_session(df)
        pitch, pitch_choice = get_pitch(session)
        pkh_check = st.checkbox("pkh_time")
        fp_10_check = st.checkbox("fp_10_time")
        fp_100_check = st.checkbox("fp_100_time")
    with col2:
        joint_data, joint_choice = get_joint(pitch)
        metric_data, metric_choice = get_metric(joint_data)
        MER_check = st.checkbox("MER_time")
        BR_check = st.checkbox("BR_time")
        MIR_check = st.checkbox("MIR_time")

    time_stamps = pitch.time_stamps
    timing_metrics = pitch.timing_metrics
    colors = [
        "xkcd:green",
        "xkcd:red",
        "xkcd:aqua",
        "xkcd:orange",
        "xkcd:yellow",
        "xkcd:magenta",
    ]
    fig_title = f"Session {session.id}, Pitch {pitch_choice}"
    ax_title = joint_choice + metric_choice.replace("Joint", "")
    line_label = metric_choice.replace("Joint", "")
    y_label = get_y_label(metric_choice)

    clicked = st.button("Load plot")

    if clicked:
        x = time_stamps
        y = metric_data

        fig, ax = plt.subplots()
        plt.style.use("ggplot")
        ax.plot(x, y)
        ax.set(title=ax_title, ylabel=y_label)

        if pkh_check:
            x = timing_metrics.pkh_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(x, y, marker="x", c=colors[0], s=200, linewidth=2.5, label="PKH")
        if fp_10_check:
            x = timing_metrics.fp_10_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(
                x, y, marker="x", c=colors[1], s=200, linewidth=2.5, label="FP 10"
            )
        if fp_100_check:
            x = timing_metrics.fp_100_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(
                x, y, marker="x", c=colors[2], s=200, linewidth=2.5, label="FP 100"
            )
        if MER_check:
            x = timing_metrics.MER_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(x, y, marker="x", c=colors[3], s=200, linewidth=2.5, label="MER")
        if BR_check:
            x = timing_metrics.BR_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(x, y, marker="x", c=colors[4], s=200, linewidth=2.5, label="BR")
        if MIR_check:
            x = timing_metrics.MIR_time
            index = list(time_stamps).index(x)
            y = metric_data[index]
            ax.scatter(x, y, marker="x", c=colors[5], s=200, linewidth=2.5, label="MIR")

        fig.suptitle(fig_title)
        fig.legend(loc="outside right upper")

        st.pyplot(fig)


# %%
if __name__ == "__main__":
    main()
