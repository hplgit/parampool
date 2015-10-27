import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField

class Formula(wtf.Form):
    x          = HTML5FloatField(default=1.0,
                             validators=[wtf.validators.InputRequired()])
    c0         = HTML5FloatField(default=0.0,
                             validators=[wtf.validators.InputRequired()])
    c1         = HTML5FloatField(default=1.0,
                             validators=[wtf.validators.InputRequired()])
    p1         = HTML5FloatField(default=0.0,
                             validators=[wtf.validators.InputRequired()])
    p2         = HTML5FloatField(default=0.0,
                             validators=[wtf.validators.InputRequired()])
    include_p1 = wtf.BooleanField(default=True)
    include_p2 = wtf.BooleanField(default=True)
