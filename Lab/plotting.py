# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import biomechanics_analysis as biomech
import gold_standard as gs

# %%
file = "landmarks.csv"
df = biomech.get_data(file)
df = biomech.get_metrics(df)

gold = gs.get_data("joint_angles.csv")
