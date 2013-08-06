import os
import parampool.utils

def generate_model_menu(classname, outfile, menu):
    """
    Generate Flask form by iterating through
    leaf nodes in the given menu object.
    """
    from parampool.menu.DataItem import DataItem

    class CodeData(object):
        """Object to hold output code through tree recursion."""
        id = 0
        parent_id = [-1]

    def leaf_func(tree_path, level, item, user_data):
        name = item.name
        field_name = parampool.utils.legal_variable_name(name)
        default = item.data["default"]

        # Make label
        label = ""
        if 'name' in item.data:
            label += item.data['name']

        widget = item.data.get("widget")

        if 'minmax' in item.data:
            minvalue = item.data['minmax'][0]
            maxvalue = item.data['minmax'][1]
        else:
            minvalue, maxvalue = DataItem.defaults['minmax']
            if widget in ("range", "integer_range"):
                raise TypeError("Cannot create a range without min/max values")

        if 'range_step' in item.data:
            range_step = item.data['range_step']
        else:
            range_steps = DataItem.defaults['range_steps']
            range_step = (maxvalue - minvalue)/range_steps
        number_step = item.data.get('number_step',
                                    DataItem.defaults['number_step'])

        # Not all widgets have a size attribute so we set size
        # in the template

        if widget == "integer":
            # NOTE: Might be problem with resizing field since
            # we do not specify min, max, and step - does this
            # html5.IntegerField have those attributes? No, it
            # gets its __init__ from wtforms.fields.Field
            user_data.code += """\

    %%(field_name)-%ds = html5.IntegerField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default=%%(default)s,
        validators=[wtf.validators.InputRequired()\
""" % user_data.longest_name % vars()
            if 'minmax' in item.data:
                user_data.code += """,
                    wtf.validators.NumberRange(%(minvalue)g, %(maxvalue)g)],
        min=%(minvalue)g, max=%(maxvalue)g, step=1)
""" % vars()
            else:
                user_data.code += "])\n"

        elif widget == "float":
            user_data.code += """\

    %%(field_name)-%ds = HTML5FloatField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default=%%(default)g,
        validators=[wtf.validators.InputRequired()\
""" % user_data.longest_name % vars()
            if 'minmax' in item.data:
                user_data.code += """,
                    wtf.validators.NumberRange(%(minvalue)g, %(maxvalue)g)],
        min=%(minvalue)g, max=%(maxvalue)g, step=%(number_step)g)
""" % vars()
            else:
                user_data.code += """],
        step='any',
        #min=%(minvalue)g, max=%%(maxvalue)g, step=%(number_step)g,
        )\n""" % vars()


        elif widget == "range":
            user_data.code += """\

    %%(field_name)-%ds = FloatRangeField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default=%%(default)g,
        onchange="showValue(this.value)",
        min=%%(minvalue)g, max=%%(maxvalue)g, step=%%(range_step)g,
        validators=[wtf.validators.InputRequired(),
                    wtf.validators.NumberRange(%%(minvalue)g, %%(maxvalue)g)])
""" % user_data.longest_name % vars()

        elif widget == "integer_range":
            user_data.code += """\

    %%(field_name)-%ds = IntegerRangeField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default=%%(default)g,
        onchange="showValue(this.value)",
        min=%%(minvalue)g, max=%%(maxvalue)g, step=%%(range_step)g,
        validators=[wtf.validators.InputRequired(),
                    wtf.validators.NumberRange(%%(minvalue)g, %%(maxvalue)g)])
""" % user_data.longest_name % vars()

        elif widget == "file":
            user_data.code += """\

    %%(field_name)-%ds = wtf.FileField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        validators=[wtf.validators.InputRequired()])
""" % user_data.longest_name % vars()

        elif widget == "select":
            if 'options' in item.data:
                choices = item.data["options"]
                if not isinstance(choices[0], (list, tuple)):
                    # Flask requires choices to be two-tuples
                    choices = [(choice,choice) for choice in choices]

                user_data.code += """\

    %%(field_name)-%ds = wtf.SelectField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default='%%(default)s',
        validators=[wtf.validators.InputRequired()],
        choices=%%(choices)s)
""" % user_data.longest_name % vars()
            else:
                print "*** ERROR: Cannot use widget select without any options."
                import sys
                sys.exit(1)

        elif widget == "checkbox":
                user_data.code += """\

    %%(field_name)-%ds = wtf.BooleanField(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default=%%(default)s)
""" % user_data.longest_name % vars()

        else:
            widget2field = {"textline": "html5.TextField",
                            "textarea": "wtf.TextAreaField",
                            "email":    "html5.EmailField",
                            "hidden":   "wtf.HiddenField",
                            "password": "wtf.PasswordField",
                            "url":      "html5.URLField",
                            "tel":      "html5.TelField"}

            if widget in widget2field.keys():
                field = widget2field[widget]
                user_data.code += """\

    %%(field_name)-%ds = %%(field)s(
        label=u'%%(label)s',
        description=u'%%(label)s',
        default='%%(default)s',
        validators=[wtf.validators.InputRequired()])
""" % user_data.longest_name % vars()
            else:
                raise TypeError("Widget '%s' not allowed" % widget)


    code = '''\
import wtforms as wtf
from parampool.html5.flask.fields import HTML5FloatField, FloatRangeField, IntegerRangeField
import flask.ext.wtf.html5 as html5

class %(classname)s(wtf.Form):
''' % vars()

    codedata = CodeData()
    codedata.code = code
    codedata.longest_name = 0

    # Find the longest name
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
from parampool.html5.flask.fields import HTML5FloatField

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
See controller.py, # Convert data ... for what type
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
            "The file %s already exists. Overwrite? [Y/n]: " % outfile)):
            return None

    if menu is not None:
        return generate_model_menu(classname, outfile, menu)
    else:
        return generate_model_inspect(
            compute_func, classname, outfile, default_field)

