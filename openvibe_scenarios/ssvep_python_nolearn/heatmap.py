import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import numpy as np
import os

try:
    x = np.load("classifiers" + os.sep + "x_train_data.npy")
    y = np.load("classifiers" + os.sep + "y_train_data.npy")
except:
    print("Could not load preprocessed Data. Please run scenario '5_train_raw_classifier'")
    exit()

x_0 = x[y==0]
x_1 = x[y==1]
x_2 = x[y==2]
x_3 = x[y==3]

L = [x_0, x_1, x_2, x_3]

fig, ax_arr = plt.subplots(4)

for i, X in enumerate(L):
    ax_arr[i].set_title(["No Stimulation",
                         "7.5 Hz Stimulation", 
                         "10 Hz Stimulation", 
                         "12 Hz Stimulation"][i])
    for j in range(X.shape[0]):
        ax_arr[i].imshow(X[j][:,:60], aspect='auto', cmap='hot', alpha=0.1)
        ax_arr[i].set_xticks(np.arange(2,60,2))
        ax_arr[i].set_xticklabels(np.arange(1, 310, 1))
        
        ax_arr[i].set_yticks([])

        
for ax in fig.axes:
    plt.sca(ax)
    plt.xticks(rotation=45)

plt.tight_layout()

plt.show()