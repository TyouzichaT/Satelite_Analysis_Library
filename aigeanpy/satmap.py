import asdf
import h5py
from zipfile import ZipFile
import json
import numpy as np
import os
import io
import matplotlib.pyplot as plt
from aigeanpy.utilis import get_meta
from pathlib import Path
import copy
from skimage.transform import rescale
import io


class SatMap(object):

    """
    The SatMap object is the main data structure used in this package.

    SatMaps are designed to house images and metadata taken from instruments 
    of the Aigean observatory. 

    The methods on this class allow basic comparison and combination between 
    images, as well as tools to summarise and visualise the data within.

    """

    def __init__(self, meta: dict, data):
        """
        Takes metadata and image data, and initialises a SatMap object.

        Parameters
        ----------
        meta : dict
            Contains the metadata for the image in question.
            Metadata can include the following information:
            
            'archive': str
                Who the file is stored by.
            'date': str ('YYYY-MM-DD')
                The day on which the file was created.
            'instrument': str
                The name of the instrument providing the data.
                This package is currently designed to work with intruments
                Lir, Mannanan, Fand, and Ecne. 
            'observatory': str
                The name of the observatory where the image was taken. 
                This package is designed for use with the Aigean
                observatory.
            'resolution': float
                The scale factor between the image and real coordinates, 
                specified in meters per pixel.
            'time': str ('HH-MM-SS')
                The time at which the file was created.
            'xcoords': (1,2) shape array of floats
                The coordinates in meters of the (left, right) boundaries 
                of the image.
            'ycoords': (1,2) shape array of floats
                The coordinates in meters of the (bottom, top) boundaries 
                of the image.

        data : numpy array
            Contains the measurement data in question.
            For images, this is the image data as an array. 

        Example
        -------
        >>> data = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 1, 'xcoords': [2., 5.], 'ycoords': [1., 4.]}
        >>> map = SatMap(meta, data)
        >>> map.data
        array([[0, 0, 1],
               [0, 0, 1],
               [0, 0, 1]])

        """

        if meta['xcoords'][1] < meta['xcoords'][0]:
            raise ValueError(
                'The first x coordinate in the metadata should be less than the second.')
        if meta['ycoords'][1] < meta['ycoords'][0]:
            raise ValueError(
                'The first y coordinate in the metadata should be less than the second.')

        if type(meta) != dict:
            raise TypeError(
                'The \'meta\' argument of a SatMap must be a dict object.')

        if type(data) != np.ndarray:
            raise TypeError(
                'The \'data\' argument of a SatMap must be an array.')

        self.meta = meta.copy()
        self.data = data.copy()
        self.shape = self.data.shape
        self.meta['xcoords'] = np.array(self.meta['xcoords']).astype(int)
        self.meta['ycoords'] = np.array(self.meta['ycoords']).astype(int)
        self.fov = (meta['xcoords'][1] - meta['xcoords'][0],
                    meta['ycoords'][1] - meta['ycoords'][0])
        self.centre = ((meta['xcoords'][1] - meta['xcoords'][0])/2,
                       (meta['ycoords'][1] - meta['ycoords'][0])/2)

    def pixel_to_earth(self, p_x, p_y):
        """
        Function to convert a given pixel coordinate to the corresponding 
        earth coordinate with the top left pixel as (0,0), the x pixel axis 
        running down the left of the image. 

        The earth coordinate of a pixel is that of the pixel's center.

        Parameters
        ----------
        p_x : int
            The x value of the pixel coordinate.
        p_y : int
            The y value of the pixel coordinate.

        Returns
        -------
        earth_x : float
            earth x coordinate, in meters, of the pixel.
        earth_y : float
            earth y coordinate, in meters, of the pixel.

        Example
        -------
        >>> data = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 1, 'xcoords': [4., 7.], 'ycoords': [6., 9.]}
        >>> map = SatMap(meta, data)
        >>> map.pixel_to_earth(0,0)
        (4.5, 8.5)

        """

        earth_x = self.meta['xcoords'][0] + p_y * \
            self.meta['resolution'] + self.meta['resolution']/2
        earth_y = self.meta['ycoords'][1] - p_x * \
            self.meta['resolution'] - self.meta['resolution']/2
        earth = (earth_x, earth_y)
        return earth

    def earth_to_pixel(self, earth_x, earth_y):
        """
        Function to convert a given earth coordinate to the corresponding 
        image pixel.

        Coordinates on or outside the boundary of the image get mapped to the
        nearest point on the edge.

        Parameters
        ----------
        earth_x : float
            Earth x coordinate, in meters.
        earth_y : float
            Earth y coordinate, in meters.

        Returns
        -------
        p_x : int
            x pixel coordinate.
        p_y : int
            y pixel coordinate.

        Example
        -------
        >>> data = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 2, 'xcoords': [0., 6.], 'ycoords': [2., 8.]}
        >>> map = SatMap(meta, data)
        >>> map.earth_to_pixel(3,5.3)
        (1, 1)

        """

        if earth_y >= self.meta['ycoords'][1]:
            p_x = 0
        elif earth_y <= self.meta['ycoords'][0]:
            p_x = self.shape[0]-1
        else:
            p_x = self.shape[0]-1-(earth_y-self.meta['ycoords']
                                   [0])//self.meta['resolution']

        if earth_x <= self.meta['xcoords'][0]:
            p_y = 0
        elif earth_x >= self.meta['xcoords'][1]:
            p_y = self.shape[1]-1
        else:
            p_y = (earth_x-self.meta['xcoords'][0])//self.meta['resolution']

        pixel = (int(p_x), int(p_y))
        return pixel

    def __str__(self):
        """
        This method allows a SatMap to be converted directly into a string.

        Returns
        -------
        summary : str
            A concise description of image metadata.

        Example
        -------
        >>> data = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta = {'date': '2022-12-01','time': '21:43:42', 'observatory': 'Aigean', 'instrument': 'lir', 'resolution': 2, 'xcoords': [0., 6.], 'ycoords': [2., 8.]}
        >>> map1 = SatMap(meta, data)
        >>> print(str(map1))
        < AIGEAN/ lir: (0,2) - (6,8) 2 m/px

        """
        summary = (f"< {self.meta['observatory'].upper()}/ {self.meta['instrument']}: ({self.meta['xcoords'][0]},{self.meta['ycoords'][0]}) - ({self.meta['xcoords'][1]},{self.meta['ycoords'][1]}) {self.meta['resolution']} m/px")
        return summary

    def __add__(self, OtherMap):
        """
        This method allows you to 'add' two SatMap objects into a new SatMap, 
        with the natural syntax "a + b".

        For images, the data will be added in the earth coordinate system. Any
        overlapping area will be the average of the two. 

        This method is written with the restriction that the two SatMaps being 
        added are from the same instrument, and from the same day, so any data
        in the overlap between them is approximately equal.

        Parameters
        ----------
        other : SatMap
            SatMap to be added to first

        Raises
        ------
        ValueError
            If objects of different resolutions, from different instruments, 
            or taken on different days are added.

        Returns
        -------
        new_satmap : SatMap
            A single satmap containing the data of the two added maps.

        Example
        -------
        >>> data1 = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> data2 = np.array([[1,0,0], [1,0,0], [1,0,0]])
        >>> meta1 = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 1, 'xcoords': [0., 3.], 'ycoords': [0., 3.]}
        >>> meta2 = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 1, 'xcoords': [3., 6.], 'ycoords': [0., 3.]}
        >>> map1 = SatMap(meta1, data1)
        >>> map2 = SatMap(meta2, data2)
        >>> (map1 + map2).data
        array([[0., 0., 1., 1., 0., 0.],
               [0., 0., 1., 1., 0., 0.],
               [0., 0., 1., 1., 0., 0.]])



        """

        if self.meta['resolution'] != OtherMap.meta['resolution']:
            raise Exception("Different resolution")

        if self.meta['date'] != OtherMap.meta['date']:
            raise Exception("Different date")

        new_meta = self.meta.copy()
        new_meta['time'] = self.meta['time']+',' + OtherMap.meta['time']
        new_meta['xcoords'] = (min(self.meta['xcoords'][0],
                                   OtherMap.meta['xcoords'][0]),
                               max(self.meta['xcoords'][1],
                                   OtherMap.meta['xcoords'][1]))

        new_meta['ycoords'] = (min(self.meta['ycoords'][0],
                                   OtherMap.meta['ycoords'][0]),
                               max(self.meta['ycoords'][1],
                                   OtherMap.meta['ycoords'][1]))

        new_meta['resolution'] = self.meta['resolution']

        arry_shape_0 = round(
            (new_meta['ycoords'][1] - new_meta['ycoords'][0])/new_meta['resolution'])
        arry_shape_1 = round(
            (new_meta['xcoords'][1] - new_meta['xcoords'][0])/new_meta['resolution'])

        new_data = np.zeros((arry_shape_0, arry_shape_1))

        if (new_meta['xcoords'][0] == self.meta['xcoords'][0] and
                new_meta['ycoords'][0] == self.meta['ycoords'][0]):
            new_data[-self.data.shape[0]:, :self.data.shape[1]] = self.data

        elif (new_meta['xcoords'][1] == self.meta['xcoords'][1] and
              new_meta['ycoords'][1] == self.meta['ycoords'][1]):
            new_data[:self.data.shape[0], -self.data.shape[1]:] = self.data

        elif (new_meta['xcoords'][0] == self.meta['xcoords'][0] and
              new_meta['ycoords'][1] == self.meta['ycoords'][1]):
            new_data[:self.data.shape[0], :self.data.shape[1]] = self.data

        elif (new_meta['xcoords'][1] == self.meta['xcoords'][1] and
              new_meta['ycoords'][0] == self.meta['ycoords'][0]):
            new_data[-self.data.shape[0]:, -self.data.shape[1]:] = self.data

        if (new_meta['xcoords'][0] == OtherMap.meta['xcoords'][0] and
                new_meta['ycoords'][0] == OtherMap.meta['ycoords'][0]):
            new_data[-OtherMap.data.shape[0]:,
                     :OtherMap.data.shape[1]] = OtherMap.data

        elif (new_meta['xcoords'][1] == OtherMap.meta['xcoords'][1] and
              new_meta['ycoords'][1] == OtherMap.meta['ycoords'][1]):
            new_data[:OtherMap.data.shape[0],
                     -OtherMap.data.shape[1]:] = OtherMap.data

        elif new_meta['xcoords'][0] == OtherMap.meta['xcoords'][0] and new_meta['ycoords'][1] == OtherMap.meta['ycoords'][1]:
            new_data[:OtherMap.data.shape[0],
                     :OtherMap.data.shape[1]] = OtherMap.data

        elif (new_meta['xcoords'][1] == OtherMap.meta['xcoords'][1] and
              new_meta['ycoords'][0] == OtherMap.meta['ycoords'][0]):
            new_data[-OtherMap.data.shape[0]:,
                     -OtherMap.data.shape[1]:] = OtherMap.data

        return SatMap(meta=new_meta, data=new_data)

    def __sub__(self, OtherMap):
        """
        A method allowing SatMap objects to be subtracted from one another
        with the syntax "a - b".

        Only SatMaps from the same instrument taken on different days can be
        subtracted from one another. The two must have at least one pixel of
        overlap. The resulting SatMap's data will be that of the overlap
        region only.       

        Parameters
        ----------
        OtherMap : SatMap
            The map whose data is to be subtracted from the first.

        Raises
        ------
        Exception
            SatMaps from different instruments or those taken on the same day 
            cannot be subtracted from one another, and will raise errors. 

        Returns
        -------
        SatMap
            The sat map containng the difference in data between the two being
            subtracted. This SatMap will have the shape of their overlapping
            region.

        Example
        -------
        A typical subtraction

        >>> data1 = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta1 = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'resolution': 2, 'xcoords': [0., 6.], 'ycoords': [2., 8.]}
        >>> map1 = SatMap(meta1, data1)
        >>> data2 = np.array([[0,1,1], [0,0,1], [0,0,0]])
        >>> meta2 = {'date': '2022-12-02','time': '21:43:42', 'instrument': 'lir', 'resolution': 2, 'xcoords': [0., 6.], 'ycoords': [2., 8.]}
        >>> map2 = SatMap(meta2, data2)
        >>> (map2-map1).data
        array([[ 0,  1,  0],
               [ 0,  0,  0],
               [ 0,  0, -1]])

        """

        if self.meta['instrument'] != OtherMap.meta['instrument']:
            raise Exception("Different instrument")

        if self.meta['date'] == OtherMap.meta['date']:
            raise Exception("Same date")

        if (self.meta['xcoords'][1] < OtherMap.meta['xcoords'][0] or
            self.meta['xcoords'][0] > OtherMap.meta['xcoords'][1] or
            self.meta['ycoords'][1] < OtherMap.meta['ycoords'][0] or
                self.meta['ycoords'][0] > OtherMap.meta['ycoords'][1]):
            raise Exception("Non-overlapping images")

        new_meta = self.meta.copy()
        new_meta['time'] = self.meta['time']+','+OtherMap.meta['time']
        new_meta['date'] = self.meta['date']+',' + OtherMap.meta['date']

        new_meta['xcoords'] = (max(self.meta['xcoords'][0],
                                   OtherMap.meta['xcoords'][0]),
                               min(self.meta['xcoords'][1],
                                   OtherMap.meta['xcoords'][1]))

        new_meta['ycoords'] = (max(self.meta['ycoords'][0],
                                   OtherMap.meta['ycoords'][0]),
                               min(self.meta['ycoords'][1],
                                   OtherMap.meta['ycoords'][1]))

        arry_shape_0 = round(
            (new_meta['ycoords'][1] - new_meta['ycoords'][0])
            / new_meta['resolution'])
        arry_shape_1 = round(
            (new_meta['xcoords'][1] - new_meta['xcoords'][0])
            / new_meta['resolution'])

        # This seems like an unnecessary step, leaving it in for now.
        new_data = np.zeros((arry_shape_0, arry_shape_1))

        # Placing in positive data
        if (new_meta['xcoords'][0] == self.meta['xcoords'][0] and
                new_meta['ycoords'][0] == self.meta['ycoords'][0]):
            new_data = self.data[-new_data.shape[0]:, :new_data.shape[1]]

        elif (new_meta['xcoords'][1] == self.meta['xcoords'][1] and
              new_meta['ycoords'][1] == self.meta['ycoords'][1]):
            new_data = self.data[:new_data.shape[0], -new_data.shape[1]:]

        elif (new_meta['xcoords'][0] == self.meta['xcoords'][0] and
              new_meta['ycoords'][1] == self.meta['ycoords'][1]):
            new_data = self.data[:new_data.shape[0], :new_data.shape[1]]

        elif (new_meta['xcoords'][1] == self.meta['xcoords'][1] and
              new_meta['ycoords'][0] == self.meta['ycoords'][0]):
            new_data = self.data[-new_data.shape[0]:, -new_data.shape[1]:]

        # Subtracting negative data
        if (new_meta['xcoords'][0] == OtherMap.meta['xcoords'][0] and
                new_meta['ycoords'][0] == OtherMap.meta['ycoords'][0]):
            new_data = new_data-OtherMap.data[-new_data.shape[0]:,
                                              :new_data.shape[1]]

        elif (new_meta['xcoords'][1] == OtherMap.meta['xcoords'][1] and
              new_meta['ycoords'][1] == OtherMap.meta['ycoords'][1]):
            new_data = new_data-OtherMap.data[:new_data.shape[0],
                                              -new_data.shape[1]:]

        elif (new_meta['xcoords'][0] == OtherMap.meta['xcoords'][0] and
              new_meta['ycoords'][1] == OtherMap.meta['ycoords'][1]):
            new_data = new_data-OtherMap.data[:new_data.shape[0],
                                              :new_data.shape[1]]

        elif (new_meta['xcoords'][1] == OtherMap.meta['xcoords'][1] and
              new_meta['ycoords'][0] == OtherMap.meta['ycoords'][0]):
            new_data = new_data-OtherMap.data[-new_data.shape[0]:,
                                              -new_data.shape[1]:]

        return SatMap(meta=new_meta, data=new_data)

    def mosaic(self, OtherMap, resolution=None, padding=True):
        """
        Takes two SatMaps and makes a mosaic: an image with the data of both, 
        including in overlap regions.

        A mosaic is similar to an addition of two SatMaps, but a mosaic can be
        created between SatMaps from different instruments, and of different
        resolutions.

        Parameters
        ----------
        OtherMap : SatMap
            The SatMap to be mosaiced.
        resolution : float, optional
            The resolution of the final image. 
            The default is the lower of the two resolutions of the input
            SatMaps.
        padding : bool, optional
            When True, the final image will be the smallest possible which
            contains all the data in both inputs to the mosaic.
            When False, the final image will be the largest possible which 
            contains no pixels without any data.
            The default is True.

        Raises
        ------
        Exception
            If the resolution doesn't evenly divide the FOV of both inputs.

        Returns
        -------
        new_Satmap : SatMap
            The SatMap containing the mosaiced data of the two original images.

        Example
        -------
        >>> data1 = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta1 = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'observatory': 'aigean', 'resolution': 3, 'xcoords': [0., 9.], 'ycoords': [0., 9.]}
        >>> map1 = SatMap(meta1, data1)
        >>> data2 = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta2 = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'observatory': 'aigean', 'resolution': 2, 'xcoords': [7., 11.], 'ycoords': [0., 4.]}
        >>> map2 = SatMap(meta2, data2)
        >>> map1.mosaic(map2)
        Traceback (most recent call last):
            ...
        Exception: Changes in resolution may necessitate changes in field-of-view

        """
        if self.meta['date'] != OtherMap.meta['date']:
            raise Exception("Different date")

        if (self.meta['xcoords'][1] < OtherMap.meta['xcoords'][0] or
            self.meta['xcoords'][0] > OtherMap.meta['xcoords'][1] or
            self.meta['ycoords'][1] < OtherMap.meta['ycoords'][0] or
                self.meta['ycoords'][0] > OtherMap.meta['ycoords'][1]):
            raise Exception("Non-overlapping images")

        map_1 = copy.deepcopy(self)
        map_2 = copy.deepcopy(OtherMap)

        if map_1.meta['resolution'] == map_2.meta['resolution']:
            raise Exception(
                "The resolution of two maps are the same, please use '+'")

        if resolution is None:
            resolution = min(map_1.meta['resolution'],
                             map_2.meta['resolution'])
            if map_1.meta['resolution'] == resolution:
                factor = map_2.meta['resolution'] / resolution
                map_2.data = rescale(map_2.data, factor)
                map_2.meta['resolution'] = resolution
            else:
                factor = map_1.meta['resolution'] / resolution
                map_1.data = rescale(map_1.data, factor)
                map_1.meta['resolution'] = resolution
        else:
            factor1 = map_1.meta['resolution'] / resolution
            map_1.data = rescale(map_1.data, factor1)
            map_1.meta['resolution'] = resolution

            factor2 = map_2.meta['resolution'] / resolution
            map_2.data = rescale(map_2.data, factor2)
            map_2.meta['resolution'] = resolution

        if (map_1.fov[0] % map_1.meta['resolution'] != 0 or
            map_1.fov[1] % map_1.meta['resolution'] != 0 or
            map_2.fov[0] % map_1.meta['resolution'] != 0 or
                map_2.fov[1] % map_1.meta['resolution'] != 0):
            raise Exception(
                'Changes in resolution may necessitate changes in field-of-view')

        if padding:
            new_Satmap = map_1+map_2
            new_Satmap.meta['instrument'] = map_1.meta['instrument'] + \
                ','+map_2.meta['instrument']
            return new_Satmap

        else:
            if self.fov[0]*self.fov[1] > OtherMap.fov[0]*OtherMap.fov[1]:
                new_Satmap = map_1+map_1
                new_Satmap.meta['instrument'] = map_1.meta['instrument'] + \
                    ','+map_2.meta['instrument']
                return new_Satmap
            else:
                new_Satmap = map_2+map_2
                new_Satmap.meta['instrument'] = map_1.meta['instrument'] + \
                    ','+map_2.meta['instrument']
                return new_Satmap

    def visualise(self, save=False, savepath='.'):
        """
        Creates a figure to visualise the data in a SatMap using matplotlib.

        Parameters
        ----------
        save : bool, optional
            When True, creates a file. The default is False.

        savepath : str, optional
            The path of the directory to save the file to. 
            The default location is the current working directory.

        **kwargs : TYPE
            DESCRIPTION.

        Returns
        -------
        path : path
            If save=True, the function returns the path of the saved file.

        Example
        -------
        >>> data = np.array([[0,0,1], [0,0,1], [0,0,1]])
        >>> meta = {'date': '2022-12-01','time': '21:43:42', 'instrument': 'lir', 'observatory': 'aigean', 'resolution': 1, 'xcoords': [4., 7.], 'ycoords': [6., 9.]}
        >>> map = SatMap(meta, data)
        >>> map.visualise(save=True, savepath='.')
        'aigeanlir20221201214342.png'

        >>> os.remove('aigeanlir20221201214342.png')

        """

        plt.imshow(self.data, cmap='viridis', extent=(
            self.meta['xcoords'][0], self.meta['xcoords'][1], self.meta['ycoords'][0], self.meta['ycoords'][1]))
        plt.colorbar(label="Depth", orientation="vertical")

        if save:
            filename = self.meta['observatory']+self.meta['instrument'] + \
                self.meta['date'].replace(
                    '-', '')+self.meta['time'].replace(':', '')+'.png'

            path = os.path.join(savepath, filename)
            plt.savefig(path)
            return filename

        else:
            plt.show()


