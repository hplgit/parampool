======= Parampool: Handling a Pool of Input Parameters in Scientific Applications =======

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

===== Killer demo: write your computational Python function =====

Here is a Python function taking some arguments, calling up computations,
and returning the results as HTML code to be displayed in a browser
(e.g., two plots and a table of results):

@@@CODE doc/src/pp/src-pp/compute.py fromto: def compute_motion_and_forces@"""

Here is the Python code you need to write in order to generate a
graphical user interface in a web browser:

@@@CODE doc/src/pp/src-pp/flask4/generate.py

The result is a "Flask": "http://flask.pocoo.org/" application.
Running `python controller.py` and opening a web browser provide access
to the user interface. You can fill in values, press *Compute*, and
get results back.

FIGURE: [doc/src/pp/fig-pp/flask4.png, width=850]

Replace "flask" by "django" and you get a Django-based user interface
instead (!).

===== Killer demo: make a menu tree =====

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

@@@CODE doc/src/pp/src-pp/compute.py fromto: def menu_definition_list@def convert_time_step

There is more to learn when specifying a menu, but you also get a lot fancier
web-based graphical user interface. The interface is automatically generated
with very few lines of code.

FIGURE: [doc/src/pp/fig-pp/flask_menu1_filled.png, width=800]

You can freely choose between a Flask or Django for realizing the
user interface.

A tutorial is in the writings (see `doc/src/pp`).
You need the tutorial be able to use the package.


