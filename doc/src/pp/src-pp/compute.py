import odespy
import numpy as np
from math import pi, sqrt, sin, cos
import matplotlib.pyplot as plt
import os
import collections

def aerodynamic_force(C, rho, A, v):
    return 0.5*C*rho*A*v**2

def forces(v_x, v_y, w, rho, A, C_D, C_L, m, g):
    # Absolute value of relative velocity
    v = sqrt((v_x - w)**2 + v_y**2)
    # Tangent vector (a, b)
    v_norm = sqrt(v_x**2 + v_y**2)
    a = v_x/v_norm
    b = v_y/v_norm
    i_t_x = a
    i_t_y = b
    # Normal vector
    if a > 0:
        i_n_x = -b
        i_n_y = a
    else:
        i_n_x = b
        i_n_y = -a

    drag_x = - aerodynamic_force(C_D, rho, A, v)*i_t_x
    drag_y = - aerodynamic_force(C_D, rho, A, v)*i_t_y
    lift_x = aerodynamic_force(C_L, rho, A, v)*i_n_x
    lift_y = aerodynamic_force(C_L, rho, A, v)*i_n_y
    gravity = -m*g
    return drag_x + lift_x, drag_y + lift_y + gravity

class Ball:
    """Data for a ball thrown through air."""
    def __init__(self, m, R, drag=True, spinrate=0, w=0):
        self.m, self.R, self.drag, self.spinrate, self.w = \
                m, R, drag, spinrate, w
        self.g = 9.81
        self.A = pi*R**2
        self.rho = 1.1184
        self.C_D = 0.47 if drag else 0
        self.C_L = spinrate/500.0*0.2

        # Initial position and velocity
        self.x0 = self.y0 = 0
        self.v_x0 = self.v_y0 = 1

    def set_initial_velocity(self, v_x, v_y):
        self.v_x0 = v_x
        self.v_y0 = v_y

    def get_initial_condition(self):
        return [self.x0,
                self.v_x0,
                self.y0,
                self.v_y0]

    def rhs(self, u, t):
        x, v_x, y, v_y = u
        F_x, F_y = forces(v_x, v_y, self.w, self.rho, self.A,
                          self.C_D, self.C_L, self.m, self.g)
        m = self.m
        return [v_x, F_x/m, v_y, F_y/m]

def solver(problem, method, dt):
    ode_solver = eval('odespy.' + method)(problem.rhs)
    ode_solver.set_initial_condition(
        problem.get_initial_condition())

    def terminate(u, t, step_no):
        y = u[step_no,2]
        return y <= 0

    # Estimate time of flight (drop aerodynamic forces)
    # y = v_y0*T - 0.5*g*T**2 = 0
    T = problem.v_y0/(0.5*problem.g)
    # Add 100% to account for possible lift force and longer flight
    T = 2*T
    N = int(round(T/float(dt)))
    t = np.linspace(0, T, N+1)

    u, t = ode_solver.solve(t, terminate)
    x = u[:,0]
    y = u[:,2]

    # Compute forces
    v_x = u[:,1]
    v_y = u[:,3]
    v = np.sqrt((v_x - problem.w)**2 + v_y**2)
    p = problem
    drag_force = aerodynamic_force(p.C_D, p.rho, p.A, v)
    lift_force = aerodynamic_force(p.C_L, p.rho, p.A, v)
    gravity_force = np.zeros(x.size) - p.m*p.g

    return x, y, t, gravity_force, drag_force, lift_force

def compute_drag_free_landing(initial_velocity, initial_angle):

    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)
    # m and R have no effect when gravity alone acts
    problem = Ball(m=0.1, R=0.11, drag=False, spinrate=0, w=0)
    problem.set_initial_velocity(v_x0, v_y0)
    # Estimate dt
    T = v_y0/(0.5*9.81); dt = T/500
    x, y, t, gravity, drag, lift = solver(problem, 'RK4', dt)
    landing_point = x[-1] # (better: find intersection point)
    return landing_point

