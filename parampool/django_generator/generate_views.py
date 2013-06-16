def generate_views(compute_function,
                   classname,
                   outfile,
                   output_template):

    compute_function_name = compute_function.__name__
    compute_function_file = compute_function.__module__

    code = '''\
from django.shortcuts import render_to_response
from django.template import RequestContext
from models import %(classname)sForm
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
    form_values = [getattr(form, name) for name in arg_names
                   if hasattr(form, name)]
''' % vars()

    # Give a warning and insert helper code if positional
    # arguments because the user must then convert form_data
    # elements explicitly.
    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults  = inspect.getargspec(compute_function).defaults
    if len(defaults) != len(arg_names):
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

    code += '''
    # Run computations
    result = compute_function(*form_values)
    return result
''' % vars()

    if outfile is None:
        return code
    else:
        out = open(outfile, 'w')
        out.write(code)
        out.close()
