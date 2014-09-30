import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField

class Mysimplefunc(wtf.Form):
    a = wtf.FloatField(validators=[wtf.validators.InputRequired()])
    b = wtf.FloatField(validators=[wtf.validators.InputRequired()])
    c = wtf.FloatField(validators=[wtf.validators.InputRequired()])
    d = wtf.TextField(default='None',
                             validators=[wtf.validators.InputRequired()])
