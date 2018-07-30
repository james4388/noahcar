h5py just hang when install with pip, need this first
```
git clone https://github.com/h5py/h5py.git
cd h5py
python setup.py install
```
but in order to install h5py you must have Cython compiler
```
git clone https://github.com/cython/cython.git
cd cython
python setup.py install
```
Ignore all of above, I use python 3.6 so there is no packages T__T. Switch back to 3.5 and everything is fine.
