import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField

class DragFreeMotionPlot(wtf.Form):
    initial_velocity = HTML5FloatField(default=5.0,
                             validators=[wtf.validators.InputRequired()])
    initial_angle    = HTML5FloatField(default=45.0,
                             validators=[wtf.validators.InputRequired()])
