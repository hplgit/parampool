======= Parampool: Handling a pool of input parameters in scientific applications =======

The `parampool` package is a tool for administering a pool of parameters
in scientific applications. The package contains

 * a general tree data structure in Python (subpackage `tree`),
 * an application of the tree structure to pools of input parameters
   for simulation programs (subpackage `pool`),
 * tools for automatic generation of web-based user interfaces
   (subpackage `generator`), based on a pool or just a function.

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

Replace `flask` by `django` and you get a Django-based user interface
instead (!).

===== Killer demo: make a pool tree =====

The user interface above was based on inspecting a Python function and
its keyword arguments and default values.
To get more control of the user interface, you can specify all the
input parameters as a hierarichal tree, called *pool tree*. Here is an example:

 * Main pool
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

@@@CODE doc/src/pp/src-pp/compute.py fromto: def pool_definition_list@def convert_time_step

There is more to learn when specifying a *pool* of parameters (compared to just
providing a compute function), but you also get a lot fancier
web-based graphical user interface or command-line (or file) interface.
The interfaces are automatically generated with very few lines of code.

FIGURE: [doc/src/pp/fig-pp/flask_pool1_filled.png, width=800]

You can freely choose between a Flask or Django application for realizing the
user interface.

Read the "tutorial": "http://hplgit.github.io/parampool/doc/pub/pp.html"
to learn how to use Parampool!
