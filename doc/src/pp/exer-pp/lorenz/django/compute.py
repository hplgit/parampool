import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import cnames
from matplotlib import animation
from scipy.integrate import odeint
from StringIO import StringIO
import base64, os, shutil

def display_result(fig1, fig2, fig3, video):
    code = '''
<img src="data:image/png;base64,%(fig1)s" height="300" width="330">
''' % vars()
    if video:
        code += '''\
<video height="300" width="330" autoplay loop title="Small variations in initial conditions">
   <source src="/static/webm/%(fig2)s">
</video>''' % vars()
    else:
        code += '''\
<img src="data:image/png;base64,%(fig2)s" height="300" width="330">
''' % vars()
    code += '''
<p>
<img src="data:image/png;base64,%(fig3)s" height="300" width="700">
''' % vars()
    return code

def create_video(u, t):
    N_trajectories = 20
    np.random.seed(1)
    t = np.linspace(0, 3, 1000)
    x0 = -15 + 30 * np.random.random((N_trajectories, 3))
    x_t = np.asarray([odeint(lorenz_init, x0i, t) for x0i in x0])
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1], projection='3d')
    ax.axis('off')

    # Choose a different color for each trajectory
    colors = plt.cm.jet(np.linspace(0, 1, N_trajectories))

    lines = sum([ax.plot([], [], [], '-', c=c)
                 for c in colors], [])
    pts = sum([ax.plot([], [], [], 'o', c=c)
               for c in colors], [])

    ax.set_xlim((-25, 25))
    ax.set_ylim((-35, 35))
    ax.set_zlim((5, 55))
    ax.view_init(30, 0)

    def init():
        for line, pt in zip(lines, pts):
            line.set_data([], [])
            line.set_3d_properties([])

            pt.set_data([], [])
            pt.set_3d_properties([])
        return lines + pts

    def animate(i):
        print i, '/', 500
        j = (2 * i) % x_t.shape[1]

        for line, pt, xi in zip(lines, pts, x_t):
            x, y, z = xi[:j].T
            line.set_data(x, y)
            line.set_3d_properties(z)

            pt.set_data(x[-1:], y[-1:])
            pt.set_3d_properties(z[-1:])

        ax.view_init(30, 0.3 * j)
        fig.canvas.draw()
        return lines + pts

    anim = animation.FuncAnimation(fig, animate, init_func=init,
                                   frames=501, interval=20, blit=True)
    dirname = os.path.dirname(__file__)
    if not os.path.isdir("%s/static/webm/" % dirname):
        os.makedirs("%s/static/webm" % dirname)

    import hashlib, time
    hashname = hashlib.sha224(str(time.time())).hexdigest()
    anim.save('%s/static/webm/%s.webm' % (dirname, hashname), fps=30)

    return "%s.webm" % hashname

def plotting(u, t, video):
    # 3D plot
    x, y, z = u[:,0], u[:,1], u[:,2]
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_title('3D plot')
    ax.plot(x, y, z, label='Lorenz')
    ax.legend()
    figfile = StringIO()
    fig.savefig(figfile, format='png')
    figfile.seek(0)
    fig1 = base64.b64encode(figfile.buf)

    # Animation or 2D plot
    if video:
        fig2 = create_video(u, t)
    else:
        plt.figure()
        plt.plot(x,z)
        plt.title("x vs z")
        figfile = StringIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        fig2 = base64.b64encode(figfile.buf)

    # x, y and z vs t plot
    plt.figure()
    plt.plot(t,x,t,y,t,z)
    plt.legend(['x','y','z'])
    plt.title('x, y and z vs t')
    figfile = StringIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    fig3 = base64.b64encode(figfile.buf)
    return fig1, fig2, fig3

def lorenz_init(initial, t):
    x = initial[0]
    y = initial[1]
    z = initial[2]

    global s, r, b

    x_dot = s*(y - x)
    y_dot = x*(r - z) - y
    z_dot = x*y - b*z
    return [x_dot, y_dot, z_dot]

def compute_lorenz(pool):
    x0 = pool.get("x0").get_value()
    y0 = pool.get("y0").get_value()
    z0 = pool.get("z0").get_value()

    global s, r, b
    s = pool.get("sigma").get_value()
    r = pool.get("rho").get_value()
    b = pool.get("beta").get_value()

    N = pool.get("N").get_value()
    T = pool.get("T").get_value()
    video = pool.get("video").get_value()

    initial = [x0, y0, z0]
    dt = float(T)/N
    t = np.linspace(0, T, N+1)

    u = odeint(lorenz_init, initial, t)
    fig1, fig2, fig3 = plotting(u, t, video)
    return display_result(fig1, fig2, fig3, video)
