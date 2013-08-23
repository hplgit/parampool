import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField

class MotionAndForces(wtf.Form):
    initial_velocity       = HTML5FloatField(default=5.0,
                             validators=[wtf.validators.InputRequired()])
    initial_angle          = HTML5FloatField(default=45.0,
                             validators=[wtf.validators.InputRequired()])
    spinrate               = HTML5FloatField(default=50.0,
                             validators=[wtf.validators.InputRequired()])
    w                      = HTML5FloatField(default=0.0,
                             validators=[wtf.validators.InputRequired()])
    m                      = HTML5FloatField(default=0.1,
                             validators=[wtf.validators.InputRequired()])
    R                      = HTML5FloatField(default=0.11,
                             validators=[wtf.validators.InputRequired()])
    method                 = wtf.TextField(default='RK4',
                             validators=[wtf.validators.InputRequired()])
    dt                     = wtf.TextField(default='None',
                             validators=[wtf.validators.InputRequired()])
    plot_simplified_motion = wtf.BooleanField(default=True)
    new_plot               = wtf.BooleanField(default=True)
