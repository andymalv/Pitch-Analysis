# %%
from typing import List

import biomechanics_analysis as biomech
import gold_standard as gs

# matplotlib.use("kitcat")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# import matplotlib


# %%
def load() -> (List[biomech.Session], List[gs.Session]):
    file = "landmarks.csv"
    df = biomech.get_data(file)
    df = biomech.get_metrics(df)

    gold = gs.get_data("joint_angles.csv")

    return df, gold


# def plot():
# %%
df, gold = load()
me = df[0].pitches[0].lead_knee
them = gold[0].pitches[0].lead_knee
x = range(np.shape(me)[0])

fig, ax = plt.subplots()
ax.plot(x, me.theta)
ax.plot(x, them)


# %%
def main():
    pass


if __name__ == "__main__":
    main()
