# Topaspy package
TOPAS itself is a refinement program of exceptional speed, principally designed
for the performance of Rietveld and related methods on diffraction data, albeit
it can be extended to other datasets. Topaspy is an attempt to make a Python
frontend to this, so that those familiar with Python can utilise its ease of
syntax, built-in methods etc. to extend TOPAS' functionality. This is not a 
substitute for being able to write TOPAS input files. Topaspy has been tested
on TOPAS Academic v7 only.

## Installation
I recommend using a virtual environment (I use conda) with the following
```
conda env create -f environment.yml
```
I would also recommend including the jupyter package. Then 
```
conda activate topaspy_env
``` 
will ensure that you have a suitable environment. Navigate to the reforms 
folder and run 
```
pip install .
```
You don't have to make a virtual environment (nor use conda) but it's highly
recommended.

## Author
This code was written by Tom Wood (Science & Technology Facilities Council,
Rutherford Appleton Laboratory, Harwell Oxford, Didcot, OX11 0QX; email:
thomas.wood@stfc.ac.uk).

## Licence
The copyright rests with the author and with STFC. 