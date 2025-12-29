# Hawkeye Pitch Analysis

Simple analysis of baseball pitch data recorded by a [Hawkeye](https://www.hawkeyeinnovations.com/) system.

## Description

A program, written in multiple languages, to intake and process kinematic data, then output plots.

## Getting Started

### Dependencies

* MATLAB
    - a MATLAB license
    - Signal Processing Toolbox
* Python
    - listed in 'requirements.txt'
* Julia
    - listed in 'Project.toml'

### Executing program

As written, the code expects the data to be in .json files one directory above the current working directory. Change as needed.

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
