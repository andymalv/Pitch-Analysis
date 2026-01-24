# Hawkeye Pitch Analysis

Simple analysis of baseball pitch data recorded by a [Hawkeye](https://www.hawkeyeinnovations.com/) system.

## Description

This repository contains code used to analyze a sample Hawkeye pitching dataset.
The analysis focuses on processing kinematic data for each group of pitches
and outputing relevant graphics.

---

## Getting Started

### Dependencies

* MATLAB
    - Signal Processing Toolbox
* Python
    - listed in 'requirements.txt'
* Julia
    - listed in 'Project.toml'

### Executing program

As written, the code expects the data to be in .json files one directory 
above the current working directory. Change as needed.

---

## Current Work

* Python:
    - Implement plotting functionality
* Julia:
    - Fix atan2 bug by unwrapping data for torso+pelvis rotation
    - Implement plotting function(s)

## Future Plans

* Add kinetic analysis
* More translations
    - R
    - C/C++

---

## Files

```
├── LICENSE             <- Open-source license
├── README.md           <- General information
│
├── Julia/PitchAnalysis <- Julia version
│   │
│   ├── src
│   │   │
│   │   └── PitchAnalysis.jl    <- Main script
│   │
│   └── Project.toml            <- Package requirements
│
├── MATLAB              <- MATLAB version
│   │
│   ├── get_data.m              <- Import data
│   ├── get_elbow_angle.m
│   ├── get_framerate.m
│   ├── get_hand_path.m
│   ├── get_joint_angle.m
│   ├── get_joint_data.m
│   ├── get_joint_group.m
│   ├── get_joint_ids.m
│   ├── get_knee_angle.m
│   ├── get_metrics.m           <- Wrapper function
│   ├── get_pelvis_rotation.m
│   ├── get_segemtn_rotation.m
│   ├── get_shoulder_rotation.m
│   ├── get_throwing_hand.m 
│   ├── get_trunk_rotation.m
│   ├── plot_metrics.m          <- Plotting function
│   └── run_pitch_analysis.m    <- Main script
│
└── Python             <- Python version
     │
     ├── pitch_analysis.py      <- Main script
     └── requirements.txt       <- Package requirements


```
