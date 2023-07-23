# Useage

Aigeanpy is designed to process data from the Aigean observatory of the Irish Space Agency.

Data is stored at the [ISA Archive](https://dokku-app.dokku.arc.ucl.ac.uk/isa-archive/), where there is instructions on how to query and download files manually. Alternatively, check out the `aigeanpy.net` module for fetching data in-line.

The package has two main modules, `aigeanpy.satmap` and `aigeanpy.clustering`.


## `satmap`

The `satmap` module is used for storing and manipulating image data from the Aigean observatory, currently supplied by the Lir, Fand, and Manannan instruments. 

The chief object in the module is the `SatMap`, which contains both image data and metadata. 

The module is equiped with a function `get_satmap()` which takes as it's argument a file path, and returns a `SatMap` object.


## `clustering`

Contains an iterative algorithm for grouping a csv file of data into clusters of similar points.


# Tutorial

Lets start with fetching some data from the ISA archive website. Suppose we want to see the data taken by the Lir instrument on 05/01/2023:

```
from aigeanpy.net import query_isa, download_isa
query_isa('2023-01-05', '2023-01-05', 'Lir')
```

Note that the second date supplied will query the database up to ***and including*** that date. Your output should look something like this:

``` 
[{'date': '2023-01-05',
  'filename': 'aigean_lir_20230105_135624.asdf',
  'instrument': 'lir',
  'resolution': 30,
  'time': '13:56:24',
  'xcoords': [500.0, 1100.0],
  'ycoords': [0.0, 300.0]},
 {'date': '2023-01-05',
  'filename': 'aigean_lir_20230105_142424.asdf',
  'instrument': 'lir',
  'resolution': 30,
  'time': '14:24:24',
  'xcoords': [700.0, 1300.0],
  'ycoords': [0.0, 300.0]}]
```

From this, we can see filenames and metadata. To actually download one of these files (the first one, say) you can run

```
download_isa('aigean_lir_20230105_135624.asdf', 'C://Users//Owner//Desktop')
```

In this example we are working with windows, where folders need to be separated by "//" to avoid parsing errors. When you look in the directory you specified, you should find the file "aigean_lir_20230105_135624.asdf".

Now we have something to play with! Set your root directory to the directory holding the file, and convert the file into a SatMap object:

```
import aigeanpy.satmap as satmap
lir_map = satmap.get_satmap('aigean_lir_20230105_135624.asdf')
lir_map.visualise()
```

You should see a plot of the image.

Check out the documentation for `aigeanpy.satmap` to see what you can do with your new toy.


