from wtforms.fields import FloatField as FlaskFloatField
from wtforms.fields import IntegerField as FlaskIntegerField
from wtforms.widgets import HTMLString, Input

class HTML5Input(Input):
    """
    Extension of Input to support HTML5 widgets.
    """
    def __init__(self, input_type=None):
        super(HTML5Input, self).__init__(input_type)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        if hasattr(field, 'min'):
            kwargs['min'] = field.min
        if hasattr(field, 'max'):
            kwargs['max'] = field.max
        if hasattr(field, 'onchange'):
            kwargs['onchange'] = field.onchange
        kwargs['step'] = field.step
        return HTMLString('<input %s>' % self.html_params(name=field.name, **kwargs))

class RangeInput(HTML5Input):
    input_type = "range" # HTML5 input type

class FloatRangeField(FlaskFloatField):
    """
    HTML5 compatibal version of FloatField. Using slider input widget.
    """
    widget = RangeInput()

    def __init__(self, label=None, validators=None, step=0.001, min=-1,
                 max=1, onchange="", unit=None, **kwargs):
        self.step = step
        self.min = min
        self.max = max
        self.unit = unit
        self.onchange = onchange
        super(FloatRangeField, self).__init__(label, validators, **kwargs)

class IntegerRangeField(FlaskIntegerField):
    """
    HTML5 compatibal version of FloatField. Using slider input widget.
    """
    widget = RangeInput()

    def __init__(self, label=None, validators=None, step=1, min=-1,
                 max=1, onchange="", unit=None, **kwargs):
        self.step = step
        self.min = min
        self.max = max
        self.unit = unit
        self.onchange = onchange
        super(IntegerRangeField, self).__init__(label, validators, **kwargs)

class NumberInput(HTML5Input):
    input_type = "number" # HTML5 input type

class FloatField(FlaskFloatField):
    """
    HTML5 compatibal version of FloatField. Using number input widget.
    Erroneous input is ignored and will not be accepted as a value.
    """
    widget = NumberInput()

    def __init__(self, label=None, validators=None, step="any", unit=None, **kwargs):
        self.step = step
        self.unit = unit
        super(FloatField, self).__init__(label, validators, **kwargs)
