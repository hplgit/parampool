from compute import compute_motion_and_forces_with_pool as compute_function

# Pool object (must be imported before compute_motion_and_forces_with_pool_pool_definition_list_models
from compute import pool_definition_list as pool_function
pool = pool_function()

# Can define other default values in a file: --poolfile name
from parampool.pool.UI import set_defaults_from_file
pool = set_defaults_from_file(pool)
# Can override default values on the command line
from parampool.pool.UI import set_values_from_command_line
pool = set_values_from_command_line(pool)

from django.shortcuts import render_to_response
from django.template import RequestContext
from compute_motion_and_forces_with_pool_pool_definition_list_models import MotionAndForcesWithPool, MotionAndForcesWithPoolForm

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
        "compute_motion_and_forces_with_pool_pool_definition_list_index.html",
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

from parampool.pool.UI import write_poolfile
write_poolfile(pool, '.tmp_pool.dat')
