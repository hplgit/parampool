import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class Myfunc(wtf.Form):
    a = FloatField(default=1.2,
                             validators=[wtf.validators.InputRequired()])
    b = wtf.IntegerField(default=2,
                             validators=[wtf.validators.InputRequired()])
    c = wtf.TextField(default='some text',
                             validators=[wtf.validators.InputRequired()])
    d = wtf.TextField(default='None',
                             validators=[wtf.validators.InputRequired()])
    e = wtf.TextField(default='[1, 2, 3]',
                             validators=[wtf.validators.InputRequired()])
    f = wtf.TextField(default='(4, 5, 6)',
                             validators=[wtf.validators.InputRequired()])
    g = wtf.TextField(default='[-1, 1]',
                             validators=[wtf.validators.InputRequired()])
    h = wtf.TextField(default='MySpecialClass(6)',
                             validators=[wtf.validators.InputRequired()])
    i = wtf.BooleanField(default=True)