def compute_drag_free_motion_plot(
    initial_velocity=5.0,
    initial_angle=45.0):

    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)
    # m and R have no effect when gravity alone acts
    problem = Ball(m=0.1, R=0.11, drag=False, spinrate=0, w=0)
    problem.set_initial_velocity(v_x0, v_y0)
    # Estimate dt
    T = v_y0/(0.5*9.81); dt = T/500
    x, y, t, gravity, drag, lift = solver(problem, 'RK4', dt)
    plt.figure()
    plt.plot(x, y)
    import time  # use time to make unique filenames
    filename = 'tmp_%s.png' % time.time()
    if not os.path.isdir('static'):
        os.mkdir('static')
    filename = os.path.join('static', filename)
    plt.savefig(filename)
    html_text = '<img src="%s" width="400">' % filename
    return html_text

def compute_drag_free_motion_plot2(
    initial_velocity=5.0,
    initial_angle=45.0,
    new_plot=True):

    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)
    # m and R have no effect when gravity alone acts
    problem = Ball(m=0.1, R=0.11, drag=False, spinrate=0, w=0)
    problem.set_initial_velocity(v_x0, v_y0)
    # Estimate dt
    T = v_y0/(0.5*9.81); dt = T/500
    x, y, t, gravity, drag, lift = solver(problem, 'RK4', dt)
    global fig_no
    if new_plot:
        fig_no = plt.figure().number
    else:
        try:
            plt.figure(fig_no)
        except NameError:
            fig_no = plt.figure().number

    plt.plot(x, y, label=r'$v=%g,\ \theta=%g$' %
             (initial_velocity, initial_angle))
    plt.legend()
    import time  # use time to make unique filenames
    filename = 'tmp_%s.png' % time.time()
    if not os.path.isdir('static'):
        os.mkdir('static')
    filename = os.path.join('static', filename)
    plt.savefig(filename)
    html_text = '<img src="%s" width="400">' % filename
    return html_text

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
    """
    This application computes the motion of a ball with radius R
    and mass m under the influence of gravity, air resistance (drag)
    and lift because of a given spinrate. The motion starts with
    a prescribed initial_velocity making an angle initial_angle
    with the ground. A wind velocity, positive in positive x direction,
    can also be given (w). Many numerical methods can be used to
    solve the equations of motion. Some legal names are ForwardEuler,
    RK2, RK4, and Fehlberg (adaptive Runge-Kutta 4/5 order).
    If the timestep dt is None, approximately 500 steps are used,
    but dt can also be given a desired float value.

    The boolean variable plot_simplified_motion adds the curve of
    the motion without drag and lift (the standard parabolic
    trajectory). This curve helps illustrate the effect of drag
    and lift. When new_plot is false (unchecked), the new computed
    curves are added to the previous ones since last time new_plot
    was true.

    # (DocOnce format)
    """
    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)

    if dt is None:
        # Estimate dt
        T = v_y0/(0.5*9.81)
        dt = T/500

    problem = Ball(m=m, R=R, drag=True,
                   spinrate=spinrate, w=w)
    problem.set_initial_velocity(v_x0, v_y0)
    x, y, t, g, d, l = solver(problem, method, dt)

    # Motion plot
    global motion_fig_no, forces_fig_no, xmax, ymax
    if new_plot:
        motion_fig_no = plt.figure().number
        forces_fig_no = plt.figure().number
        xmax = ymax = 0
    try:
        plt.figure(motion_fig_no)
    except NameError:
        motion_fig_no = plt.figure().number
        xmax = ymax = 0
    plt.plot(x, y, label='')
    xmax = max(xmax, x.max())
    ymax = max(ymax, y.max())
    if plot_simplified_motion:
        problem_simplified = Ball(m=m, R=R, drag=False,
                                  spinrate=0, w=0)
        problem_simplified.set_initial_velocity(v_x0, v_y0)
        xs, ys, ts, dummy1, dummy2, dummy3 = \
            solver(problem_simplified, method, dt)
        plt.plot(xs, ys, 'r--')
        xmax = max(xmax, xs.max())
        ymax = max(ymax, ys.max())
    plt.axis([x[0], xmax, 0, 1.2*ymax])
    plt.title('Trajectory')
    plt.legend(loc='upper left')

    import time  # use time to make unique filenames
    filename = 'tmp_motion_%s.png' % time.time()
    if not os.path.isdir('static'):
        os.mkdir('static')
    filename = os.path.join('static', filename)
    plt.savefig(filename)
    plotwidth = 400
    html_text = """
<table>
<tr>
<td valign="top"><img src="%(filename)s" width="%(plotwidth)s"></td>
""" % vars()

    # Force plot
    try:
        plt.figure(forces_fig_no)
    except NameError:
        forces_fig_no = plt.figure().number
    plt.plot(x, d/np.abs(g), label='drag vs gravity')
    if spinrate != 0:
        plt.plot(x, l/np.abs(g), label='lift vs gravity')
    plt.legend()
    plt.title('Forces')

    filename = 'tmp_forces_%s.png' % time.time()
    filename = os.path.join('static', filename)
    plt.savefig(filename)
    html_text += """\
<td valign="top"><img src="%(filename)s" width="%(plotwidth)s"></td>
</tr>
</table>
""" % vars()
    return html_text