from parampool.utils import assert_equal_text

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
from parampool.html5.flask.fields import FloatField, FloatRangeField, IntegerRangeField
import flask.ext.wtf.html5 as html5

class Test(wtf.Form):
     a     = html5.TextField(u'velocity of body (km/h)',
                        default='120',
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
     test1 = FloatRangeField(u'rangetest',
                        onchange="showValue(this.value)",
                        min=0,
                        max=1,
                        default=0.5,
                        validators=[wtf.validators.InputRequired(),
                                    wtf.validators.NumberRange(0,
                                                               1)])
     test2 = wtf.FileField(u'filetest',
                        validators=[wtf.validators.InputRequired()])
     test3 = wtf.SelectField(u'choicetest',
                        default='y',
                        validators=[wtf.validators.InputRequired()],
                        choices=[('y', 'y'), ('y3', 'y^3'), ('siny', 'sin(y)')])
     test4 = html5.TextField(u'texttest',
                        default='Test',
                        validators=[wtf.validators.InputRequired()])
     test5 = wtf.BooleanField(u'booltest', default=True)
"""

    menu_tree = [
        'main', [
            dict(name='a', default='120', unit='km/h',
                 help='velocity of body', str2type=eval),
            'test properties1', [
                dict(name='b', default=0.43, unit='kg', help='mass'),
                dict(name='c', default=pi*0.11**3, help='volume'),
                dict(name='C_D', default=0.2, minmax=[0,1],
                     help='drag coefficient'),
                ],
            'test properties2', [
                dict(name='test1', default=0.5, help='rangetest',
                     widget='range', minmax=[0,1]),
                dict(name='test2', default='', help='filetest',
                     widget='file'),
                dict(name='test3', default='y', help='choicetest', widget="select",
                     options=[('y', 'y'), ('y3', 'y^3'), ('siny', 'sin(y)')]),
                dict(name='test4', default='Test', help='texttest'),
                dict(name='test5', default=True, str2type=bool, help='booltest'),
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
