from collections import OrderedDict
import re, inspect, numpy
from math import *  # enable eval to work with math functions (str2type=eval)

class DataItem:
    """
    Represent a data item (parameter) by its name, a default value,
    and an optional set of attributes that describe the data item.
    Typical attributes are

    =============== ==================================================
    Name            Description
    =============== ==================================================
    ``name``        name (mandatory)
    ``default``     default value
    ``unit``        registered unit (e.g., km, h, 1/s, kg/m**3)
    ``help``        description of the data item
    ``str2type``    object transforming a string to desired type,
                    can be ``eval``, ``float``, ... Based on type
                    of ``widget`` or ``default`` if not given.
    ``value``       current value assigned in a user interface
    ``minmax``      legal interval (2-list) of values
    ``options``     legal list of values
    ``namespace``   user's namespace for use when ``str2type=eval``
    ``user_data``   meta data stored in this object
    ``validate``    callable that can validate the value
    ``symbol``      LaTex code for mathematical symbol
    ``widget``      recommended widget in graphical user interfaces;
                    allowed types are: "integer", "float", "range",
                    "integer_range", "textline", "textarea",
                    "checkbox", "select", "email", "hidden",
                    "password", "file", "url", "tel"
    ``widget_size`` width of widget in graphical user interfaces
                    (number of characters)
    =============== ==================================================

    The ``str2type`` attribute should be explicitly set to have full
    control of how user input in form of strings (on the command line
    or in a GUI) is transferred to the right type. For example,
    if the data item is a real value, set call the constructor with
    ``str2type=float``, if the value is boolean use ``bool``,
    if string use ``str``, if integer use ``int``, if list, tuple,
    or dictionary use ``eval``, if user-defined data type (class)
    use the class name (implying the constructor for converting from
    string to right data type).

    If ``str2type`` is not set, one first checks if ``widget`` is
    specified and sets the ``str2type`` accordingly ("float" and
    "float_range" lead to ``float``,"integer" and "integer_range" to ``int``,
    "checkbox" to ``bool`` (or more precisely, the built in
    ``str2bool`` converter), while all other widgets lead to
    ``str2type`` as ``str`` (assuming the answer is a string).
    If ``widget`` is not set, one applies the type of the ``default``
    value for setting ``str2type``. A ``float``, ``int``, ``bool``,
    or ``str`` is recognized by the types, while lists, tuples,
    and dictionaries and in fact all other types leads to using
    ``eval`` as ``str2type``. This means that the string (``s``) must have
    the right Python syntax so that ``eval(s)`` turns the string into
    the right object. As emphasized, it is best to explicitly set
    ``str2type``.

    A common problem with setting ``str2type`` based on default
    value is if you have a real number, but set the default to (e.g.)
    5. Then ``str2type`` becomes ``int``, and any attempt to set
    the value to something real like 5.1 will fail.

    A number and a unit can be specified together as value. If unit
    is not given, it is set based on the unit used in the value, otherwise
    (unit specified) a unit conversion of the numerical value takes place.
    """
    _legal_data = 'name default unit help value str2type minmax options widget validate namespace user_data symbol widget_size range_step number_step'.split()

    # defaults are used by GUI generating software to get
    # values of attributes that are not set. These defaults can
    # be set in user code:
    # import parampool.menu.DataItem
    # parampool.menu.DataItem.DataItem.defaults['minmax'] = [-10000, 10000]
    defaults = {'widget_size': 11, 'minmax': [-1000, 1000],
                'range_steps': 100, 'number_step': 0.001}
    # range_steps: how many steps in a range slider
    # number_step: the increment in number when clicking on arrows
    # in a number HTML5 field
    # widget_size: width of input field

    def _signature(self):
        """Return output signature with "DataItem: name=..."."""
        return 'DataItem "%s"' % self.name

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise ValueError('DataItem: name must be an argument')
        self.name = kwargs['name']

        if 'default' not in kwargs:
            kwargs['default'] = None  # indicates required variable

        if kwargs['default'] is None:
            # Override user's choice
            # AEJ: This overrides e.g. FileField and PasswordField, which normally
            # have None as default, to textline. I added an if-test here to avoid
            # that issue.
            if not kwargs['widget'] in ('file', 'password'):
                kwargs['widget'] = 'textline'
                if not 'str2type' in kwargs:
                    kwargs['str2type'] = eval
                #print 'Data item "%s" has default value None and gets widget "textline" and str2type=eval' % self.name

        # Check that all arguments are valid
        for arg in kwargs:
            if arg not in self._legal_data:
                raise ValueError(
                    '%s argument %s=%s is not valid. Valid '
                    'arguments are\n%s' %
                    (self._signature(), arg, kwargs[arg],
                     ', '.join(self._legal_data)))

        self.data = OrderedDict(**kwargs)

        if 'str2type' not in self.data:
            # use widget type if set, otherwise use the type
            # of the default value
            if 'widget' in self.data and self.data['widget']:
                if self.data['widget'] in ('float', 'range'):
                    self.data['str2type'] = float
                elif self.data['widget'] in ('integer', 'integer_range'):
                    self.data['str2type'] = int
                elif self.data['widget'] in ('file', 'select', 'textline',
                                             'textarea', 'email', 'hidden',
                                             'password', 'url', 'tel'):
                    self.data['str2type'] = str
                elif self.data['widget'] in ('checkbox',):
                    self.data['str2type'] = str2bool

            elif self.data['default'] is None:
                self.data['str2type'] = str
            elif isinstance(self.data['default'], basestring):
                self.data['str2type'] = str
            elif type(self.data['default']) == type(True):
                # Careful with boolean values, use special str2bool
                self.data['str2type'] = str2bool
            elif type(self.data['default']) in (
                type(()), type([]), type({})):
                self.data['str2type'] = eval
            elif isinstance(self.data['default'], numpy.ndarray):
                self.data['str2type'] = lambda s: numpy.asarray(eval(s))
            elif type(self.data['default']) in (
                type(2.0), type(2), type(2+0j)):
                self.data['str2type'] = type(self.data['default'])
            else:
                # Assume user's non-standard data can be turned
                # from str to object via eval and self.data['namespace']
                self.data['str2type'] = eval
            # If user has set str2type to bool, change to str2bool
            # since bool does not work properly for turning a string
            # to a boolean
            if self.data['str2type'] == bool:
                self.data['str2type'] = str2bool

        if not 'widget' in self.data:
            if self.data['str2type'] == str2bool:
                self.data['widget'] = 'checkbox'
            elif self.data['str2type'] == float:
                if 'minmax' in self.data:
                    # min/max given, use HTML5 number widget
                    self.data['widget'] = 'float'
                else:
                    # just use a plain text field
                    self.data['widget'] = 'textline'
            elif self.data['str2type'] == int:
                if 'minmax' in self.data:
                    # min/max given, use HTML5 number widget
                    self.data['widget'] = 'integer'
                else:
                    # just use a plain text field
                    self.data['widget'] = 'textline'
            elif 'options' in self.data:
                self.data['widget'] = 'select'
            else:
                self.data['widget'] = 'textline'

        self._check_validity_of_data()

        # Override widget if unit is given - then we need a text field
        if 'unit' in self.data:
            if 'widget' in self.data:
                self.data['widget'] = 'textline'

        self._use_str2type = True  # convert data to right type

        self._values = [self.data['default']]
        self._assigned_value = False  # True if value from UI

        import math
        self.math_functions = [name for name in dir(math)
                               if not name.startswith('_')]

    def _check_validity_of_data(self):
        if 'minmax' in self.data:
            attr = self.data['minmax']
            if not isinstance(attr, (list,tuple)):
                raise TypeError(
                    '%s: minmax must be 2-list/tuple, not %s' %
                    self._signature(), type(attr))
            if len(attr) != 2:
                raise TypeError(
                    '%s: minmax list/tuple must have length 2, not %d' %
                    self._signature(), len(attr))
            if not isinstance(attr[0], (float,int)) or \
               not isinstance(attr[1], (float,int)):
                ValueError('%s: minmax has wrong data types [%s, %s]' %
                           self._signature(),
                           type(attr[0]), type(attr[1]))

        if 'options' in self.data:
            attr = self.data['options']
            if not isinstance(attr, (list,tuple)):
                raise TypeError(
                    '%s: options must list/tuple, not %s' %
                    type(attr))

        if 'widget' in self.data:
            widget = self.data['widget']
            allowed_widgets = ("integer", "float", "range", "integer_range",
                               "textline", "textarea", "checkbox", "select",
                               "email", "hidden", "password", "file", "url",
                               "tel")
            if not widget in allowed_widgets:
                raise TypeError('%s: widget %s is not allowed. Plese select \
from the following list: %s' % (self._signature(), widget, allowed_widgets))

        for attr in 'help', 'widget':
            if attr in self.data:
                if not isinstance(self.data[attr], basestring):
                    raise TypeError('%s: %s must be string, not %s' %
                                    self._signature(), attr,
                                    type(self.data[attr]))

    def _has_math_expression(self, value):
        if isinstance(value, str):
            for operator in ['*', '+', '-', '/']:
                if operator in value:
                    if not value.strip().startswith('-'):
                        return True
            for math_function in self.math_functions:
                if math_function in value:
                    return True
        return False

    def _process_value(self, value):
        """
        Perform unit conversion (if relevant), convert to string
        value to right type according to str2type, and perform
        validation.
        """

        if isinstance(value, str):
            value = self._handle_unit_conversion(value)

        if not self._use_str2type:
            return value

        # Convert value to the right type

        if not 'str2type' in self.data:
            return value # cannot do any conversion

        # No conversion needed if str2type is some string type
        if inspect.isclass(self.data['str2type']) and \
               issubclass(self.data['str2type'], basestring):
            return value

        # Otherwise, convert to registered type using str2type
        if self.data['str2type'] == eval or \
               self._has_math_expression(value):
            # Execute in some namespace?
            if 'namespace' in self.data:
                value = eval(value, self.data['namespace'])
            else:
                try:
                    value = eval(value)
                    # Note: this eval can handle math expressions
                    # like sin(pi/2) since this module imports all of
                    # the math module
                except Exception, e:
                    # value is a string
                    pass
        else:
            try:
                value = self.data['str2type'](value)
            except Exception, e:
                # Deal with common error first: default is int by accident,
                # should have been float
                msg = ''
                if self.data['str2type'] == int:
                    try:
                        value = float(value)
                        if type(self.data['default']) == type(1):
                            msg = 'str2type is int but should have been float, either specify str2type=float or set the default value to %d.0, not just %d (which makes str2type become int if not explicitly set).'
                    except:
                        pass # cannot find out of this case
                raise TypeError(
                'could not apply str2type=%s to value %s %s\n%s\n'
                'Python exception: %s' %
                (self.data['str2type'], value, type(value), msg, e))

        return value

    def _validate(self, value):
        if 'minmax' in self.data:
            lo, hi = self.data['minmax']
            if not (lo <= value <= hi):
                raise DataItemValueError(
                    '%s: value=%s not in [%s, %s]' %
                    self._signature(), value, lo, hi)

        if 'options' in self.data:
            if value not in self.data['options']:
                raise DataItemValueError(
                    '%s: wrong value=%s not in %s' %
                    (self._signature(), value, self.data['options']))

    def _handle_unit_conversion(self, value):
        """
        Return converted value (float) if value with unit,
        otherwise just return value.
        """
        # Is value an expression and a unit?
        if self._has_math_expression(value):
            if ' ' in value.strip():
                # Space indicates that it might have a unit, let's try
                # eval on first part
                parts = value.split()
                if len(parts) == 2:
                    expression, unit = parts
                    if self._has_math_expression(expression):
                        # Evaluate expression and recreate value
                        expression = eval(expression)
                        value = str(expression) + ' ' + unit

        # Is value a number and a unit?
        number_with_unit = r'^\s*([Ee.0-9+-]+) +([A-Za-z0-9*/]+)\s*$'
        if re.search(number_with_unit, value):
            if not hasattr(self, 'PhysicalQuantity_class'):
                # Must install the unit conversion tool (the first time
                # we see the need for units)
                from Scientific.Physics.PhysicalQuantities import \
                     PhysicalQuantity
                self.PhysicalQuantity_class = PhysicalQuantity
            q = self.PhysicalQuantity_class(value)  # quantity with unit
            if 'unit' in self.data:
                registered_unit = self.data['unit']
                if registered_unit != q.getUnitName():
                    if q.isCompatible(registered_unit):
                        q.convertToUnit(registered_unit)
                    else:
                        raise DataItemValueError(
                            '%s: value=%s, unit %s is not compatible with '
                            'registered unit %s' %
                            (self._signature(), value, q.getUnitName(),
                            registered_unit))
            else:
                # No unit registered, register this one
                self.data['unit'] = unit
            value = str(q.getValue())  # ensure str so we can do eval on math
        # else: just return value as it came in
        return value

    def get(self, attribute_name, default=None):
        """
        Return value of attribute name.
        If attribute_name is not registered, raise exception if
        default is None, otherwise return default.
        """
        if attribute_name in self.data:
            return self.data[attribute_name]
        else:
            if default is None:
                raise ValueError(
                    '%s: no attribute with name "%s"\n'
                    'registered names are %s' %
                    (self._signature(), attribute_name,
                     ', '.join(list(self.data.keys()))))
            else:
                return default

    def set_value(self, value):
        """Set value as a string."""

        if isinstance(value, unicode):
            value.encode('ascii', 'replace')
            value = str(value)

        if not isinstance(value, str):
            if not type(value) == type(self.data["default"]):
                if not (isinstance(value, float) and isinstance(self.data["default"], int)):
                    raise ValueError('%s: value=%s %s must be a string (or %s)' %
                                 (self._signature(), value, type(value),
                                  type(self.data["default"])))
            else:
                self._use_str2type = False

        # The item can have a single value or multiple values
        if isinstance(value, str) and '&' in value:
            self._values = [v.strip() for v in value.split('&')]
        else:
            self._values = [value]

        validate = self.data.get('validate', DataItem._validate)
        for i in range(len(self._values)):
            value = self._process_value(self._values[i])

            # Validate value
            try:
                valid = validate(self, value)
            except DataItemValueError, e:
                valid = None
                raise e
            if valid is not None:
                # No exception was raised in the validate routine,
                # raise it here
                if not valid:
                    raise DataItemValueError('%s = %s: validate function %s claims invalid value' % (self.name, value, validate.__name__))

            # value is ok, assign it
            self._values[i] = value

        self._assigned_value = True

    def get_values(self):
        """Return (possibly multiple) values set for this data item."""
        if self._values == [None]:
            pass
            #raise ValueError(
            #    '%s: value not set.\ndefault=None so value must be set.' %
            #    self._signature())
        if self._assigned_value:
            return self._values
        elif 'default' in self.data:
            return [self.data['default']]
        else:
            raise ValueError('DataItem "%s" has not default value and no assigned value' % self.name)

    def get_value(self, with_unit=False, fmt=None):
        """
        Return a single value set for this data item.
        `with_unit` returns the value and the unit as a string, and
        in that case `fmt` can be used to specify the formatting.
        Without `fmt` the registered value is returned, with `fmt`
        given, the value is returned as a string formatted according
        to `fmt`.
        """
        if fmt:
            value = fmt % self.get_values()[0]
        else:
            value = self.get_values()[0]

        if with_unit:
            if 'unit' in self.data:
                return '%s %s' % (value, self.data['unit'])
            else:
                return value
        else:
            if fmt:
                return value
            else:
                return self.get_values()[0]

    def has_multiple_values(self):
        return len(self._values) > 1

    def __str__(self):
        """Return pretty print of this data item."""
        attribute_names = list(self.data.keys())
        attribute_names.remove('name')
        import pprint
        s = '%s:' % self._signature()
        if self.has_multiple_values():
            s += ' multiple values: %s' % self.get_values()
        else:
            s += ' value=%s' % self.get_value()

        s += ' ' + ', '.join(['%s=%s' % (name, self.data[name])
                       for name in sorted(attribute_names)])
        return s

    def __repr__(self):
        args = ', '.join(['%s=%s' % (attr, repr(self.data[attr]))
                          for attr in self.data])
        return '%s(%s)' % (self.__class__.__name__, args)

