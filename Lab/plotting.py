# %%
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import biomechanics_analysis as biomech


# %%
def load() -> List[biomech.Session]:
    file = "landmarks.csv"
    df = biomech.get_data(file)
    df = biomech.get_metrics(df)

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
    pitch_data = session.pitches[pitch_index]

    return pitch_data, pitch_choice


def get_pitch_multiselect(
    session: biomech.Session,
) -> Tuple[List[biomech.Pitch], List[str]]:
    pitch_num = len(session.pitches)
    pitch_list = [f"Pitch {i}" for i in range(1, pitch_num + 1)]
    pitch_choice = st.multiselect("Select pitches: ", pitch_list)

    if type(pitch_choice) is not list:
        pitch_choice = [pitch_choice]

    pitch_data = [session.pitches[pitch_list.index(i)] for i in pitch_choice]

    return pitch_data, pitch_choice


def get_joint(pitches: List[biomech.Pitch]) -> Tuple[List[pd.DataFrame], str]:
    joint_list = ["Lead Knee"]
    joint_choice = st.selectbox("Select a joint: ", joint_list)

    match joint_choice:
        case "Lead Knee":
            joint_data = [pitch.lead_knee for pitch in pitches]

    return joint_data, joint_choice


# def get_joint(pitch: biomech.Pitch) -> Tuple[pd.DataFrame, str]:
#     joint_list = ["Lead Knee"]
#     joint_choice = st.selectbox("Select a joint: ", joint_list)
#
#     match joint_choice:
#         case "Lead Knee":
#             joint_data = pitch.lead_knee
#
#     return joint_data, joint_choice


def get_metric(joint: List[pd.DataFrame]) -> Tuple[pd.DataFrame, str]:
    metric_list = ["Joint Angle", "Joint Veolcity"]
    metric_choice = st.selectbox("Select a metric: ", metric_list)

    match metric_choice:
        case "Joint Angle":
            metric_data = pd.concat([joint.theta for joint in joint], axis=1)
        case "Joint Velocity":
            metric_data = pd.concat([joint.omega for joint in joint], axis=1)

    return metric_data, metric_choice


# def get_metric(joint: pd.DataFrame) -> Tuple[pd.Series, str]:
#     metric_list = ["Joint Angle", "Joint Veolcity"]
#     metric_choice = st.selectbox("Select a metric: ", metric_list)
#
#     match metric_choice:
#         case "Joint Angle":
#             metric_data = joint.theta
#         case "Joint Velocity":
#             metric_data = joint.omega
#
#     return metric_data, metric_choice


def get_y_label(metric_choice: str) -> str:
    match metric_choice:
        case "Joint Angle":
            units = "(°)"
        case "Joint Velocity":
            units = "(m/s)"

    y_label = metric_choice + " " + units

    return y_label


def make_timing_marks2(
    ax,
    checkboxes: List[bool],
    metric_data: List[pd.Series],
    timing_metrics: List[pd.DataFrame],
):
    colors = [
        "xkcd:green",
        "xkcd:red",
        "xkcd:aqua",
        "xkcd:orange",
        "xkcd:yellow",
        "xkcd:magenta",
    ]

    for i in range(len(metric_data)):
        if checkboxes[0]:
            x = timing_metrics[i].pkh_time
            y = metric_data[i][x]
            ax.scatter(x, y, marker="x", c=colors[0], s=200, linewidth=2.5, label="PKH")
        if checkboxes[1]:
            x = timing_metrics[i].fp_10_time
            y = metric_data[i][x]
            ax.scatter(
                x, y, marker="x", c=colors[1], s=200, linewidth=2.5, label="FP 10"
            )
        if checkboxes[2]:
            x = timing_metrics[i].fp_100_time
            y = metric_data[i][x]
            ax.scatter(
                x, y, marker="x", c=colors[2], s=200, linewidth=2.5, label="FP 100"
            )
        if checkboxes[3]:
            x = timing_metrics[i].MER_time
            y = metric_data[i][x]
            ax.scatter(x, y, marker="x", c=colors[3], s=200, linewidth=2.5, label="MER")
        if checkboxes[4]:
            x = timing_metrics[i].BR_time
            y = metric_data[i][x]
            ax.scatter(x, y, marker="x", c=colors[4], s=200, linewidth=2.5, label="BR")
        if checkboxes[5]:
            x = timing_metrics[i].MIR_time
            y = metric_data[i][x]
            ax.scatter(x, y, marker="x", c=colors[5], s=200, linewidth=2.5, label="MIR")


