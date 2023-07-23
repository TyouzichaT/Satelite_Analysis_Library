"""
test_aigean.py

This file contains all the unit tests for the aigean module.

Tests are aranged into classes based on the aspect of the module being tested
"""

import asdf
import h5py
import zipfile
import json
import csv
import numpy as np
import pytest
import unittest
from ..net import *
from ..analysis import *
from unittest.mock import patch
from aigeanpy import satmap
import random

##############################################################################

"""
Trial data to be used in subsequent testing
"""

# Dummy Arrays
data_1 = np.array([[1,1,1], [0,0,0], [0,0,0]])
data_1_old = data_1.copy()
meta_1 = {'date': '2022-12-01', 'instrument': 'lir', 'time': '21:43:42', 
          'resolution': 1, 'xcoords': [0., 3.], 'ycoords': [0., 3.]}
meta_1_old = meta_1.copy()
map_1 = satmap.SatMap(meta_1, data_1)


map_1x = satmap.SatMap(meta_1.copy(), data_1.copy())
map_1x.meta['date'] = '2022-12-02'

map_1_reso2 = satmap.SatMap(meta_1.copy(), data_1.copy())
map_1_reso2.meta['resolution'] = 2


data_2= np.array([[0,0,1], [0,0,1], [0,0,1]])
meta_2 = {'date': '2022-12-01', 'time': '21:43:42', 'instrument': 'lir',
          'resolution': 1, 'xcoords': [2., 5.], 'ycoords': [1., 4.]}
map_2 = satmap.SatMap(meta_2, data_2)


data_3= np.array([[.1,.4,.9], [.1,.2,.3], [.1,.1,.1]])
meta_3 = {'date': '2022-12-02', 'time': '21:43:42', 'instrument': 'lir',
          'resolution': 1, 'xcoords': [1., 4.], 'ycoords': [1., 4.]}
map_3 = satmap.SatMap(meta_3, data_3)


# Real data
prefix="aigeanpy//tests//test-files//"
lir_0105_0 = satmap.get_satmap(prefix+'aigean_lir_20230105_135624.asdf')
lir_0105_1 = satmap.get_satmap(prefix+'aigean_lir_20230105_142424.asdf')
man_0105_0 = satmap.get_satmap(prefix+'aigean_man_20230105_135624.hdf5')
man_0105_1 = satmap.get_satmap(prefix+'aigean_man_20230105_141024.hdf5')
fan_0105_0 = satmap.get_satmap(prefix+'aigean_fan_20230105_135624.zip')
fan_0105_1 = satmap.get_satmap(prefix+'aigean_fan_20230105_140724.zip')
fan_0105_2 = satmap.get_satmap(prefix+'aigean_fan_20230105_142624.zip')
lir_0106_0 = satmap.get_satmap(prefix+'aigean_lir_20230106_125938.asdf')
fan_0106_0 = satmap.get_satmap(prefix+'aigean_fan_20230106_131838.zip')




##############################################################################

class TestQuery(unittest.TestCase):
    @patch.object(requests, 'get', side_effect=ConnectionError)
    def test_get_query_isa_timeout(self, mock_requests):
        with self.assertRaises(ConnectionError):
            query_isa('2022-12-08', '2022-12-09', 'Lir')


class TestGetSatMap:
    """
    Contains tests for the get_satmap fucntion
    """
    def test_get_ecne_satmap(self):
        with pytest.raises(ValueError):
            satmap.get_satmap('aigeanpy/tests/test-files/aigean_ecn_20230105_135624.csv')
    

class TestSatMapInit:
    """
    A class containing unit tests for SatMap initialisation.
    
    """
    
    def test_init_inputs(self):
        """
        Negative tests on the variables suplied to satmap.SatMap()
        """
        data = np.array([[1,1,1],[0,0,0],[0,0,0]])
        meta = {'date': '2022-12-01', 'instrument': 'lir', 'time': '21:43:42',
                'resolution': 1, 'xcoords': [0., 3.], 'ycoords': [0., 3.]}
        with pytest.raises(TypeError):
            meta_wrong_type = meta.keys()
            satmap.SatMap(meta_wrong_type, data)
        with pytest.raises(TypeError):
            data_wrong_type = '1,1,1,,0,0,0,,0,0,0'
            satmap.SatMap(meta, data_wrong_type)
    
    
    def test_init_backaction(self):
        """
        Ensures the data used in forming a SatMap doesn't change as it does so.
        """
        data = np.array([[1,1,1], [0,0,0], [0,0,0]])
        meta = {'date': '2022-12-01', 'instrument': 'lir', 'time': '21:43:42',
                'resolution': 1, 'xcoords': [0., 3.], 'ycoords': [0., 3.]}
        data_old = data.copy()
        meta_old = meta.copy()
        map_new = satmap.SatMap(meta, data)
        assert np.array_equiv(data_old, data), (
            'The creation of the SatMap has altered the original raw data')
        assert meta_old == meta, (
            'The creation of the SatMap has altered the original metadata')
    
            
    def test_init_coordinates(self):
        """
        Negative test for bad coordinate ordering.
        """
        data = np.array([[1,1,1],[0,0,0],[0,0,0]])
        meta = {'date': '2022-12-01','instrument': 'lir','time': '21:43:42',
                'resolution': 1, 'xcoords': [3., 0.],'ycoords': [0., 3.]}
        with pytest.raises(ValueError):
            satmap.SatMap(meta, data)
            
    def test_resolution(self):
        """
        The resolution in the metadata should be the scale factor between
        the shape of the data and the size of the whole image in meters.
        
        Note that in numpy the first value of shape is the number of rows,
        i.e. the height of the image, corresponding to the y axis. 
        """
        x_size = map_1.meta['xcoords'][1] - map_1.meta['xcoords'][0]
        x_resolution = x_size / map_1.shape[1]
        assert x_resolution == map_1.meta['resolution']
        
        y_size = map_1.meta['ycoords'][1] - map_1.meta['ycoords'][0]
        y_resolution = y_size / map_1.shape[0]
        assert y_resolution == map_1.meta['resolution']
        
        