def str2bool(s):
    """
    Turn a string s, holding some boolean value
    ('on', 'off', 'True', 'False', 'yes', 'no' - case insensitive)
    into boolean variable. s can also be a boolean. Example:

    >>> str2bool('OFF')
    False
    >>> str2bool('yes')
    True
    """
    if isinstance(s, str):
        true_values = ('on', 'true', 'yes')
        false_values = ('off', 'false', 'no')
        s2 = s.lower()  # make case insensitive comparison
        if s2 in true_values:
            return True
        elif s2 in false_values:
            return False
        else:
            raise ValueError('"%s" is not a boolean value %s' % \
                             (s, true_values+false_values))
    else:
        raise TypeError('%s %s (not string!) cannot be converted to bool' % \
                        (s, type(s)))


class DataItemValueError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    __repr__ = __str__


import nose.tools as nt

def test_DataItem_set_value():
    d = DataItem(name='A', default=1.0)  # minimal

    # Test that non-strings cannot be assigned with set_value
    try:
        d.set_value(2)
        assert False, 'should be illegal to set a value that is not a string'
    except ValueError:
        pass
    try:
        d.set_value('some method')
        assert False, 'should be illegal to convert "some method" to str2type=float'
    except TypeError:
        pass

    # Test that plain assignment works: value and type
    d.set_value('2')
    nt.assert_equal(d.get_value(), 2.0)
    nt.assert_equal(type(d.get_value()), d.data['str2type'])

