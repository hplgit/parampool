import odespy
import numpy as np
from math import pi, sqrt, sin, cos
import matplotlib.pyplot as plt
import os

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

def compute_motion(
    initial_velocity=5.0,
    initial_angle=45.0,
    spinrate=50.0,
    m=0.1,
    R=0.11,
    method='RK4'
    ):
    v_x0 = initial_velocity*cos(initial_angle*pi/180)
    v_y0 = initial_velocity*sin(initial_angle*pi/180)
    xmax = 0
    ymax = 0

    for dt in [0.02]:
        #for method in ['ForwardEuler', 'RK2', 'RK4']:
        for drag in [True, False]:
            problem = Ball(m=m, R=R, drag=drag,
                           spinrate=spinrate if drag else 0, w=0)
            problem.set_initial_velocity(v_x0, v_y0)
            x, y, t, g, d, l = solver(problem, method, dt)
            plt.figure(1)
            if drag:
                plt.plot(x, y, label='%s' % ('w/drag' if drag else ''))
            else:
                plt.plot(x, y, 'r--')
            if drag:
                plt.figure(2)
                plt.plot(x, d, label='drag force')
                if spinrate:
                    plt.plot(x, l, label='lift force')
                plt.plot(x, np.abs(g), label='gravity force')
            xmax = max(xmax, x.max())
            ymax = max(ymax, y.max())
    plt.figure(1)
    plt.axis([x[0], xmax, 0, 1.2*ymax])
    plt.legend()
    plt.figure(2)
    plt.legend()
    plt.show()

def compute_average(data=np.array([1,2]), filename=None):
    if filename is not None:
        data = np.loadtxt(os.path.join('uploads', filename))
        what = 'file data'
    else:
        what = 'array'
    return 'mean of %s: %.3g<br>\nstandard deviation:' % \
           (what, np.mean(data), np.std(data))

if __name__ == '__main__':
    print compute_drag_free_landing(5, 60)
    compute_motion()
