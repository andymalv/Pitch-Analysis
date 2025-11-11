# %%
import os

import numpy as np
import pandas as pd


# %%
def get_data(directory):
    print(f"Gathering data for", directory, "...\n")

    files = []
    for file in os.listdir(directory):
        if file.endswith(".json"):
            files.append(os.path.join(directory, file))

    num_files = np.size(files)

    for i in range(num_files):
        try:
            file_path = files[i]
            data_hold = pd.read_json(file_path)
        except:
            print(f"Error reading file: ", file_path)

        # filed_name =
