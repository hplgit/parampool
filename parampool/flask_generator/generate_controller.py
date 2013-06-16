import os
from distutils.util import strtobool

def generate_controller(compute_function, classname,
                        outfile, output_template, overwrite):

    if not overwrite and outfile is not None and os.path.isfile(outfile):
        if not strtobool(raw_input(
            "The file %s already exists. Overwrite? [Y/N]: " % outfile)):
            return None

    compute_function_name = compute_function.__name__
    compute_function_file = compute_function.__module__
    code = '''\
import os
from flask import Flask, render_template, request, session
from werkzeug import secure_filename
from %(compute_function_file)s import %(compute_function_name)s as compute_function
from models import %(classname)s

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['txt', 'npy'])

# Relative path of folder for uploaded files
UPLOAD_DIR = 'uploads/'

# Application object
app = Flask(__name__)

# Configure for uploading of files
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = 'MySecretKey'

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = %(classname)s(request.form)
    if request.method == 'POST' and form.validate():

        # Save uploaded file if it exists and is valid
        if request.files:
            file = request.files[form.filename.name]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Compute result
        result = compute(form)

    else:
        result = None

    return render_template("%(output_template)s", form=form, result=result)

def compute(form):
    """
    Generic function for compute_function with arguments
    taken from a form object (wtforms.Form subclass).
    Return the output from the compute_function.
    """
    # Extract arguments to the compute function
    import inspect
    arg_names = inspect.getargspec(compute_function).args

    # Extract values from form
    form_values = [getattr(form, name) for name in arg_names
                   if hasattr(form, name)]
    form_data = [value.data for value in form_values]
''' % vars()

    # Insert helper code if positional
    # arguments because the user must then convert form_data
    # elements explicitly.
    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults  = inspect.getargspec(compute_function).defaults
    if not defaults or len(defaults) != len(arg_names):
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
    result = compute_function(*form_data)
    return result

if __name__ == '__main__':
    app.run(debug=True)
''' % vars()

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()
        print "Flask main application written to %s." % outfile
        print "Usage: python %s" % outfile

# No tests
