from typing import Union
from pathlib import Path
import sys


def get_meta(meta_dict):
    meta = {}
    meta['archive'] = meta_dict['archive']
    meta['year'] = meta_dict['year']
    meta['date'] = meta_dict['date']
    meta['instrument'] = meta_dict['instrument']
    meta['observatory'] = meta_dict['observatory']
    meta['resolution'] = meta_dict['resolution']
    meta['time'] = meta_dict['time']
    meta['xcoords'] = meta_dict['xcoords']
    meta['ycoords'] = meta_dict['ycoords']
    return meta


def read_csv(filename: Union[Path, str]):

    lines = open(filename, 'r').readlines()
    points = []
    for line in lines:
        points.append(tuple(map(float, line.strip().split(','))))

    return points

# common print error


def print_err(msg="", is_stop=True):
    print(msg)
    if is_stop:
        sys.exit(1)
