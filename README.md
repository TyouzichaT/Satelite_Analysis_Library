# aigeanpy-Working-Group-12 

Welcome to the aigeanpy package! This is a package providing some basic tools for reading and 
interpreting data from the Aigean observatory. It has been made as coursework for COMP0233 by
group 12.


## Installation

```bash
pip install git+git://github.com/TyouzichaT/Satelite_Analysis_lib
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
