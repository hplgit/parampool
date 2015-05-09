import os
from compute import compute_motion_and_forces_with_menu as compute_function

# Menu object (must be imported before compute_motion_and_forces_with_menu_menu_definition_api_with_separate_submenus_model)
# AEJ: Why? With login we don't even have this file.
# TODO: Find out the reason for this order of imports.
from compute import menu_definition_api_with_separate_submenus as menu_function
menu = menu_function()

# Can define other default values in a file: --menufile name
from parampool.menu.UI import set_defaults_from_file
menu = set_defaults_from_file(menu)
# Can override default values on the command line
from parampool.menu.UI import set_values_from_command_line
menu = set_values_from_command_line(menu)

from flask import Flask, render_template, request
from compute_motion_and_forces_with_menu_menu_definition_api_with_separate_submenus_model import MotionAndForcesWithMenu

# Application object
app = Flask(__name__)

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = MotionAndForcesWithMenu(request.form)
    if request.method == 'POST' and form.validate():

        # Send data to Menu object
        for field in form:
            if field.name not in request.files:
                name = field.description
                value = field.data
                data_item = menu.set_value(name, value)

        result = compute(menu)

    else:
        result = None

    return render_template("compute_motion_and_forces_with_menu_menu_definition_api_with_separate_submenus_view.html", form=form, result=result)


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

if __name__ == '__main__':
    app.run(debug=True)

    from parampool.menu.UI import write_menufile
    write_menufile(menu, '.tmp_menu.dat')
