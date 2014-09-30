# Define input data as a tree (menu and submenus)
# tree = list of (menu_name, menu_list_of_dicts)
from math import pi

menu_tree = [
    'main', [
        dict(name='print intermediate results', default=False),
        dict(name='U', default=120, unit='km/h',
             help='velocity of body', str2type=eval),
        'fluid properties', [
            dict(name='rho', default=1.2, unit='kg/m**3',
                 help='density'),
            dict(name='mu', default=2E-5, help='viscosity'),
            ],
        'body properties', [
            dict(name='m', default=0.43, unit='kg', help='mass'),
            dict(name='V', default=pi*0.11**3, help='volume'),
            dict(name='A', default=pi*0.11**2, unit='m**2',
                 help='cross section area'),
            dict(name='d', default=2*0.11, unit='m',
                 help='diameter'),
            dict(name='C_D', default=0.2, minmax=[0,1],
                 help='drag coefficient'),
            ],
        ],
    ]
