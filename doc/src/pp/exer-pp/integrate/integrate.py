def pool_def_api():
    from parampool.pool.Pool import Pool
    pool = Pool()
    pool.subpool('Main pool')
    pool.add_data_item(name='Expression to be integrated',
                       default='sin(x)', widget='textline')
    pool.add_data_item(name='a', default=0.0, symbol='a')
    pool.add_data_item(name='b', default=1.0, symbol='b')

    return pool

def compute(pool):
    string_expression = pool.get_value('Expression to be integrated')
    a = pool.get_value('a')
    b = pool.get_value('b')
    expr, I = integrate(string_expression, a, b)
    if isinstance(I, str):
        # Symbolic expression in latex
        import sympy as sym
        print sym.latex(expr), I
        return '\( \int %s dx = %s \)' % (sym.latex(expr), I)
    elif isinstance(I, (int,float)):
        return 'Numerical integration of '\
               '\( \int_{a=%s}^{b=%s}%s dx: %.4f' % \
               (a, b, sym.latex(expr), I)

def integrate(string_expression, a, b):
    assert isinstance(string_expression, str)
    import sympy as sym
    expr = sym.sympify(string_expression)
    x = sym.Symbol('x')
    I = sym.integrate(expr, x)
    if isinstance(I, sym.Integral):
        # Did not succeed to integrate symbolically
        f = sym.lambdify([x], expr)  # Python function
	I = trapezoidal(f, a, b, n=100)
    else:
        I = sym.latex(I)  # make LaTeX expression
    return expr, I  # str if symbolic, float if numerical integration

def trapezoidal(f, a, b, n):
    h = (b-a)/float(n)
    import numpy as np
    x = np.linspace(a, b, n+1)
    I = h*(sum(f(x)) - 0.5*(f(a) + f(b)))
    return I
