# -*- coding: utf-8 -*-
"""srp_gnn.ipynb_ambient_dyno_drive_basic_long

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1S02a_T3bRRU5EF6rP5ujodL_EtdCMtVm
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import sys

sys.path.insert(0, os.path.dirname(os.getcwd()) + "/code/")
!pip install helper_functions
!pip install networkx
import networkx
import helper_functions
from importlib import reload

from tqdm import tqdm
import numpy as np
import pandas as pd
from scipy.integrate import quad

import matplotlib.pyplot as plt
# %matplotlib inline

import json
import fnmatch
import scipy

from sklearn.metrics import auc
from sklearn.covariance import EllipticEnvelope

from google.colab import drive
drive.mount('/content/drive')

!unzip /content/drive/MyDrive/srp/ambient_dyno_drive_basic_long.zip -d /content/data

# List the files in the 'data' folder
files = [file for file in os.listdir('/content/data') if 'dyno' in file]
files

"""## Load Training Data
 we only have one file, "ambient_dyno_drive_benign_anomaly.log," in the folder, there is no need to perform aggregation since there is no multiple file merging required.

calling out make_can_df
"""

def make_can_df(log_filepath):

    can_df = pd.read_fwf(
        log_filepath, delimiter = ' '+ '#' + '('+')',
        skiprows = 1,skipfooter=1,
        usecols = [0,2,3],
        dtype = {0:'float64', 1:str, 2: str},
        names = ['time','pid', 'data'] )

    can_df.pid = can_df.pid.apply(lambda x: int(x,16))
    can_df.data = can_df.data.apply(lambda x: x.zfill(16)) #pad with 0s on the left for data with dlc < 8
    can_df.time = can_df.time - can_df.time.min()
    return can_df[can_df.pid<=0x700]

# Read the log file and parse the contents into a DataFrame
df = make_can_df('/content/data/ambient_dyno_drive_basic_long.log')
df

# Sort the DataFrame based on the 'time' column
df_sorted = df.sort_values('time')

# Format the 'time' values to two decimal points
df_sorted['time'] = df_sorted['time'].round(2)

# Print the new sorted DataFrame
print(df_sorted)

"""partition to 10 sec slices / time windows
here, we partition the DataFrame into consecutive time slices of 10 seconds each and print the labeled time slice along with the corresponding rows of data for each time slice.
"""

# Define the time slice duration in seconds
time_slice_duration = 10.0

# Determine the number of time slices
num_slices = int(df_sorted['time'].max() / time_slice_duration) + 1

# Iterate over the time slices
for i in range(num_slices):
    start_time = i * time_slice_duration
    end_time = (i + 1) * time_slice_duration
    time_slice_label = f"Time Slice {i + 1}: ({start_time}, {end_time}]"
    time_slice_df = df_sorted[(df_sorted['time'] > start_time) & (df_sorted['time'] <= end_time)]
    print(f"{time_slice_label}\n{time_slice_df}\n")



"""### building the graph for each time window"""

import networkx as nx
import matplotlib.pyplot as plt

# Define the time slice duration in seconds
time_slice_duration = 10.0

# Determine the number of time slices
num_slices = int(df['time'].max() / time_slice_duration) + 1

# Iterate over the time slices
for i in range(num_slices):
    start_time = i * time_slice_duration
    end_time = (i + 1) * time_slice_duration
    time_slice_label = f"Time Slice {i + 1}: ({start_time}, {end_time}]"
    time_slice_df = df[(df['time'] > start_time) & (df['time'] <= end_time)]

    # Build the graph for the current time slice
    G = nx.DiGraph()
    node_ids = time_slice_df['pid'].unique().tolist()
    G.add_nodes_from(node_ids)

    for j in range(len(time_slice_df) - 1):
        source = time_slice_df.iloc[j]['pid']
        target = time_slice_df.iloc[j+1]['pid']

        if G.has_edge(source, target):
            G[source][target]['weight'] += 1
        else:
            G.add_edge(source, target, weight=1)

    # Plot the graph
    plt.figure(i)
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=500, font_size=10, edge_color='gray')
    plt.title(time_slice_label)

plt.show()















