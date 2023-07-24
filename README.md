# Satelite_Analysis_Library
This library is used to analyse data from different instruments on-board a satellite. The instruments provide daily updates from a piece of land that can be used to track water levels at different locations. The Irish Space Agency has launched Aigean, an Earth observation satellite to monitor an area around Lough Ree. Recently, rainfall has decreased in the area, and during the latest years droughts have become more frequent and more severe. With the instruments on board Aigean the scientific community will be able to obtain better data about the water levels and the erosion of the land, and therefore will be able to generate more accurate predictions.

The three imagers are called: **Lir**, **Manannan** and **Fand**.
- **Lir** has the largest field-of-view, but the smaller resolution with a pixel size of 20 m per pixel; 
- **Manannan** provides a smaller field-of-view with a better resolution of 10 m per pixel;
- **Fand** has the smallest field-of-view but a very high resolution of 1 m per pixel.

The radar is called **Ecne** and it provides three measurements for the deepest areas in the region. The measurements are turbulence, salinity and algal density for these points.

## Installation

```bash
pip install git+git://github.com/TyouzichaT/Satelite_Analysis_library
```

## Usage
    
Use it on your own library with:

```python
from aigeanpy import aigeanpy


```

# Running Tests

To run unit tests, navigate to the top level directory an run `pytest`. Simple!

To run doctests for a given script, you can call

``python <filepath> -v``

The `-v` marker is for verbose, so you will see the doctests even if they all pass.


# Building Documentation With Sphinx

To create the documentation, make sure you have sphinx and myst-parser installed.

Navigate to /docs/ and run

``sphinx-build . _html/build``

The front page of the doumentation is then found at `/docs/_html/build/index.html`.
