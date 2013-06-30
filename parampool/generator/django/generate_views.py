def generate_views(compute_function,
                   classname,
                   outfile,
                   output_template,
                   output_models):

    compute_function_name = compute_function.__name__
    compute_function_file = compute_function.__module__

    models_module = output_models.replace('.py', '')

    code = '''\
from django.shortcuts import render_to_response
from django.template import RequestContext
from %(models_module)s import %(classname)sForm
from %(compute_function_file)s import %(compute_function_name)s as compute_function

def index(request):
    result = None
    form = %(classname)sForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        result = compute(form)
        form = %(classname)sForm(request.POST)

    return render_to_response(
        "%(output_template)s",
        {"form": form,
         "result": result},
        context_instance=RequestContext(request))

def compute(form):
    """
    Generic function for compute_function with arguments
    taken from a form object (django.forms.ModelForm subclass).
    Return the output from the compute_function.
    """
    # Extract arguments to the compute function
    import inspect
    arg_names = inspect.getargspec(compute_function).args

    # Extract values from form
    form_data = [getattr(form, name) for name in arg_names
                 if hasattr(form, name)]
''' % vars()

    # Give a warning and insert helper code if positional
    # arguments because the user must then convert form_data
    # elements explicitly.
    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults  = inspect.getargspec(compute_function).defaults
    if defaults is not None and len(defaults) != len(arg_names):
        # Insert example on argument conversion since there are
        # positional arguments where default_field might be the
        # wrong type
        code += '''
    # Convert data to right types (if necessary)
    # for i in range(len(form_data)):
    #    name = arg_names[i]
    #    if name == '...':
    #         form_data[i] = int(form_data[i])
    #    elif name == '...':
'''
    else:
        # We have default values: do right conversions
        code += '''
    defaults  = inspect.getargspec(compute_function).defaults

    # Make defaults as long as arg_names so we can traverse both with zip
    if defaults:
        defaults = ["none"]*(len(arg_names)-len(defaults)) + list(defaults)
    else:
        defaults = ["none"]*len(arg_names)

    # Convert form data to the right type:
    import numpy
    for i in range(len(form_data)):
        if defaults[i] != "none":
            #if isinstance(defaults[i], (str,bool,int,float)): # bool not ready
            if isinstance(defaults[i], (str,int,float)):
                pass  # special widgets for these types do the conversion
            elif isinstance(defaults[i], numpy.ndarray):
                form_data[i] = numpy.array(eval(form_data[i]))
            elif defaults[i] is None:
                if form_data[i] == 'None':
                    form_data[i] = None
                else:
                    try:
                        # Try eval if it succeeds...
                        form_data[i] = eval(form_data[i])
                    except:
                        pass # Just keep the text
            else:
                # Use eval to convert to right type (hopefully)
                try:
                    form_data[i] = eval(form_data[i])
                except:
                    print 'Could not convert text %s to %s for argument %s' % (form_data[i], type(defaults[i]), arg_names[i])
                    print 'when calling the compute function...'
'''

    code += '''
    # Run computations
    result = compute_function(*form_data)
    return result
''' % vars()

    if outfile is None:
        return code
    else:
        out = open(outfile, 'w')
        out.write(code)
        out.close()
