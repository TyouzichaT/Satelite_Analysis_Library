from setuptools import find_packages, setup

REQUIRES = [
    "requests>=2.22.0",
    "asdf>=2.14.3",
    "matplotlib>=3.1.1",
    "numpy>=1.18",
    "h5py>=3.6.0",
    "pathlib>=1.0",
    "scikit-image>=0.19.0",
    "myst_parser>=0.15.0"
]

setup(
    name='aigeanpy',
    keywords="aigeanpy",
    packages=find_packages(exclude=['aigeanpy.tests']),
    version='0.1.0',
    description="An application for processing data from the Aigean observatory",
    install_requires = REQUIRES,
    author='COMP0223 Group 12',
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'aigean_today = aigeanpy.aigean_today:main',
            'aigean_metadata = aigeanpy.aigean_metadata:main',
            'aigean_mosaic = aigeanpy.aigean_mosaic:main'
        ]
    },
)