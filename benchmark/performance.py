from aigeanpy.clustering_numpy import cluster_num
from aigeanpy.clustering import cluster
import matplotlib.pyplot as plt
from timeit import default_timer as timer
import numpy as np
from random import *
from math import *
from pathlib import Path
import sys
import os
current_folder = Path(__file__).absolute().parent
new_wd = os.path.join(current_folder.parent)
os.chdir(new_wd)
sys.path.append(new_wd)


points_num = np.arange(100, 10000, 100)
t = np.zeros([len(points_num), 3])
i = 0
for num in points_num:
    f = np.random.random((num, 3))
    np.savetxt('new_sample.csv', f, delimiter=',')

    tic = timer()
    cluster('new_sample.csv', 3, 10)
    toc = timer()
    t[i, 0] = toc - tic

    tic = timer()
    cluster_num('new_sample.csv', 3, 10)
    toc = timer()
    t[i, 1] = toc - tic
    i = i+1

os.remove("new_sample.csv")

C, S = t[:, 0], t[:, 1]
plt.plot(points_num, C, marker='.', label='without numpy')
plt.plot(points_num, S, marker='.', label='with numpy')
plt.xlabel('number of points')
plt.ylabel('time(s)')
plt.title(' Time for clustering algorithm')
plt.legend()
os.chdir(current_folder)
plt.savefig('performance.png')
