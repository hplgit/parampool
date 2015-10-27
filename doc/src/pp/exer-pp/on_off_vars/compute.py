import numpy as np
from math import pi, sqrt, sin, cos
import os

def formula(x=1.0, c0=0.0, c1=1.0, p1=0.0, p2=0.0,
            include_p1=True, include_p2=True):
    r = c0 + c1*x
    if include_p1:
        r += x**p1
    if include_p2:
        r += x**p2
    return r

if __name__ == '__main__':
    r = 2 + 4*0 + 0**0 + 0**0
    assert formula(0, c0=2, c1=4, p1=0, p2=0,
                   include_p1=True, include_p2=True) == r
    r = 2 + 4*2 + 2**3
    assert formula(2, c0=2, c1=4, p1=3, p2=2,
                   include_p1=True, include_p2=False) == r