def test_DataItem_required_value():
    # A required variable is indicated by missing default or
    # default set to None

    d = DataItem(name='A')  # no default, must set variable, type str

    nt.assert_equal(d.get_value(), None)
    # Test that non-strings cannot be assigned with set_value
    try:
        d.set_value(2)
        assert False, 'cannot set value to 2 - must be a string'
    except:
        pass
    whatever = 'just something'
    d.set_value(whatever)
    nt.assert_equal(d.get_value(), whatever)
    nt.assert_equal(type(d.get_value()), d.data['str2type'])

def test_DataItem_unit_conversion():
    d = DataItem(name='V', default=0.2, help='velocity', unit='m/s')
    nt.assert_equal(d.get_values(), [0.2])
    d.set_value('2 km/h')
    nt.assert_equal(d.get_value(with_unit=True,
                                 fmt='%5.2f').strip(),
                    '0.56 m/s')
    nt.assert_almost_equal(d.get_value(), 0.555555555, places=6)

    try:
        d.set_value('5.2 kg/m')
        assert False, 'wrong unit should trigger exception'
    except:
        pass


def test_DataItem_str2type():
    # Test assignments with str2type=eval
    d = DataItem(name='U', default=2, str2type=eval)
    values_str = ['[1, 2, 3, 4]', 'some method', '2.3']
    values = [[1, 2, 3, 4], 'some method', 2.3]
    for value_str, value in zip(values_str, values):
        d.set_value(value_str)
        nt.assert_equal(d.get_value(), value)

    # Test user-defined function for str2type: str to numpy array
    # via list syntax
    def str2d(s):
        return numpy.asarray(eval(s), dtype=numpy.float)

    d = DataItem(name='Q', default=1.5, str2type=str2d)
    nt.assert_equal(d.get_value(), 1.5)
    d.set_value('[-1, 5, 8]')
    diff = numpy.abs(d.get_value() - numpy.array([-1, 5, 8.])).max()
    nt.assert_almost_equal(diff, 0, places=14)

    # Test class for str2type
    class Str2d:
        def __call__(self, s):
            return int(round(float(s)))

    d = DataItem(name='T', default=2, str2type=Str2d())
    d.set_value('3.87')
    nt.assert_equal(d.get_value(), 4)