# The following function has the same functionality as
# compute_motion_and_forces0 above, but has true math in
# the doc string and avoids plot files.

def compute_motion_and_forces(
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
    """
    This application computes the motion of a ball with radius $R$
    and mass $m$ under the influence of gravity, air drag and lift
    because of a given spinrate $\omega$. The motion starts with a
    prescribed initial velocity $v_0$ making an angle initial_angle
    $\theta$ with the ground. A wind velocity $w$, positive in
    positive $x$ direction, can also be given.

    The ordinary differential equation problem governing the
    motion reads

    !bt
    \begin{align*}
    m\frac{d^2\bm{r}}{dt^2} &= -mg\bm{j} -
    \frac{1}{2}C_D\varrho A v^2\bm{i}_t +
    \frac{1}{2}C_L\varrho A v^2\bm{i}_n\\
    \bm{r}(0) &= 0\bm{i} + 0\bm{j}\\
    \frac{d\bm{r}}{dt}(0) &= v_0\cos\theta\bm{i} + v_0\sin\theta\bm{j},
    \end{align*}
    !et
    where $\bm{i}$ and $\bm{j}$ are unit vectors in the $x$ and $y$
    directions, respectively, $g$ is the acceleration of gravity,
    $A$ is the cross section area normal to the motion, $\bm{i}_t$
    is a unit tangent vector to the trajectory, $\bm{i}_n$ is
    a normal vector (pointing upwards) to the trajectory,
    $C_D$ and $C_L$ are lift coefficients, and $\varrho$ is the
    air density. For a ball, $C_D$ is taken as 0.45, while
    $C_L$ depends on the spinrate through $C_L=0.2\omega/500$.

    Many numerical methods can be used to solve the problem.
    Some legal names are `ForwardEuler`, `RK2`, `RK4`,
    and `Fehlberg` (adaptive Runge-Kutta 4/5 order).  If the
    timestep `dt` is None, approximately 500 steps are used, but
    `dt` can also be given a desired `float` value.

    The boolean variable `plot_simplified_motion` adds the curve
    of the motion without drag and lift (the standard parabolic
    trajectory). This curve helps illustrate the effect of drag
    and lift. When `new_plot` is `False` (unchecked), the new
    computed curves are added to the previous ones since last
    time `new_plot` was true.

    # (DocOnce format)
    """
    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)

    if dt is None:
        # Estimate dt
        T = v_y0/(0.5*9.81)
        dt = T/500

    problem = Ball(m=m, R=R, drag=True,
                   spinrate=spinrate, w=w)
    problem.set_initial_velocity(v_x0, v_y0)
    x, y, t, g, d, l = solver(problem, method, dt)

    # Define global variables that can hold values from call to
    # call of this function
    global motion_fig_no, forces_fig_no, xmax, ymax, data

    if new_plot:
        motion_fig_no = plt.figure().number  # make new figure and get its no
        forces_fig_no = plt.figure().number
        xmax = ymax = 0
        data = []
    try:
        plt.figure(motion_fig_no)            # set plt back to existing figure
    except NameError:
        motion_fig_no = plt.figure().number
        xmax = ymax = 0
        data = []

    # Record data for this run
    latex_symbol = lambda symbol: r'\( %s \)' % symbol
    data.append(collections.OrderedDict([
        (latex_symbol('v_0'), initial_velocity),
        (latex_symbol(r'\theta'), initial_angle),
        (latex_symbol(r'\omega'), spinrate),
        (latex_symbol('w'), w),
        (latex_symbol('m'), m),
        (latex_symbol('R'), R),
        ('method', method),
        (latex_symbol(r'\Delta t'), dt),
        ('landing point', x[-1])]))

    # Motion plot
    plt.plot(x, y, label='')
    xmax = max(xmax, x.max())
    ymax = max(ymax, y.max())
    if plot_simplified_motion:
        problem_simplified = Ball(m=m, R=R, drag=False,
                                  spinrate=0, w=0)
        problem_simplified.set_initial_velocity(v_x0, v_y0)
        xs, ys, ts, dummy1, dummy2, dummy3 = \
            solver(problem_simplified, method, dt)
        plt.plot(xs, ys, 'r--', label='')
        xmax = max(xmax, xs.max())
        ymax = max(ymax, ys.max())
    plt.axis([x[0], xmax, 0, 1.2*ymax])
    plt.title('Trajectory')

    # Avoid plot file: make PNG code as base64 coded string
    # embedded in the HTML image tag
    plotwidth = 400
    from StringIO import StringIO
    figfile = StringIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = figfile.buf  # extract string
    import base64
    figdata_png = base64.b64encode(figdata_png)
    html_text = """
<table>
<tr>
<td valign="top">
<img src="data:image/png;base64,%(figdata_png)s" width="%(plotwidth)s">
</td>
""" % vars()

    # Force plot
    try:
        plt.figure(forces_fig_no)
    except NameError:
        forces_fig_no = plt.figure().number
    plt.plot(x, d/np.abs(g), label='drag vs gravity')
    if spinrate != 0:
        plt.plot(x, l/np.abs(g), label='lift vs gravity')
    plt.legend()
    plt.title('Forces')

    figfile = StringIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = figfile.buf  # extract string
    figdata_png = base64.b64encode(figdata_png)
    html_text += """\
<td valign="top">
<img src="data:image/png;base64,%(figdata_png)s" width="%(plotwidth)s">
</td>
</tr>
</table>
""" % vars()
    # Add table of data for the runs so far in the plots
    table = """
<center>
<table border=1>
<tr>
"""
    for variable in data[0]:
        table += '<td align="center"> %-10s </td>' % variable  # column headings
    table += '\n</tr>\n'

    for case in data:
        table += '<tr>'
        for variable in case:
            if isinstance(case[variable], float):
                table += '<td align="right"> %.3g </td>' % case[variable]
            else:
                table += '<td> %-10s </td>' % case[variable]
        table += '</tr>\n'
    table += '</table>\n</center>\n'
    html_text += table
    return html_text


