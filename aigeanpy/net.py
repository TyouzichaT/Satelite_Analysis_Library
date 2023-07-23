import os
import requests
from pathlib import Path
import datetime


def query_isa(start_date: str, stop_date: str, instrument=None):
    """
    Query the Aigean database for JSON files that include information about the date and time of
    the observations, the instrument used, the field of view observed and the filename where that observation is
    stored`

    Parameters
    ----------
    start_date : str
        date in format YYYY-mm-dd - sets the starting date to search for data in the Aigean archive

    stop_date : str
        date in format YYYY-mm-dd - sets the end date (inclusive) to search in the Aigean archive

    instrument : str
        one of the possible instruments: 'Lir', 'Manannan', 'Fand' or 'Ecne'. 

    Returns
    -------
    r : JSON object
        the JSON file queried.

    Example
    -------
    A typical query, looking for data from Ecne across two days in January.

    >>> query_isa('2023-01-10', '2023-01-11', 'Ecne')
    [{'date': '2023-01-10', 'filename': 'aigean_ecn_20230110_091234.csv', 'instrument': 'ecne', 'resolution': 1, 'time': '09:12:34', 'xcoords': [0.0, 1500.0], 'ycoords': [0.0, 500.0]}, {'date': '2023-01-11', 'filename': 'aigean_ecn_20230111_081548.csv', 'instrument': 'ecne', 'resolution': 1, 'time': '08:15:48', 'xcoords': [0.0, 1500.0], 'ycoords': [0.0, 500.0]}]

    """
    try:
        datetime.datetime.strptime(start_date, '%Y-%m-%d')
        datetime.datetime.strptime(stop_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-mm-dd")

    try:
        if instrument == None:
            response = requests.get("http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query",
                                    params={
                                        'start_date': start_date,
                                        'stop_date': stop_date,
                                    })
        else:
            response = requests.get("http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/query",
                                    params={
                                        'start_date': start_date,
                                        'stop_date': stop_date,
                                        'instrument': instrument,
                                    })
    except:
            raise ConnectionError('No internet connection')
            
    r = response.json()
    return r


def download_isa(filename: str, save_dir: str):
    """
    Downloads a file from the ISA archive. Appropriate filenames can be found using query_isa.

    Parameters
    ----------
    filename : str
        A filename within the ISA archive.

    save_dir : str
        A directory relative to the root to save the file into. If you wish to
        save into the current directory, enter ".".

    Example
    -------
    The filename needs to be exactly as given from a query; here the instrument name \'Ecne\' should appear as `ecn` in the filename.

    >>> download_isa('aigean_ecne_20230110_091234.zip', '.')
    Traceback (most recent call last):
        ...
    Exception: Download file failed

    """
    if not os.path.exists(save_dir):
        raise Exception("Saving path does not exits")

    url = 'http://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/download/?filename={}'.format(
        filename)
    response = requests.get(url, stream=True)
    file_path = os.path.join(save_dir, filename)

    if response.ok:
        download = response.content
        dir_path = Path(file_path)
        dir_path.write_bytes(download)
    else:
        raise Exception("Download file failed")


if __name__ == "__main__":
    import doctest
    doctest.testmod()
