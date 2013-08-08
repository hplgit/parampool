import parampool.utils

def generate_models_menu(classname, outfile, menu):
    """
    Generate Django ModelForm by iterating through
    leaf nodes in the given menu object.
    """
    from parampool.menu.DataItem import DataItem
    default_widget_size = DataItem.defaults['widget_size']

    class CodeData(object):
        """Object to hold output code through tree recursion."""
        id = 0
        parent_id = [-1]

    def leaf_func(tree_path, level, item, user_data):
        name = item.name
        field_name = parampool.utils.legal_variable_name(name)
        field_name_quoted = "'%s'" % field_name
        default = item.data["default"]

        # Make label
        label = ""
        if 'name' in item.data:
            label += item.data['name']
        verbose_name = ' ' + label  # space avoids upper case first char

        widget = item.data.get("widget")
        widget_size = item.get("widget_size", default=default_widget_size)

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

        if widget in ("integer", "integer_range"):
            user_data.code += """\

    %%(field_name)-%ds = models.IntegerField(
        verbose_name='%%(verbose_name)s',
        default=%%(default)g)
""" % user_data.longest_name % vars()
            # TODO: Minmax for integers
            if 'minmax' in item.data:
                pass

            if widget == "integer":
                user_data.widget_specs += """
            #%%(field_name_quoted)-%ds: NumberInput(attrs={'size': %%(widget_size)d, 'min': %%(minvalue)s, 'max': %%(maxvalue)s, 'step': %%(number_step)s}),""" % user_data.longest_name % vars()
                user_data.widget_specs += """
            %%(field_name_quoted)-%ds: NumberInput(attrs={'size': %%(widget_size)d, 'step': 'any'}),""" % user_data.longest_name % vars()
            elif widget == "integer_range":
                user_data.widget_specs += """
            %%(field_name_quoted)-%ds: RangeInput(attrs={'size': %%(widget_size)d, 'min': %%(minvalue)s, 'max': %%(maxvalue)s, 'step': %%(range_step)g, 'onchange': 'showValue(this.value)'}),""" % user_data.longest_name % vars()

        elif widget in ("float", "range"):
            if 'minmax' in item.data:
                user_data.code += """\

    %%(field_name)-%ds = MinMaxFloat(
        verbose_name='%%(verbose_name)s',
        default=%%(default)g,
        min_value=%%(minvalue)g, max_value=%%(maxvalue)g)
""" % user_data.longest_name % vars()
            else:
                user_data.code += """\

    %%(field_name)-%ds = models.FloatField(
        verbose_name='%%(verbose_name)s',
        default=%%(default)g)
""" % user_data.longest_name % vars()

            if widget == "range":
                user_data.widget_specs += """
            %%(field_name_quoted)-%ds: RangeInput(attrs={'size': %%(widget_size)d, 'min': %%(minvalue)s, 'max': %%(maxvalue)s, 'step': %%(range_step)g, 'onchange': 'showValue(this.value)'}),""" % user_data.longest_name % vars()
            elif widget == "float":
                user_data.widget_specs += """
            %%(field_name_quoted)-%ds: NumberInput(attrs={'size': %%(widget_size)d, 'min': %%(minvalue)s, 'max': %%(maxvalue)s, 'step': %%(number_step)g}),""" % user_data.longest_name % vars()
                user_data.widget_specs += """
            #%%(field_name_quoted)-%ds: NumberInput(attrs={'size': %%(widget_size)d, 'step': 'any'}),""" % user_data.longest_name % vars()

        elif widget == "file":
            user_data.code += """\

    %%(field_name)-%ds = models.FileField(
        verbose_name='%%(verbose_name)s',
        upload_to='uploads/')
""" % user_data.longest_name % vars()

            user_data.widget_specs += """
            # AEJ: TextInput for File removes the 'Choose File' button.
            #%%(field_name_quoted)-%ds: TextInput(attrs={'size': %%(widget_size)d}),""" % user_data.longest_name % vars()

        elif widget == "select":
            if 'options' in item.data:
                choices = item.data["options"]
                if not isinstance(choices[0], (list, tuple)):
                    # Django requires choices to be two-tuples
                    choices = [(choice,choice) for choice in choices]
                user_data.code += """\

    %%(field_name)-%ds = models.CharField(
        verbose_name='%%(verbose_name)s',
        max_length=50,
        default='%%(default)s',
        choices=%%(choices)s)
""" % user_data.longest_name % vars()

            else:
                print "*** ERROR: Cannot use widget 'select' without any options."
                import sys
                sys.exit(1)
            # No widget size spec for options

        elif widget == "checkbox":
            user_data.code += """\

    %%(field_name)-%ds = models.BooleanField(
        verbose_name='%%(verbose_name)s',
        default=%%(default)s)
""" % user_data.longest_name % vars()

        elif widget == "textline":
            user_data.code += """\

    %%(field_name)-%ds = models.CharField(
        verbose_name='%%(verbose_name)s',
        default='%%(default)s',
        max_length=50)
""" % user_data.longest_name % vars()

            user_data.widget_specs += """
            %%(field_name_quoted)-%ds: TextInput(attrs={'size': %%(widget_size)d}),""" % user_data.longest_name % vars()
        else:
            not_supported = ("hidden", "password", "tel")
            if widget in not_supported:
                print "*** ERROR: Widget '%s' is not currently supported." % widget
                import sys
                sys.exit(1)

            widget2field = {
                "textarea": "models.TextField",
                "email":    "models.EmailField",
                "url":      "models.URLField"}
            widget2widget = {
                "textarea": "Textarea",
                "email":    "EmailInput",
                "url":      "URLInput"}

            if widget in widget2field.keys():
                field = widget2field[widget]
                django_widget = widget2widget[widget]
                user_data.code += """\

    %%(field_name)-%ds = %%(field)s(
        verbose_name='%%(verbose_name)s',
        default='%%(default)s')
""" % user_data.longest_name % vars()

                user_data.widget_specs += """
            %%(field_name_quoted)-%ds: %%(django_widget)s(attrs={'size': %%(widget_size)d}),""" % user_data.longest_name % vars()
            else:
                raise TypeError("Widget '%s' not allowed" % widget)


    code = '''\
from django.db import models
from django.forms import ModelForm
from parampool.html5.django.models import MinMaxFloat
from parampool.html5.django.forms.widgets import \\
     TextInput, NumberInput, RangeInput, Textarea, EmailInput, URLInput

# Note: The verbose_name attribute starts with a blank to avoid
# that Django forces the first character to be upper case.

class %(classname)s(models.Model):
''' % vars()

    codedata = CodeData()
    codedata.code = code
    codedata.widget_specs = ''
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
    widget_specs = codedata.widget_specs
    code += """
class %(classname)sForm(ModelForm):
    class Meta:
        model = %(classname)s
        widgets = {%(widget_specs)s}
""" % vars()

    if outfile is None:
        return code
    else:
        out = open(outfile, 'w')
        out.write(code)
        out.close()


