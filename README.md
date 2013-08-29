## Parampool: Organization of Parameters in Trees

The `parampool` package is a tool administering a pool of parameters
in scientific applications. The package contains

 * a general tree data structure in Python (subpackage `tree`),

 * an application of the tree structure to menus of input parameters
   for simulation programs (subpackage `menu`),

 * tools for automatic generation of web-based user interfaces
   (subpackage `generator`), based on a menu or just a function.

With `parampool` it is very easy to equip a scientific application with
various kinds of user interfaces: graphical via web, command line,
and file input.

#### Killer demo: write your computational Python function

Here is a Python function taking some arguments, calling up computations,
and returning the results as HTML code to be displayed in a browser
(e.g., two plots and a table of results):


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.Python}
def compute_motion_and_forces0(
    initial_velocity=5.0,
    initial_angle=45.0,
    spinrate=50.0,
    w=0.0,
    m=0.1,
    R=0.11,
    method='RK4',
    dt=None,
    plot_simplified_motion=True,
    new_plot=True
    ):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is the Python code you need to write in order to generate a
graphical user interface in a web browser:


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.Python}
from parampool.generator.flask import generate
from compute import compute_motion_and_forces

generate(compute_motion_and_forces, MathJax=True)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The result is a [Flask](http://flask.pocoo.org/) application.
Running `python controller.py` and opening a web browser provide access
to the user interface. You can fill in values, press *Compute*, and
get results back.

![Web interface with two graphs.](doc/src/pp/fig-pp/flask4.png)

Replace "flask" by "django" and you get a Django-based user interface
instead (!).

#### Killer demo: make a menu tree

The user interface above was based on inspecting a Python function and
its keyword arguments and default values.
To get more control of the user interface, you can specify all the
input parameters as a hierarichal tree, called *menu tree*, say

 * Main menu

   * Initial motion data

     * Initial velocity: `initial_velocity`

     * Initial angle: `initial_angle`

     * Spinrate: `spinrate`


   * Body and environment data

     * Wind velocity: `w`

     * Mass: `m`

     * Radius: `R`


   * Numerical parameters

     * Method: `method`

     * Time step: `dt`


   * Plot parameters

     * Plot simplified motion: `plot_simplified_motion`

     * New plot: `new_plot`



In Python, this may take the form


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.Python}
def menu_definition_list():
    """Create and return menu defined through a nested list."""
    menu = [
        'Main', [
            'Initial motion data', [
                dict(name='Initial velocity', default=5.0),
                dict(name='Initial angle', default=45,
                     widget='range', minmax=[0,90], range_step=1),
                dict(name=r'Spinrate', default=50, widget='float',
                     unit='1/s'),
                ],
            'Body and environment data', [
                dict(name='Wind velocity', default=0.0,
                     help='Wind velocity in positive x direction.',
                     minmax=[-50, 50], number_step=0.5,
                     widget='float', str2type=float),
                dict(name='Mass', default=0.1, unit='kg',
                     validate=lambda data_item, value: value > 0),
                dict(name='Radius', default=0.11, unit='m'),
                ],
            'Numerical parameters', [
                dict(name='Method', default='RK4',
                     widget='select',
                     options=['RK4', 'RK2', 'ForwardEuler'],
                     help='Numerical solution method.'),
                dict(name='Time step', default=None,
                     widget='textline', unit='s'),
                ],
            'Plot parameters', [
                dict(name='Plot simplified motion', default=True),
                dict(name='New plot', default=True),
                ],
            ],
        ]
    from parampool.menu.UI import listtree2Menu
    menu = listtree2Menu(menu)
    return menu
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is more to learn when specifying a menu, but you also get a lot fancier
web-based graphical user interface. The interface is automatically generated
with very few lines of code.

![](doc/src/pp/fig-pp/flask_menu1_filled.png)

You can freely choose between a Flask or Django for realizing the
user interface.

A tutorial is in the writings (see `doc/src/pp`).
You need the tutorial be able to use the package.

