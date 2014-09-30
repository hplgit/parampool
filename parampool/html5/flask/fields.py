"""
HTML5 widgets for wtforms and flask.
See also the projects https://github.com/brutus/wtforms-html5
and http://simonklee.org/pkg/flask-wtf.
"""

from wtforms.fields import FloatField as FlaskFloatField
from wtforms.fields import IntegerField as FlaskIntegerField
from wtforms.widgets import HTMLString, Input
from parampool.menu.DataItem import DataItem

class HTML5Input(Input):
    """
    Extension of Input to support HTML5 widgets.
    """
    def __init__(self, input_type=None):
        super(HTML5Input, self).__init__(input_type)

    def __call__(self, field, **kwargs):
        """This is the method called from the template (form.field)."""
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        attrs = 'min', 'max', 'step', 'size', 'onchange'
        for attr in attrs:
            if attr not in kwargs and hasattr(field, attr):
                kwargs[attr] = getattr(field, attr)
        r = HTMLString('<input %s>' % self.html_params(name=field.name, **kwargs))
        return r

class RangeInput(HTML5Input):
    input_type = "range" # HTML5 input type

class FloatRangeField(FlaskFloatField):
    """
    HTML5 compatible version of FloatField. Using slider input widget.
    """
    widget = RangeInput()

    def __init__(self, label=None, validators=None, step=None, min=None,
                 max=None, onchange="", size=20, unit=None, **kwargs):
        if step is not None:
            self.step = step
        else:
            self.step = "any"
        if min is not None:
            self.min = min
        else:
            raise ValueError('Must specify min and max in %s constructor'
                             % self.__class__.__name__)
        if max is not None:
            self.max = max
        else:
            raise ValueError('Must specify min and max in %s constructor'
                             % self.__class__.__name__)
        if unit is not None:
            self.unit = unit
        self.onchange = onchange
        self.size = size
        super(FloatRangeField, self).__init__(label, validators, **kwargs)

class IntegerRangeField(FlaskIntegerField):
    """
    HTML5 compatible version of IntegerField. Using slider input widget.
    """
    widget = RangeInput()

    def __init__(self, label=None, validators=None, step=None, min=None,
                 max=None, onchange="", size=20, unit=None, **kwargs):
        if step is not None:
            self.step = step
        else:
            self.step = "any"
        if min is not None:
            self.min = min
        else:
            raise ValueError('Must specify min and max in %s constructor'
                             % self.__class__.__name__)
        if max is not None:
            self.max = max
        else:
            raise ValueError('Must specify min and max in %s constructor'
                             % self.__class__.__name__)
        if unit is not None:
            self.unit = unit
        self.onchange = onchange
        self.size = size
        super(IntegerRangeField, self).__init__(label, validators, **kwargs)

class NumberInput(HTML5Input):
    input_type = "number" # HTML5 input type

class HTML5FloatField(FlaskFloatField):
    """
    HTML5 compatibal version of FloatField. Using number input widget.
    Erroneous input is ignored and will not be accepted as a value.
    """
    widget = NumberInput()

    def __init__(self, label=None, validators=None,
                 min=None, max=None, size=20, step=None, unit=None,
                 **kwargs):
        if step is not None:
            self.step = step
        else:
            self.step = "any"
        if min is not None:
            self.min = min
        if max is not None:
            self.max = max
        if unit is not None:
            self.unit = unit
        self.min = min
        self.max = max
        self.size = size
        # For size to work in the template (or from here),
        # we must specify min, max, and step != 'any'
        super(HTML5FloatField, self).__init__(label, validators, **kwargs)
