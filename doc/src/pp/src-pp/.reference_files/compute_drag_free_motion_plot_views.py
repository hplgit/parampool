from compute import compute_drag_free_motion_plot as compute_function

from django.shortcuts import render_to_response
from django.template import RequestContext
from compute_drag_free_motion_plot_models import DragFreeMotionPlot, DragFreeMotionPlotForm

def index(request):
    result = None

    form = DragFreeMotionPlotForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form = form.save(commit=False)
        result = compute(form)
        form = DragFreeMotionPlotForm(request.POST or None)

    return render_to_response(
        "compute_drag_free_motion_plot_index.html",
        {"form": form,
         "result": result,

        },
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
