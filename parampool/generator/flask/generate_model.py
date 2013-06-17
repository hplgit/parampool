import os

def generate_model_menu(compute_function, classname, outfile, menu):
    """
    Generate Flask form by iterating through
    leaf nodes in the given menu object.
    """

    class CodeData(object):
        """Object to hold output code through tree recursion."""
        id = 0
        parent_id = [-1]

    def leaf_func(tree_path, level, item, user_data):
        name = item.name
        default = item.data["default"]

        # Make label
        label = ""
        if item.data.has_key("help"):
            label += item.data["help"]
        if item.data.has_key("unit"):
            label += " (" + item.data["unit"] + ")"

        if item.data.has_key("minmax"):
            minvalue = item.data["minmax"][0]
            maxvalue = item.data["minmax"][1]

        widget = item.data.get("widget", None)

        if widget is not None:
            if widget == "RangeField":
                if not item.data.has_key("minmax"):
                    raise TypeError("Cannot create a range without min/max values")
                user_data.code += """ \
    %%(name)-%ds = RangeFloatField(u'%%(label)s',
                        onchange="showValue(this.value)",
                        min=%%(minvalue)g,
                        max=%%(maxvalue)g,
                        default=%%(default)g,
                        validators=[wtf.validators.InputRequired(),
                                    wtf.validators.NumberRange(%%(minvalue)g,
                                                               %%(maxvalue)g)])
""" % user_data.longest_name % vars()

            elif widget == "IntRangeField":
                if not item.data.has_key("minmax"):
                    raise TypeError("Cannot create a range without min/max values")
                user_data.code += """ \
    %%(name)-%ds = RangeFloatField(u'%%(label)s',
                        onchange="showValue(this.value)",
                        step=1.0,
                        min=%%(minvalue)g,
                        max=%%(maxvalue)g,
                        default=%%(default)g,
                        validators=[wtf.validators.InputRequired(),
                                    wtf.validators.NumberRange(%%(minvalue)g,
                                                               %%(maxvalue)g)])
""" % user_data.longest_name % vars()

            elif widget == "FileField":
                user_data.code += """ \
    %%(name)-%ds = wtf.FileField(u'%%(label)s',
                        validators=[wtf.validators.InputRequired())
""" % user_data.longest_name % vars()

        else:
            # Choose between given options
            if item.data.has_key("options"):
                choices = item.data["options"]
                user_data.code += """ \
    %%(name)-%ds = wtf.SelectField(u'%%(label)s',
                        default='%%(default)s',
                        validators=[wtf.validators.InputRequired()],
                        choices=%%(choices)s)
""" % user_data.longest_name % vars()

            # Bool
            elif isinstance(default, bool):
                user_data.code += """ \
    %%(name)-%ds = wtf.BooleanField(u'%%(label)s', default=%%(default)s)
""" % user_data.longest_name % vars()

            # Text input
            elif isinstance(default, str):
                user_data.code += """ \
    %%(name)-%ds = wtf.TextField(u'%%(label)s',
                        default='%%(default)s',
                        validators=[wtf.validators.InputRequired()])
""" % user_data.longest_name % vars()

            # Regular float input
            elif isinstance(default, float):
                user_data.code += """ \
    %%(name)-%ds = FloatField(u'%%(label)s',
                        default=%%(default)g,
                        validators=[wtf.validators.InputRequired()\
""" % user_data.longest_name % vars()
                if item.data.has_key("minmax"):
                    user_data.code += """,
                                    wtf.validators.NumberRange(%(minvalue)g,
                                                               %(maxvalue)g)])
""" % vars()
                else:
                    user_data.code += "])\n"

            # Integer
            elif isinstance(default, int):
                user_data.code += """ \
    %%(name)-%ds = wtf.IntegerField(u'%%(label)s',
                        default=%%(default)g,
                        validators=[wtf.validators.InputRequired()\
""" % user_data.longest_name % vars()
                if item.data.has_key("minmax"):
                    user_data.code += """,
                                    wtf.validators.NumberRange(%(minvalue)g,
                                                               %(maxvalue)g)])
""" % vars()
                else:
                    user_data.code += "])\n"

            # Anything else
            else:
                raise TypeError('Argument %s=%s is not supported.' %
                                name, type(value))

    code = '''\
import wtforms as wtf
from parampool.html5.flask.fields import FloatField, RangeFloatField

class %(classname)s(wtf.Form):
''' % vars()

    codedata = CodeData()
    codedata.code = code
    codedata.longest_name = 0

    # Find the longest name
    # TODO: Try to find a simpler solution that avoids double traverse
    def longest_name_func(tree_path, level, item, user_data):
        if len(item.name) > user_data.longest_name:
            user_data.longest_name = len(item.name)

    menu.traverse(callback_leaf=longest_name_func,
                  user_data=codedata,
                  verbose=False)

    # Generate all code
    menu.traverse(callback_leaf=leaf_func,
                  user_data=codedata,
                  verbose=False)

    code = codedata.code

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_model_inspect(compute_function, classname, outfile, default_field):
    """
    Generate the Flask form by using inspect on the
    given function. Default values in the function
    are kept as default values in the form class.
    Variables without a default value are assumed
    to be represented by `default_field` forms.
    """

    code = '''\
import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class %(classname)s(wtf.Form):
''' % vars()

    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults  = inspect.getargspec(compute_function).defaults

    # Give a warning if positional
    # arguments because the user must then convert form_data
    # elements explicitly.
    compute_function_name = compute_function.__name__
    if (not defaults or len(defaults) != len(arg_names)):
        print """
*** Warning:
%(compute_function_name)s has positional arguments.
We recommend to use keyword arguments only since this
generator can then detect the type of each argument and
assign the proper form field type.

The default form field for the positional arguments is
%(default_field)s, which requires explicit conversion
for all arguments that are not of this type.
See %(outfile)s, # Convert data ... for what type
of code that may be needed.
""" % vars()

    # Make defaults as long as arg_names so we can traverse both with zip
    if defaults:
        defaults = ["none"]*(len(arg_names)-len(defaults)) + list(defaults)
    else:
        defaults = ["none"]*len(arg_names)
    longest_name = max(len(name) for name in arg_names)

    # Need to use wtforms for all fields except FloatField
    if default_field != "FloatField":
        if default_field[:4] != "wtf.":
            default_field = "wtf." + default_field

    # Map type of default to right form field
    class Dummy:
        pass

    class_tp = Dummy()  # for user-defined types
    import numpy
    array_tp = numpy.arange(1)
    type2form = {type(1.0):  'FloatField',
                 type(1):    'wtf.IntegerField',
                 type(''):   'wtf.TextField',
                 type(True): 'wtf.BooleanField',
                 type([]):   'wtf.TextField',
                 type(()):   'wtf.TextField',
                 type(None): 'wtf.TextField',
                 type(class_tp): 'wtf.TextField',
                 type(array_tp): 'wtf.TextField',
                 }
    # A compute(form) function will convert from TextField string
    # to the right types: list, tuple, user-defined class, array, via
    # eval

    for name, value in zip(arg_names, defaults):
        # No default value?
        if value == "none":
            code += """\
    %%(name)-%ds = %%(default_field)s(validators=[wtf.validators.InputRequired()])
""" % longest_name % vars()

        else:
            if type(value) in type2form:
                # HPL's assumption regarding filename
                if "filename" in name:
                    form = 'wtf.FileField'
                    code += """\
    %%(name)-%ds = %%(form)s(validators=[wtf.validators.InputRequired()])
""" % longest_name % vars()

                else:
                    form = type2form[type(value)]

                    if isinstance(value, bool):
                        code += """\
    %%(name)-%ds = %%(form)s(default=%%(value)s)
""" % longest_name % vars()

                    else:
                        code += """\
    %%(name)-%ds = %%(form)s(default=""" % longest_name % vars()

                        # Text input
                        if type2form[type(value)] == 'wtf.TextField':
                            if isinstance(value, numpy.ndarray):
                                # Hack to make arrays look like lists
                                value = value.tolist()

                            code += "'%(value)s'," % vars()

                        # Floats, integers,
                        else:
                            code += "%(value)s," % vars()
                        code += """
                             validators=[wtf.validators.InputRequired()])
"""
            else:
                raise TypeError('Argument %s=%s is not supported.' %
                                (name, type(value)))

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_model(compute_func, classname, outfile, default_field,
                    menu=None, overwrite=False):
    """
    Generate the Flask form using menu if given,
    else use inspect on the compute function.
    """

    if not overwrite and outfile is not None and os.path.isfile(outfile):
        from distutils.util import strtobool
        if not strtobool(raw_input(
            "The file %s already exists. Overwrite? [Y/N]: " % outfile)):
            return None

    if menu is not None:
        return generate_model_menu(
            compute_func, classname, outfile, menu)
    else:
        return generate_model_inspect(
            compute_func, classname, outfile, default_field)

