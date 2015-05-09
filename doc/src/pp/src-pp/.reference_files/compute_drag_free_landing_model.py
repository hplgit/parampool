import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField

class DragFreeLanding(wtf.Form):
    initial_velocity = wtf.FloatField(validators=[wtf.validators.InputRequired()])
    initial_angle    = wtf.FloatField(validators=[wtf.validators.InputRequired()])