class TestSatMapCoords:
    """
    Tests for the two coordinate transformation methods for SatMaps, 
    easrth_to_pixel and pixel_to_earth.
    """
    
    def test_coordinate_transforms(self):
        """
        Makes sure converting to and from earth-pixel coordinate systems gets 
        you back to where you were.
        """
        assert map_1.pixel_to_earth(map_1.earth_to_pixel(.5,.5)[0],
                                    map_1.earth_to_pixel(.5,.5)[1]) == (.5,.5)


class TestSatMapAddSub:
    """
    Tests for SatMap method __add__ and __sub__.
    """

    def test_self_addition(self):
        """
        The data of a satmap should be unchanged when added to itself.
        """
        assert np.array_equiv((map_1+map_1).data, map_1.data)

        
    def test_addition(self):
        """
        A typical addition. As currently written, the second satmap overwrites
        the first where they overlap. 
        """
        assert np.array_equiv((map_1+map_2).data, np.array([[0, 0, 0, 0, 1],
                                                            [1, 1, 0, 0, 1],
                                                            [0, 0, 0, 0, 1],
                                                            [0, 0, 0, 0, 0]]))
    
    def test_addition_multiple(self):
        """
        Ensures output of addition can itself undergo addition.
        """
        two_maps = fan_0105_0+fan_0105_1
        try:
            three_maps = two_maps + fan_0105_2         
        except:
            assert False, 'The output of __add__ was not able to be used as an input for __add__'
        else:
            assert True
    
    def test_addition_no_overlap(self):
        """
        Assuring correct shape for addition of two distant images.
        """
        fan_add = fan_0105_0 + fan_0105_2
        expected_fov = (975, 200)
        assert fan_add.fov == expected_fov
        assert fan_add.shape == (200//5, 975//5)
        
        
    def test_addition_criteria_day(self):
        """
        Negative test for adding SatMaps from different days.
        """
        with pytest.raises(Exception):
            map_1 + map_3
            
    def test_addition_criteria_resolution(self):
        """
        Negative test for adding SatMaps from different instruments.
        """
        with pytest.raises(Exception):
            map_1 + map_1_reso2
            
    
    def test_self_subtraction(self):
        """
        Tests that an image subtracted from itself gives an empty array.
        """
        assert np.array_equiv((map_1-map_1x).data, np.zeros(map_1.data.shape))
        
        
    def test_subtraction(self):
        """
        A typical subtraction.
        """
        
        ms = (map_1-map_3)
        
        assert np.array_equiv(ms.data, np.array([[0.9, 0.8],[-0.1, -0.1]]))
        
class TestSatMapMosaic:
    """
    Tests for the mosaic function
    """
    def test_mosaic_same_instrument(self):
        """
        A negative test for mosaicing images of the same resolution.
        
        As currently written, images from the same instrument should just be
        added (via the __add__ method).
        """
        with pytest.raises(Exception):
            lir_0105_0.mosaic(lir_0105_1)
            
    def test_mosaic_resolutions(self):
        """
        Testing shape of data for mosaic of lir and manannan data.
        
        """
        expected_size = (600, 400)
        resolutions = [1, 2, 10]
        for res in resolutions:
            lir_man_mosaic = lir_0105_0.mosaic(man_0105_1,
                                               padding=True,
                                               resolution=res)
            assert lir_man_mosaic.shape == (expected_size[1]/res,
                                            expected_size[0]/res)
            
    def test_mosaic_commutative(self):
        """
        Testing shape of mosaic of Manannan and Fand is commutative.
        """
        man = man_0105_1
        fan = fan_0105_2
        assert np.all(man.mosaic(fan).data - fan.mosaic(man).data)==0
        
        
def test_backaction():
    """
    After all the testing has been done the same data will have been used 
    repeatedly. This test ensures input data is unchanged by the processing.
    """
    assert np.array_equiv(data_1, data_1_old)
    assert meta_1 == meta_1_old


def generate_data(points_num,dim_num,low,high):
    data=np.zeros((points_num,dim_num))
    for dim in range(dim_num):
        data[:,dim]= np.random.uniform(low,high,points_num)
    return data

def cluster_2data():
    data1=generate_data(100,3,1,5)
    data2=generate_data(100,3,-5,-10)
    data=np.vstack((data1,data2))
    index=[[i for i in range(100)],[i for i in range(100,200)]]
    return data, index


def test_kmeans():
    f1,indice1 = cluster_2data()
    np.savetxt('sample_cluster.csv', f1, delimiter=',')

    list1= kmeans('sample_cluster.csv',2,10,False)
    list2= kmeans('sample_cluster.csv',2,10,True)

    os.remove('sample_cluster.csv')

    flag1=0
    flag2=0
    for list in indice1:
        for l in list1:
            if l==list:
                flag1=flag1+1
        for k in list2:
            if k==list:
                flag2=flag2+1
    if flag1==2 and flag2==2:
        assert True
    else:
        assert False

    