def pool_definition_list():
    """Create and return pool defined through a nested list."""
    pool = [
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
                     validate=lambda data_item, value: value > 0,
                     help='Mass of body.'),
                dict(name='Radius', default=0.11, unit='m',
                     help='Radius of spherical body.'),
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
                dict(name='Plot simplified motion', default=True,
                     help='Plot motion without drag+lift forces.'),
                dict(name='New plot', default=True,
                     help='Erase all old curves.'),
                ],
            ],
        ]
    from parampool.pool.UI import listtree2Pool
    pool = listtree2Pool(pool)
    return pool

def convert_time_step(data_item, value):
    # Value must be None or a float
    if value == 'None':
        return None
    else:
        try:
            return float(value)
        except TypeError:
            raise TypeError('%s: could not convert "%s" to float'
                            % (data_item.name, value))

def pool_definition_api():
    """Create and return pool using the parampool.pool API."""
    from parampool.pool.Pool import Pool
    pool = Pool()
    # Go to a subpool, but create it if it does not exist
    pool.subpool('Main pool')
    pool.subpool('Initial motion data')
    # Define data items for the current subpool
    pool.add_data_item(
        name='Initial velocity', default=5.0)
    pool.add_data_item(
        name='Initial angle', default=45,
        widget='range', minmax=[0,90])
    pool.add_data_item(
        name='Spinrate', default=50, widget='float', unit='1/s')

    # Move to (and create) another subpool, as in a file tree
    pool.subpool('../Body and environment data')
    # Add data items for the current subpool
    pool.add_data_item(
        name='Wind velocity', default=0.0,
        help='Wind velocity in positive x direction.',
        minmax=[-50, 50], number_step=0.5,
        widget='float', str2type=float)
    pool.add_data_item(
        name='Mass', default=0.1, unit='kg',
        validate=lambda data_item, value: value > 0,
        help='Mass of body.')
    pool.add_data_item(
        name='Radius', default=0.11, unit='m',
        help='Radius of spherical body.')

    pool.subpool('../Numerical parameters')
    pool.add_data_item(
        name='Method', default='RK4',
        widget='select',
        options=['RK4', 'RK2', 'ForwardEuler'],
        help='Numerical solution method.')
    pool.add_data_item(
        name='Time step', default=None,
        widget='textline', unit='s', str2type=convert_time_step)

    pool.subpool('../Plot parameters')
    pool.add_data_item(
        name='Plot simplified motion', default=True,
        help='Plot motion without drag+lift forces.')
    pool.add_data_item(
        name='New plot', default=True,
        help='Erase all old curves.')
    pool.update()
    return pool

