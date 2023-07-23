from math import *
from random import *
import numpy as np
from typing import Union
from pathlib import Path
from aigeanpy.utilis import read_csv
from argparse import ArgumentParser


def cluster_num(filename: Union[Path, str], cluster_num: int, iters: int):
    """
    Picks three points randomly to be the initial centres of the clusters, assigns each data
    point to a cluster and updates the centre of each cluster by setting it to the average
    of all points assigned to the cluster, using numpy. 

    Parameters
    ----------
    filename : Path
        filename of CSV that you wish to read into the algorithm
    clusters : int
        number of clusters you want to form
    iterations: int
        number of iterations for the code to perform

    Returns
    -------
    class_indice : list
        list of points where the point is in the cluster. 

    """
    points = np.genfromtxt(filename, delimiter=",", dtype='float')
    random_index = np.arange(points.shape[0])
    np.random.shuffle(random_index)
    centres = points[random_index[0:cluster_num]]

    for j in range(iters):

        distance = np.zeros([points.shape[0], cluster_num])
        for i in range(cluster_num):
            distance[:, i] = ((points[:, 0]-centres[i, 0])**2 + (points[:, 1] -
                              centres[i, 1])**2 + (points[:, 2]-centres[i, 2])**2)**0.5

        alloc = np.argmin(distance, axis=1)

        for i in range(cluster_num):
            centres[i] = np.sum(points[np.argwhere(alloc == i)],
                                axis=0)/len(np.argwhere(alloc == i))

    class_indice = []
    for i in range(cluster_num):
        alloc_index = np.argwhere(alloc == i).flatten().tolist()
        class_indice.append(alloc_index.copy())
        print("Cluster " + str(i) + " is centred at " +
              str(centres[i]) + " and has " + str(len(alloc_index)) + " points.")

    return class_indice


def process():
    """
    function to create command line interface

    Parameters
    ----------
    None

    Returns
    -------
    None

    """
    parser = ArgumentParser(
        description='Cluster points with numpy into 3 classes')
    parser.add_argument('filename', type=str,
                        help='Please give file path to your csv file')
    parser.add_argument('--iters', default=10, type=int,
                        help='Please give number of iterations')
    arguments = parser.parse_args()

    cluster_num(arguments.filename, 3, arguments.iters)


if __name__ == "__main__":
    process()
