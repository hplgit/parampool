from django.shortcuts import render_to_response
from django.template import RequestContext
from compute_average_models import AverageForm
from compute import compute_average as compute_function

import os
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

def index(request):
    result = None

    filename = None
    form = AverageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        for field in form:
            if field.name in request.FILES:
                filename = field.data.name
                with open(os.path.join(UPLOAD_DIR, filename), 'wb+') as destination:
                    for chunk in field.data.chunks():
                        destination.write(chunk)
        form = form.save(commit=False)
        request.session["filename"] = filename
        result = compute(form, request)
        form = AverageForm(request.POST, request.FILES)

    return render_to_response(
        "compute_average_index.html",
        {"form": form,
         "result": result,

        },
        context_instance=RequestContext(request))

def compute(form, request):

    """
    Generic function for compute_function with arguments
    taken from a form object (django.forms.ModelForm subclass).
    Return the output from the compute_function.
    """
    # Extract arguments to the compute function
    import inspect
    arg_names = inspect.getargspec(compute_function).args


    form_data = []
    for name in arg_names:
        if name != "filename":
            if hasattr(form, name):
                form_data.append(getattr(form, name))
        else:
            form_data.append(request.session.get("filename"))

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

    # Run computations
    result = compute_function(*form_data)
    return result
