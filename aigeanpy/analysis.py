from typing import Union
from pathlib import Path
from aigeanpy.clustering import cluster
from aigeanpy.clustering_numpy import cluster_num


def kmeans(filename: Union[Path, str], clusters: int = 3, iterations: int = 10, Numpy=False):
    """
    Function to call the cluster_numpy and cluster functions 

    Parameters
    ----------
    filename : Path
        filename of CSV that you wish to read into the algorithm
    clusters : int
        number of clusters you want to form
    iterations: int
        number of iterations for the code to perform
    Numpy: bool
        whether to run clustering with pure python or with numpy

    Returns
    -------
    list
        a list with the measurement indices that belong to each group

    """
    file = Path(filename)
    if file.suffix != '.csv':
        raise ValueError("Input file must be a CSV file.")
        
    if Numpy:
        return cluster_num(filename, clusters, iterations)
    else:
        return cluster(filename, clusters, iterations)
