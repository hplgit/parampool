import os
from compute import compute_average as compute_function

from flask import Flask, render_template, request, session
from compute_average_model import Average
from werkzeug import secure_filename

# Application object
app = Flask(__name__)

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['txt', 'dat', 'npy'])

# Relative path of folder for uploaded files
UPLOAD_DIR = 'uploads/'

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = 'MySecretKey'

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = Average(request.form)
    if request.method == 'POST':

        # Save uploaded file if it exists and is valid
        if request.files:
            file = request.files[form.filename.name]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                session["filename"] = filename
            else:
                session["filename"] = None
        else:
            session["filename"] = None

        result = compute(form)

    else:
        result = None

    return render_template("compute_average_view.html", form=form, result=result)


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

    import wtforms
    form_data = []
    for value in form_values:
        if not isinstance(value, wtforms.fields.simple.FileField):
            form_data.append(value.data)
        else:
            form_data.append(session["filename"])

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
            if isinstance(defaults[i], (str,bool,int,float)):
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

if __name__ == '__main__':
    app.run(debug=True)
