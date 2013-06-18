from django.shortcuts import render_to_response
from django.template import RequestContext
from models import MysimplefuncForm
from compute import mysimplefunc as compute_function

def index(request):
    result = None
    form = MysimplefuncForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        result = compute(form)
        form = MysimplefuncForm(request.POST)

    return render_to_response(
        "index.html",
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

    # Convert data to right types (if necessary)
    # for i in range(len(form_data)):
    #    name = arg_names[i]
    #    if name == '...':
    #         form_data[i] = int(form_data[i])
    #    elif name == '...':

    # Run computations
    result = compute_function(*form_data)
    return result
