import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class Average(wtf.Form):
    data_array = wtf.TextField(default='[1]',
                             validators=[wtf.validators.InputRequired()])
    filename   = wtf.FileField(validators=[wtf.validators.InputRequired()])
