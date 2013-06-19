import os
import numpy as np

def compute_average(data=np.array([1,2]), filename=None):
    if filename is not None:
        data = np.loadtxt(os.path.join('uploads', filename))
        what = 'file data'
    else:
        what = 'array'
    return 'mean of %s: %.3g<br>\nstandard deviation: %.3g' % \
           (what, np.mean(data), np.std(data))
