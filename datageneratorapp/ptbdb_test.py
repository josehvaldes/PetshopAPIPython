#
import pandas as pd
import matplotlib.pyplot as plt
import random
import numpy as np 

ptbdb_normal_df = pd.read_csv('./data/ptbdb_normal.csv')
ptbdb_abnormal_df = pd.read_csv('./data/ptbdb_abnormal.csv')

#remove last column for graphing purposes
ptbdb_normal_df = ptbdb_normal_df.drop(ptbdb_normal_df.columns[-1], axis=1)
ptbdb_abnormal_df = ptbdb_abnormal_df.drop(ptbdb_abnormal_df.columns[-1], axis=1)

columnsize = len(ptbdb_normal_df.columns)

plot1_index = random.randint(1, len(ptbdb_normal_df)-1)
plot2_index = random.randint(1, len(ptbdb_normal_df)-1)

plot3_index = random.randint(1, len(ptbdb_abnormal_df)-1)
plot4_index = random.randint(1, len(ptbdb_abnormal_df)-1)

#ptbdb_normal_df samples
print(f"Normal Index: {plot1_index} {plot2_index}")  

#ptbdb_abnormal_df samples
print(f"AbNormal Index: {plot3_index} {plot4_index}")  

x_values = np.arange(columnsize)

# Create a figure and a set of subplots (1 row, 2 columns)
fig, (ax) = plt.subplots(4, figsize=(14, 6)) # Adjust figsize as needed
fig.suptitle('ECG Signal Comparison', fontsize=16)

ax[0].plot(x_values, ptbdb_normal_df.iloc[plot1_index], color='blue')
ax[0].set_title('Normal ECG Signal')
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Amplitude')

ax[1].plot(x_values, ptbdb_normal_df.iloc[plot2_index], color='blue')

ax[2].plot(x_values, ptbdb_abnormal_df.iloc[plot3_index], color='red')
ax[2].set_title('Abnormal ECG Signal')

ax[3].plot(x_values, ptbdb_abnormal_df.iloc[plot4_index], color='red')

plt.tight_layout()

plt.show()