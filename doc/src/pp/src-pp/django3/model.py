import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class DragFreeMotionPlot2(wtf.Form):
    initial_velocity = FloatField(default=5.0,
                             validators=[wtf.validators.InputRequired()])
    initial_angle    = FloatField(default=45.0,
                             validators=[wtf.validators.InputRequired()])
    new_plot         = wtf.BooleanField(default=True)
