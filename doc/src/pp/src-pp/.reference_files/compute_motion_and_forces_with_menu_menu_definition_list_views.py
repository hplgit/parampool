from compute import compute_motion_and_forces_with_menu as compute_function

# Menu object (must be imported before compute_motion_and_forces_with_menu_menu_definition_list_models
from compute import menu_definition_list as menu_function
menu = menu_function()

# Can define other default values in a file: --menufile name
from parampool.menu.UI import set_defaults_from_file
menu = set_defaults_from_file(menu)
# Can override default values on the command line
from parampool.menu.UI import set_values_from_command_line
menu = set_values_from_command_line(menu)

from django.shortcuts import render_to_response
from django.template import RequestContext
from compute_motion_and_forces_with_menu_menu_definition_list_models import MotionAndForcesWithMenu, MotionAndForcesWithMenuForm

def index(request):
    result = None

    form = MotionAndForcesWithMenuForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        for field in form:
            name = MotionAndForcesWithMenu._meta.get_field(field.name).verbose_name.strip()
            value = field.data
            menu.set_value(name, value)
        result = compute(menu)
        form = MotionAndForcesWithMenuForm(request.POST)

    return render_to_response(
        "compute_motion_and_forces_with_menu_menu_definition_list_index.html",
        {"form": form,
         "result": result,
        },
        context_instance=RequestContext(request))

def compute(menu):
    """
    Generic function for calling compute_function with values
    taken from the menu object.
    Return the output from the compute_function.
    """

    # compute_function must have only one positional argument
    # named menu
    import inspect
    arg_names = inspect.getargspec(compute_function).args
    if len(arg_names) == 1 and arg_names[0] == "menu":
        result = compute_function(menu)
    else:
        raise TypeError('%s(%s) can only have one argument named "menu"'
                        % (compute_function.__name__, ', '.join(arg_names)))
    return result

from parampool.menu.UI import write_menufile
write_menufile(menu, '.tmp_menu.dat')
