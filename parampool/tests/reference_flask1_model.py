import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class Mysimplefunc(wtf.Form):
    a = FloatField(validators=[wtf.validators.InputRequired()])
    b = FloatField(validators=[wtf.validators.InputRequired()])
    c = FloatField(validators=[wtf.validators.InputRequired()])
    d = wtf.TextField(default='None',
                             validators=[wtf.validators.InputRequired()])
