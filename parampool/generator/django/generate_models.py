def generate_models_menu(compute_function, classname, outfile, menu):
    """
    Generate Django ModelForm by iterating through
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
        label = " "
        if item.data.has_key("help"):
            label += item.data["help"]
        if item.data.has_key("unit"):
            label += " (" + item.data["unit"] + ")"

        if item.data.has_key("minmax"):
            minvalue = item.data["minmax"][0]
            maxvalue = item.data["minmax"][1]

        widget = item.data.get("widget", None)

        if widget is not None:
            # FIXME: Slider not yet supported.
            if widget == "RangeField" or widget == "IntRangeField":
                raise NotImplementedError("Slider not yet supported.")

            elif widget == "FileField":
                user_data.code += """ \
    %%(name)-%ds = models.FileField(verbose_name='%%(label)s',
                        upload_to='uploads/')
""" % user_data.longest_name % vars()

        else:
            # Choose between given options
            if item.data.has_key("options"):
                choices = item.data["options"]
                # TODO: Implement this!

            # Text input
            elif isinstance(default, str):
                user_data.code += """ \
    %%(name)-%ds = models.TextField(verbose_name='%%(label)s',
                        default='%%(default)s')
""" % user_data.longest_name % vars()

            # Regular float input
            elif isinstance(default, float):
                if item.data.has_key("minmax"):
                    user_data.code += """ \
    %%(name)-%ds = MinMaxFloat(verbose_name='%%(label)s',
                        default=%%(default)g,
                        min_value=%%(minvalue)g,
                        max_value=%%(maxvalue)g)
""" % user_data.longest_name % vars()
                else:
                    user_data.code += """ \
    %%(name)-%ds = models.FloatField(verbose_name='%%(label)s',
                        default=%%(default)g)
""" % user_data.longest_name % vars()



            # Integer
            elif isinstance(default, int):
                if item.data.has_key("minmax"):
                    # TODO: Implement MinMaxInt
                    pass

                user_data.code += """ \
    %%(name)-%ds = models.IntegerField(verbose_name='%%(label)s',
                        default=%%(default)g)
""" % user_data.longest_name % vars()

            # Anything else
            else:
                raise TypeError('Argument %s=%s is not supported.' %
                                name, type(value))

    code = '''\
from django.db import models
from django.forms import ModelForm
from parampool.html5.django.models import MinMaxFloat

class %(classname)s(models.Model):
''' % vars()

    import inspect
    arg_names = inspect.getargspec(compute_function).args
    longest_name = max(len(name) for name in arg_names)

    codedata = CodeData()
    codedata.code = code
    codedata.longest_name = longest_name

    menu.traverse(callback_leaf=leaf_func,
                       user_data=codedata,
                       verbose=False)

    code = codedata.code
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
See %(outfile)s, # Convert data ... for what type
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
    type2form = {type(1.0):  'FloatField',
                 type(1):    'wtf.IntegerField',
                 type(''):   'wtf.TextField',
                 type(True): 'wtf.BooleanField',
                 type([]):   'wtf.TextField',
                 type(()):   'wtf.TextField',
                 type(None): 'wtf.TextField',
                 type(class_tp):        'wtf.TextField',
                 type(numpy.ndarray):   'wtf.TextField',
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
    %%(name)-%ds = models.%%(form)s(verbose_name=' %%(name)s',
                                    upload_to='uploads/')
""" % longest_name % vars()

                else:
                    form = type2form[type(value)]

                    # FIXME: Implementation for ChoiceField
                    if isinstance(value, bool):
                        raise NotImplementedError("Choices not yet supported.")
                    else:
                        code += """\
    %%(name)-%ds = models.%%(form)s(verbose_name=' %%(name)s',
                                    default=""" % longest_name % vars()

                        # Text input
                        if isinstance(value, str):
                            code += "'%(value)s')\n" % vars()

                        # Floats, integers, whatever...
                        else:
                            code += "%(value)s)\n" % vars()
            else:
                raise TypeError('Argument %s=%s is not supported.' %
                                name, type(value))
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


def generate_models(compute_func, classname, outfile, default_field,
                    menu=None):
    """
    Generate the Django ModelForm using menu if given,
    else use inspect on the compute function.
    """
    if menu is not None:
        return generate_models_menu(
            compute_func, classname, outfile, menu)
    else:
        return generate_models_inspect(
            compute_func, classname, outfile, default_field)