def get_satmap(filename: str):
    """
    Takes a string specifying a data file produced by Aigean, and converts 
    said file into a SatMap object.

    Parameters
    ----------
    filename : str
        The name of the file to be converted. 
        If the file is not in the working directory the path will also need to
        be specified.
        Files can be found at https://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/
        Currently, only asdf, hdf5, and zip files holding a json are supported.

    Raises
    ------
    Exception
        Throws an error when an inappropriate file name is supplied.

    Returns
    -------
    SatMap
        SatMap containing the data and metadata of the file.

    Example
    -------
    >>> get_satmap('theresnodogthere.asdf')
    Traceback (most recent call last):
        ...
    Exception: File does not exist

    """

    if "asdf" in filename:
        try:
            af = asdf.open(filename)
        except:
            raise Exception('File does not exist')
        meta = get_meta(dict(af))
        data = af['data'][:]
        return SatMap(meta, data)

    elif "hdf5" in filename:
        try:
            f = h5py.File(filename, 'r')
        except:
            raise Exception('File does not exist')
        meta = {}
        for key in f.attrs.keys():
            meta[key] = f.attrs[key]
        for key in f['observation'].attrs.keys():
            meta[key] = f['observation'].attrs[key]
        data = f['observation']['data'][:]
        return SatMap(meta, data)

    elif "zip" in filename:
        try:
            zip_file = io.BytesIO(open(filename, "rb").read())
        except:
            raise Exception('File does not exist')

        with ZipFile(zip_file, 'r') as zf:
            with zf.open("observation.npy") as f:
                data = np.load(f)
            with zf.open("metadata.json") as f:
                meta = json.load(f)
        return SatMap(data=data, meta=meta)

    elif "ecn" in filename:
        raise ValueError(
            "Data from the Ecne instrument cannot be put into a SatMap, since it doesn't contain an image.")

    else:
        raise Exception("Unknown file type")


if __name__ == "__main__":
    import doctest
    doctest.testmod()
