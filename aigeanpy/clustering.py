from math import *
from random import *
from typing import Union
from pathlib import Path
from aigeanpy.utilis import read_csv
from argparse import ArgumentParser


def cluster(filename: Union[Path, str], clusters: int, iterations: int):
    """
    Picks three points randomly to be the initial centres of the clusters, assigns each data
    point to a cluster and updates the centre of each cluster by setting it to the average
    of all points assigned to the cluster

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
    points = read_csv(filename)

    centres = sample(points, clusters)

    alloc = [None]*len(points)

    n = 0
    while n < iterations:

        for i in range(len(points)):
            select_point = points[i]
            distance = [None] * clusters

            for s, centre in enumerate(centres):
                distance[s] = sqrt((select_point[0]-centre[0])**2 +
                                   (select_point[1]-centre[1])**2 + (select_point[2]-centre[2])**2)

            alloc[i] = distance.index(min(distance))

        for i in range(clusters):

            alloc_ps = [p for j, p in enumerate(points) if alloc[j] == i]
            dim1 = sum([a[0] for a in alloc_ps]) / len(alloc_ps)
            dim2 = sum([a[1] for a in alloc_ps]) / len(alloc_ps)
            dim3 = sum([a[2] for a in alloc_ps]) / len(alloc_ps)
            new_mean = (dim1, dim2, dim3)
            centres[i] = new_mean
        n = n+1

    class_indice = []
    for i in range(clusters):
        alloc_ps = [j for j, p in enumerate(points) if alloc[j] == i]
        class_indice.append(alloc_ps.copy())
        print("Cluster " + str(i) + " is centred at " +
              str(centres[i]) + " and has " + str(len(alloc_ps)) + " points.")

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
        description='Cluster points without numpy into 3 classes')
    parser.add_argument('filename', type=str,
                        help='Please give file path to your csv file')
    parser.add_argument('--iters', default=10, type=int,
                        help='Please give number of iterations')
    arguments = parser.parse_args()

    cluster(arguments.filename, 3, arguments.iters)


if __name__ == "__main__":
    process()