def pool_definition_api_with_separate_subpools():
    """
    Create and return a pool by calling up other functions
    for defining the subpools. Also demonstrate customization
    of pool properties and inserting default values from file
    or the command line.
    """
    from parampool.pool.Pool import Pool
    pool = Pool()
    pool.subpool('Main pool')
    pool = motion_pool(pool)
    pool.change_subpool('..')
    pool = body_and_envir_pool(pool)
    pool.change_subpool('..')
    pool = numerics_pool(pool)
    pool.change_subpool('..')
    pool = plot_pool(pool)
    pool.update()  # finalize pool construction

    from parampool.pool.UI import (
        set_data_item_attribute,
        set_defaults_from_file,
        set_defaults_from_command_line,
        set_defaults_in_model_file,
        write_poolfile,
        )
    # Change default values in the web GUI
    import parampool.pool.DataItem
    parampool.pool.DataItem.DataItem.defaults['minmax'] = [0, 100]
    parampool.pool.DataItem.DataItem.defaults['range_steps'] = 500
    # Can also change 'number_step' for the step in float fields
    # and 'widget_size' for the width of widgets

    # Let all widget sizes be 6, except for Time step
    pool = set_data_item_attribute(pool, 'widget_size', 6)
    pool.get('Time step').data['widget_size'] = 4

    pool = set_defaults_from_file(pool, command_line_option='--poolfile')
    pool = set_defaults_from_command_line(pool)
    flask_modelfile = 'model.py'
    django_modelfile = os.path.join('motion_and_forces_with_pool', 'app',
                                    'models.py')
    if os.path.isfile(flask_modelfile):
        set_defaults_in_model_file(flask_modelfile, pool)
    elif os.path.isfile(django_modelfile):
        set_defaults_in_model_file(django_modelfile, pool)

    poolfile = open('pool.dat', 'w')
    poolfile.write(write_poolfile(pool))
    poolfile.close()

    return pool

