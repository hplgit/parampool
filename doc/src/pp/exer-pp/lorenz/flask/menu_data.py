def pool_function():
    pool_tree = [
        'Lorenz data', [
            dict(name='T', default=50, widget='float',
                help='End time'),
            dict(name='N', default=100000, widget='integer',
                help='Number of time steps'),
            dict(name='video', default=False, widget='checkbox',
                help='Display a video. WARNING: May take several minutes'),
            'Initial condition', [
                dict(name='x0', default=1, widget='float',
                     help='Initial condition in x-direction',
                     symbol='x_0'),
                dict(name='y0', default=0, widget='float',
                     help='Initial condition in y-direction',
                     symbol='y_0'),
                dict(name='z0', default=0, widget='float',
                     help='Initial condition in z-direction',
                     symbol='z_0'),
                ],
            'Lorenz parameters', [
                dict(name='sigma', default=10.,
                     symbol='\\sigma'),
                dict(name='rho', default=28.,
                     symbol='\\rho'),
                dict(name='beta', default='8.0/3', str2type=eval, symbol='\\beta'),
                ],
            ],
        ]
    from parampool.pool.UI import listtree2Pool
    return listtree2Pool(pool_tree)
