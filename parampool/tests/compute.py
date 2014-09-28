import numpy as np

def mysimplefunc(a, b, c, d=None):
    return a, b, c, d

class MySpecialClass:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return 'MySpecialClass(%s)' % self.x

def myfunc(a=1.2, b=2, c='some text', d=None,
           e=[1,2,3], f=(4,5,6), g=np.array([-1,1]),
           h=MySpecialClass(6), i=True):
    """
    This function does not compute anything - it just returns the
    value of the input parameters as altered by the user.

    However, inside the function we do calculate the heavy formula

    !bt
    \[ Q = e^{-ab}\sin(\pi g_0),\]
    !et
    where $g_0$ is the first element in the `g` array.

    The various input parameters are

    |------------------------|
    | variable | type        |
    |--l----------l----------|
    | `a`      | f           |
    | `b`      | integer     |
    | `c`      | text        |
    | `d`      | anything    |
    | `e`      | list        |
    | `f`      | tuple       |
    | `g`      | numpy array written with list syntax |
    | `h`      | user-defined instance of type `MySpecialClass` |
    | `i`      | boolean     |
    |------------------------|

    # (DocOnce format)
    """
    r = '<!-- Special formatting of the data: -->\n'
    var = 1  # must be defined as variable before iterating over locals()
    for var in sorted(locals()):
        if var not in ('r', 'var'):
            r += '<tt><font color="red">%s</font>: ' % var + repr(locals()[var]) + '</tt><br>\n'
    # Do as promised in the doc string
    from math import sin, exp, pi
    try:
        g0 = g[0]  # works only if g is an array...
        Q = exp(-a*b)*sin(g0*pi)
    except:
        pass
    return r
