import numpy as np

class MySpecialClass:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return 'MySpecialClass(%s)' % self.x

def myfunc(a=1.2, b=2, c='some text', d=None,
           e=[1,2,3], f=(4,5,6), g=np.array([-1,1]),
           h=MySpecialClass(6)):
    r = '<!-- Special formatting of the data: -->\n'
    var = 1  # must be defined as variable before iterating over locals()
    for var in locals():
        if var not in ('r', 'var'):
            r += '<pre>\n' + repr(locals()[var]) + '\n</pre>\n'
    return r