def test_DataItem_validate():
    # Should do checking for values in DataItem and also call validator
    legal_values = 'Newton Secant Bisection'.split()
    d = DataItem(name='method', default='Newton',
                 options=legal_values)
    try:
        d.set_value('Broyden')
        assert False, 'wrong value, not among options'
    except:
        pass
    d.set_value('Secant')
    nt.assert_equal(d.get_value(), 'Secant')

    # User-supplied validation function, here case-insensitive
    # test of some options
    class Validate:
        def __init__(self, legal_values):
            self.legal_values = [v.lower() for v in legal_values]

        def __call__(self, data_item, value):
            if value.lower() not in self.legal_values:
                raise DataItemValueError(
                    '%s: %s not in %s' %
                    (data_item._signature(), value, self.legal_values))

    validate = Validate(legal_values)
    d = DataItem(validate=validate, **d.data)
    d.set_value('NEWTON')
    nt.assert_equal(d.get_value(), 'NEWTON')

def test_DataItem_multiple_values():
    legal_values = 'Newton Secant Bisection'.split()
    d = DataItem(name='method', default='Secant',
                 options=legal_values)
    values = 'Newton & Secant & Bisection'
    d.set_value(values)
    nt.assert_equal(d.get_values(), values.split(' & '))

    d = DataItem(name="a", help="piecewise constant function values",
                 default=[1])
    values = '[1, 5, 0.1]   & [10, 1, 100, 1000] & [4] &[9, 2.5]'
    d.set_value(values)
    expected = [eval(a) for a in values.split('&')]
    nt.assert_equal(d.get_values(), expected)