def generate_models_inspect(compute_function, classname,
                            outfile, default_field):
    """
    Generate the Django ModelForm by using inspect on the
    given function. Default values in the function
    are kept as default values in the form class.
    Variables without a default value are assumed
    to be floats.
    """

    code = '''\
from django.db import models
from django.forms import ModelForm

class %(classname)s(models.Model):
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
See views.py, # Convert data ... for what type
of code that may be needed.
""" % vars()

    # Avoid possible index error
    if defaults:
        defaults = ["none"]*(len(arg_names)-len(defaults)) + list(defaults)
    else:
        defaults = ["none"]*len(arg_names)
    longest_name = max(len(name) for name in arg_names)

    class Dummy:
        pass

    class_tp = Dummy()  # for user-defined types
    import numpy
    array_tp = numpy.arange(1)
    textfield = 'CharField'
    type2form = {type(1.0):  'FloatField',
                 type(1):    'IntegerField',
                 type(''):   textfield,
                 #type(True): 'ChoiceField',
                 type(True): textfield,
                 type([]):   textfield,
                 type(()):   textfield,
                 type(None): textfield,
                 type(class_tp): textfield,
                 type(array_tp): textfield,
                 }
    # A compute(form) function will convert from TextField string
    # to the right types: list, tuple, user-defined class, array, via
    # eval

    for name, value in zip(arg_names, defaults):

        # No default value
        if value is "none":
            code += """\
    %%(name)-%ds = models.%%(default_field)s(verbose_name=' %%(name)s')
""" % longest_name % vars()

        else:
            if type(value) in type2form:
                # HPL's assumption regarding filename
                if "filename" in name:
                    form = 'FileField'
                    code += """\
    %%(name)-%ds = models.%%(form)s(verbose_name=' %%(name)s', upload_to='uploads/', blank=True)
""" % longest_name % vars()

                else:
                    form = type2form[type(value)]

                    # FIXME: Implementation for ChoiceField
                    if 0: #isinstance(value, bool):
                        #raise NotImplementedError("Choices not yet supported.")
                        pass
                    else:
                        code += """\
    %%(name)-%ds = models.%%(form)s(verbose_name=' %%(name)s', default=""" % longest_name % vars()

                        # Text input
                        if type2form[type(value)] == textfield:
                            if isinstance(value, numpy.ndarray):
                                # Hack to make arrays look like lists
                                value = value.tolist()

                            code += "'%(value)s'," % vars()

                        # Floats, integers, ...
                        else:
                            code += "%(value)s," % vars()
                        if form == 'CharField':
                            code += 'max_length=28,'
                        code += ')\n'
            else:
                raise TypeError('Argument %s=%s is not supported.' %
                                (name, type(value)))
    code += """
class %(classname)sForm(ModelForm):
    class Meta:
        model = %(classname)s
""" % vars()


    if outfile is None:
        return code
    else:
        out = open(outfile, 'w')
        out.write(code)
        out.close()

def loginize(classname, outfile):
    f = open(outfile, 'r')
    code = f.read()
    f.close()
    f = open(outfile, 'w')
    f.write("""\
from django.contrib.auth.models import User
%(code)s""" % vars())
    f.close()

    f = open(outfile, 'r')
    lines = f.readlines()
    f.close()

    code = ""
    append = False
    for line in lines:
        code += line
        if line == "class %(classname)sForm(ModelForm):\n" % vars():
            append = False
        if line == "class %(classname)s(models.Model):\n" % vars():
            newcode = """
class %(classname)sUser(models.Model):
""" % vars()
            append = True
            continue
        if append:
            newcode += line

    newcode += """\

    user = models.ForeignKey(User)
    result = models.TextField(blank=True)
    comments = models.TextField(blank=True)


class %(classname)sUserForm(ModelForm):
    class Meta:
        model = %(classname)sUser""" % vars()


    code += newcode

    if outfile is None:
        return code
    else:
        out = open(outfile, 'w')
        out.write(code)
        out.close()

def generate_models(compute_func, classname, outfile, default_field,
                    menu=None, login=False):
    """
    Generate the Django ModelForm using menu if given,
    else use inspect on the compute function.
    """

    if menu is not None:
        generate_models_menu(classname, outfile, menu)
    else:
        generate_models_inspect(
            compute_func, classname, outfile, default_field)

    if login:
        loginize(classname, outfile)
