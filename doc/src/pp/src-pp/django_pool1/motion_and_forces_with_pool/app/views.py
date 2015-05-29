from compute import compute_motion_and_forces_with_pool as compute_function

# Pool object (must be imported before models
from compute import pool_definition_list as pool_function
pool = pool_function()

from django.shortcuts import render_to_response
from django.template import RequestContext
from models import MotionAndForcesWithPool, MotionAndForcesWithPoolForm

def index(request):
    result = None

    form = MotionAndForcesWithPoolForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        for field in form:
            name = MotionAndForcesWithPool._meta.get_field(field.name).verbose_name.strip()
            value = field.data
            pool.set_value(name, value)
        result = compute(pool)
        form = MotionAndForcesWithPoolForm(request.POST)

    return render_to_response(
        "index.html",
        {"form": form,
         "result": result,

        },
        context_instance=RequestContext(request))

def compute(pool):
    """
    Generic function for calling compute_function with values
    taken from the pool object.
    Return the output from the compute_function.
    """

    # compute_function must have only one positional argument
    # named pool
    import inspect
    arg_names = inspect.getargspec(compute_function).args
    if len(arg_names) == 1 and arg_names[0] == "pool":
        result = compute_function(pool)
    else:
        raise TypeError('%s(%s) can only have one argument named "pool"'
                        % (compute_function.__name__, ', '.join(arg_names)))
    return result
