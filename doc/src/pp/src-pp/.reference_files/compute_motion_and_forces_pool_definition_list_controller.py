import os
from flask import Flask, render_template, request, session
from compute import compute_motion_and_forces as compute_function
from compute_motion_and_forces_pool_definition_list_model import MotionAndForces

# Application object
app = Flask(__name__)

# Pool object
from compute import pool_definition_list as pool_function
pool = pool_function()

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = MotionAndForces(request.form)
    if request.method == 'POST' and form.validate():

        # Send data to Pool object
        for field in form:
            name = field.description
            value = field.data
            data_item = pool.set_value(name, value)

        result = compute(pool)

    else:
        result = None

    return render_template("compute_motion_and_forces_pool_definition_list_view.html", form=form, result=result)

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
                        % (compute_function_name, ', '.join(arg_names)))
    return result

if __name__ == '__main__':
    app.run(debug=True)