def motion_pool(pool, name='Initial motion data'):
    pool.subpool(name)
    pool.add_data_item(
        name='Initial velocity', default=5.0, symbol='v_0',
        unit='m/s', help='Initial velocity',
        str2type=float, widget='float',
        validate=lambda data_item, value: value > 0)
    pool.add_data_item(
        name='Initial angle', default=45, symbol=r'\theta',
        widget='range', minmax=[0,90], str2type=float,
        help='Initial angle',
        validate=lambda data_item, value: 0 < value <= 90)
    pool.add_data_item(
        name='Spinrate', default=50, symbol=r'\omega',
        widget='float', str2type=float, unit='1/s',
        help='Spinrate')
    return pool

def body_and_envir_pool(pool, name='Body and environment data'):
    pool.subpool(name)
    pool.add_data_item(
        name='Wind velocity', default=0.0, symbol='w',
        help='Wind velocity in positive x direction.', unit='m/s',
        minmax=[-50, 50], number_step=0.5,
        widget='float', str2type=float)
    pool.add_data_item(
        name='Mass', default=0.1, symbol='m',
        help='Mass of body.', unit='kg',
        widget='float', str2type=float,
        validate=lambda data_item, value: value > 0)
    pool.add_data_item(
        name='Radius', default=0.11, symbol='R',
        help='Radius of spherical body.', unit='m',
        widget='float', str2type=float,
        validate=lambda data_item, value: value > 0)
    return pool

def numerics_pool(pool, name='Numerical parameters'):
    pool.subpool(name)
    pool.add_data_item(
        name='Method', default='RK4',
        widget='select',
        options=['RK4', 'RK2', 'ForwardEuler'],
        help='Numerical solution method.')
    pool.add_data_item(
        name='Time step', default=None, symbol=r'\Delta t',
        widget='textline', unit='s', str2type=eval,
        help='None: ca 500 steps, otherwise specify float.')
    return pool

def plot_pool(pool, name='Plot parameters'):
    pool.subpool(name)
    pool.add_data_item(
        name='Plot simplified motion', default=True,
        help='Plot motion without drag and lift forces.')
    pool.add_data_item(
        name='New plot', default=True,
        help='Erase all old curves.')
    return pool


def compute_motion_and_forces_with_pool(pool):
    initial_velocity = pool.get_value('Initial velocity')
    initial_angle = pool.get_value('Initial angle')
    spinrate = pool.get_value('Spinrate')
    w = pool.get_value('Wind velocity')
    m = pool.get_value('Mass')
    R = pool.get_value('Radius')
    method = pool.get_value('Method')
    dt = pool.get_value('Time step')
    plot_simplified_motion = pool.get_value('Plot simplified motion')
    new_plot = pool.get_value('New plot')
    return compute_motion_and_forces(
        initial_velocity, initial_angle, spinrate, w,
        m, R, method, dt, plot_simplified_motion,
        new_plot)

def compute_motion_and_forces_with_pool_loop(pool):
    html = ''
    initial_angle = pool.get_value('Initial angle')
    method = pool.get_value('Method')
    new_plot = pool.get_value('New plot')  # should be True here
    plot_simplified_motion = pool.get_value('Plot simplified motion')
    for initial_velocity in pool.get_values('Initial velocity'):
        for spinrate in pool.get_values('Spinrate'):
            for m in pool.get_values('Mass'):
                for R in pool.get_values('Radius'):
                    for dt in pool.get_values('Time step'):
                        for w in pool.get_values('Wind velocity'):
                            html += compute_motion_and_forces(
                                initial_velocity, initial_angle,
                                spinrate, w, m, R, method, dt,
                                plot_simplified_motion, new_plot)
    return html

def compute_average(data_array=np.array([1]), filename=None):
    if filename is not None:
        data = np.loadtxt(os.path.join('uploads', filename))
        what = 'file %s' % filename
    else:
        data = data_array
        what = 'data_array'
    return """
Data from %s:
<p>
<table border=1>
<tr><td> mean    </td><td> %.3g </td></tr>
<tr><td> st.dev. </td><td> %.3g </td></tr>
</table></p>
""" % (what, np.mean(data), np.std(data))


if __name__ == '__main__':
    print compute_drag_free_landing(5, 60)