def make_timing_marks(ax, checkboxes, metric_data, time_stamps, timing_metrics):
    colors = [
        "xkcd:green",
        "xkcd:red",
        "xkcd:aqua",
        "xkcd:orange",
        "xkcd:yellow",
        "xkcd:magenta",
    ]

    if checkboxes[0]:
        x = timing_metrics.pkh_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[0], s=200, linewidth=2.5, label="PKH")
    if checkboxes[1]:
        x = timing_metrics.fp_10_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[1], s=200, linewidth=2.5, label="FP 10")
    if checkboxes[2]:
        x = timing_metrics.fp_100_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[2], s=200, linewidth=2.5, label="FP 100")
    if checkboxes[3]:
        x = timing_metrics.MER_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[3], s=200, linewidth=2.5, label="MER")
    if checkboxes[4]:
        x = timing_metrics.BR_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[4], s=200, linewidth=2.5, label="BR")
    if checkboxes[5]:
        x = timing_metrics.MIR_time
        index = list(time_stamps).index(x)
        y = metric_data[index]
        ax.scatter(x, y, marker="x", c=colors[5], s=200, linewidth=2.5, label="MIR")

    return ax


def get_selections(df) -> Tuple[biomech.Session, List, List, List, List]:
    col1, col2 = st.columns(2)
    with col1:
        session = get_session(df)
        pitch_data, pitch_choice = get_pitch(session)
        # pitch_data, pitch_choice = get_pitch_multiselect(session)
        mean_check = st.checkbox("Average selected pitches")
    with col2:
        joint_data, joint_choice = get_joint([pitch_data])
        # joint_data, joint_choice = get_joint(pitch_data)
        metric_data, metric_choice = get_metric(joint_data)

    if mean_check:
        metric_data = metric_data.mean(axis=1)

    st.divider()

    st.header("Select timing metrics: ")
    col1, col2 = st.columns(2)
    with col1:
        pkh_check = st.checkbox("pkh_time")
        fp_10_check = st.checkbox("fp_10_time")
        fp_100_check = st.checkbox("fp_100_time")
    with col2:
        MER_check = st.checkbox("MER_time")
        BR_check = st.checkbox("BR_time")
        MIR_check = st.checkbox("MIR_time")

    pitch = [pitch_data, pitch_choice, mean_check]
    joint = [joint_data, joint_choice]
    metric = [metric_data, metric_choice]
    checkboxes = [pkh_check, fp_10_check, fp_100_check, MER_check, BR_check, MIR_check]

    return session, pitch, joint, metric, checkboxes


def make_fig2(df):
    session, pitches, joint, metric, checkboxes = get_selections(df)

    timing_metrics = [pitch[0].timing_metrics for pitch in pitches]

    fig_title = f"Session {session.id}"
    ax_title = joint[1] + metric[1].replace("Joint", "")
    y_label = get_y_label(metric[1])

    clicked = st.button("Load plot")

    if clicked:
        fig, ax = plt.subplots()
        plt.style.use("ggplot")
        fig.suptitle(fig_title)
        ax.set(title=ax_title, ylabel=y_label)

        for i in metric[0]:
            x = range(0, 101)
            y = metric[i]
            plot_label = f"Pitch {i + 1}"

            ax.plot(x, y, label=plot_label)

        fig.legend(loc="outside right upper")

        st.pyplot(fig)


def make_fig(df):
    session, pitch, joint, metric, checkboxes = get_selections(df)

    time_stamps = pitch[0].time_stamps
    timing_metrics = pitch[0].timing_metrics
    fig_title = f"Session {session.id}, Pitch {pitch[1]}"
    ax_title = joint[1] + metric[1].replace("Joint", "")
    y_label = get_y_label(metric[1])

    clicked = st.button("Load plot")

    if clicked:
        x = time_stamps
        y = metric[0]

        fig, ax = plt.subplots()
        plt.style.use("ggplot")
        ax.plot(x, y)
        ax.set(title=ax_title, ylabel=y_label)

        ax = make_timing_marks(ax, checkboxes, metric[0], time_stamps, timing_metrics)

        fig.suptitle(fig_title)
        fig.legend(loc="outside right upper")

        st.pyplot(fig)


# %%
def main():
    if "df" not in vars():
        df = load()

    st.title("Driveline Pitching Data")
    make_fig(df)


# %%
if __name__ == "__main__":
    main()