def test_DataItem_str():
    """Test output of __str__."""
    d = DataItem(name='Q', default=1.2, minmax=[0,2],
                 widget='range', help='volume flux')
    answer = """DataItem "Q": value=1.2 default=1.2, help=volume flux, minmax=[0, 2], str2type=<type 'float'>, widget=range"""
    nt.assert_equal(str(d), answer)

def test_DataItem_math():
    # Test use of basic functions from math (available in DataItem)
    d = DataItem(name='q', default=0, str2type=eval)
    d.set_value('sin(pi/2)*exp(0) & pi**2')
    nt.assert_almost_equal(d.get_values()[0], 1, places=14)
    nt.assert_almost_equal(d.get_values()[1], pi**2, places=14)

def test_DataItem_namespace():
    # Define user-specific function and use that when setting values
    # (eval in DataItem will use local namespace)
    def Gaussian(x, mean=0, sigma=1):
        return 1/(sqrt(2*pi)*sigma)*exp(-(x-mean)**2/(2*sigma**2))

    d = DataItem(name='q', default=0, namespace=locals(), str2type=eval)
    d.set_value('Gaussian(2, 2, 3) & Gaussian(3)')
    nt.assert_almost_equal(d.get_values()[0], 0.1329807601338109, places=12)
    nt.assert_almost_equal(d.get_values()[1], 0.0026880519410391462, places=12)

def test_DataItem_dict2DataItem():
    data = dict(name="A", help="area", default=1, str2type=float)
    d = DataItem(**data)
    nt.assert_equal(str(d), """DataItem "A": value=1 default=1, help=area, str2type=<type 'float'>, widget=float""")


if __name__ == '__main__':
    test_DataItem_set_value()
    test_DataItem_required_value()
    test_DataItem_unit_conversion()
    test_DataItem_str2type()
    test_DataItem_validate()
    test_DataItem_multiple_values()
    test_DataItem_str()
    test_DataItem_math()
    test_DataItem_namespace()
    test_DataItem_dict2DataItem()