from parampool.misc.assert_utils import assert_equal_text

def test_inspect():
    model_code = """\
import wtforms as wtf
from parampool.html5.flask.fields import FloatField

class Test(wtf.Form):
    a        = FloatField(validators=[wtf.validators.InputRequired()])
    b        = wtf.IntegerField(default=1,
                             validators=[wtf.validators.InputRequired()])
    c        = FloatField(default=1.0,
                             validators=[wtf.validators.InputRequired()])
    func     = wtf.TextField(default='y(x)',
                             validators=[wtf.validators.InputRequired()])
    mybool   = wtf.BooleanField(default=True)
    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])
"""

    def compute(a, b=1, c=1.0, func='y(x)', mybool=True, filename='tmp.tmp'):
        return None

    generated_code = generate_model(compute, "Test", outfile=None,
                                     default_field="FloatField")
    assert_equal_text(generated_code, model_code,
                      'newly generated', 'reference result',
                      msg='Error in generated text!')

def test_menu():
    from math import pi
    from parampool.menu.UI import listtree2Menu

    model_code = """\
import wtforms as wtf
from parampool.html5.flask.fields import FloatField, RangeFloatField

class Test(wtf.Form):
     a     = wtf.IntegerField(u'velocity of body (km/h)',
                        default=120,
                        validators=[wtf.validators.InputRequired()])
     b     = FloatField(u'mass (kg)',
                        default=0.43,
                        validators=[wtf.validators.InputRequired()])
     c     = FloatField(u'volume',
                        default=0.00418146,
                        validators=[wtf.validators.InputRequired()])
     C_D   = FloatField(u'drag coefficient',
                        default=0.2,
                        validators=[wtf.validators.InputRequired(),
                                    wtf.validators.NumberRange(0,
                                                               1)])
     test1 = RangeFloatField(u'rangetest',
                        onchange="showValue(this.value)",
                        min=0,
                        max=1,
                        default=0.5,
                        validators=[wtf.validators.InputRequired(),
                                    wtf.validators.NumberRange(0,
                                                               1)])
     test2 = wtf.FileField(u'filetest',
                        validators=[wtf.validators.InputRequired())
     test3 = wtf.SelectField(u'choicetest',
                        default='y',
                        validators=[wtf.validators.InputRequired()],
                        choices=[('y', 'y'), ('y3', 'y^3'), ('siny', 'sin(y)')])
     test4 = wtf.TextField(u'texttest',
                        default='Test',
                        validators=[wtf.validators.InputRequired()])
     test5 = wtf.BooleanField(u'booltest', default=True)
"""

    menu_tree = [
        'main', [
            dict(name='a', default=120, unit='km/h',
                 help='velocity of body', str2type=eval),
            'test properties1', [
                dict(name='b', default=0.43, unit='kg', help='mass'),
                dict(name='c', default=pi*0.11**3, help='volume'),
                dict(name='C_D', default=0.2, minmax=[0,1],
                     help='drag coefficient'),
                ],
            'test properties2', [
                dict(name='test1', default=0.5, help='rangetest',
                     widget='RangeField', minmax=[0,1]),
                dict(name='test2', default='', help='filetest',
                     widget='FileField'),
                dict(name='test3', default='y', help='choicetest',
                     options=[('y', 'y'), ('y3', 'y^3'), ('siny', 'sin(y)')]),
                dict(name='test4', default='Test', help='texttest'),
                dict(name='test5', default=True, help='booltest'),
                ],
            ],
        ]

    menu = listtree2Menu(menu_tree)
    def compute_func(a, b, c, C_D, test1, test2, test3, test4):
        return None

    generated_code = generate_model(compute_func, "Test", outfile=None,
                                    default_field="FloatField", menu=menu)
    assert_equal_text(generated_code, model_code,
                      'newly generated', 'reference result',
                      msg='Error in generated text!')

if __name__ == '__main__':
    test_inspect()
    test_menu()
