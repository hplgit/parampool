import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField, FloatRangeField, IntegerRangeField
import flask.ext.wtf.html5 as html5

class MotionAndForcesWithPool(wtf.Form):

    Initial_velocity       = wtf.TextField(
        label=u'Initial velocity',
        description=u'Initial velocity',
        default='5.0',
        validators=[wtf.validators.InputRequired()])

    Initial_angle          = FloatRangeField(
        label=u'Initial angle',
        description=u'Initial angle',
        default=45,
        onchange="showValue(this.value)",
        min=0, max=90, step=1,
        validators=[wtf.validators.InputRequired(),
                    wtf.validators.NumberRange(0, 90)])

    Spinrate               = wtf.TextField(
        label=u'Spinrate',
        description=u'Spinrate',
        default='50',
        validators=[wtf.validators.InputRequired()])

    Wind_velocity          = HTML5FloatField(
        label=u'Wind velocity',
        description=u'Wind velocity',
        default=0,
        validators=[wtf.validators.InputRequired(),
                    wtf.validators.NumberRange(-50, 50)],
        min=-50, max=50, step=0.5)

    Mass                   = wtf.TextField(
        label=u'Mass',
        description=u'Mass',
        default='0.1',
        validators=[wtf.validators.InputRequired()])

    Radius                 = wtf.TextField(
        label=u'Radius',
        description=u'Radius',
        default='0.11',
        validators=[wtf.validators.InputRequired()])

    Method                 = wtf.SelectField(
        label=u'Method',
        description=u'Method',
        default='RK4',
        validators=[wtf.validators.InputRequired()],
        choices=[('RK4', 'RK4'), ('RK2', 'RK2'), ('ForwardEuler', 'ForwardEuler')])

    Time_step              = wtf.TextField(
        label=u'Time step',
        description=u'Time step',
        default='None',
        validators=[wtf.validators.InputRequired()])

    Plot_simplified_motion = wtf.BooleanField(
        label=u'Plot simplified motion',
        description=u'Plot simplified motion',
        default=True)

    New_plot               = wtf.BooleanField(
        label=u'New plot',
        description=u'New plot',
        default=True)
