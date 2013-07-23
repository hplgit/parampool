import os
from distutils.util import strtobool

def generate_controller(compute_function, classname,
                        outfile, filename_template,
                        menu_function, overwrite,
                        filename_model):

    if not overwrite and outfile is not None and os.path.isfile(outfile):
        if not strtobool(raw_input(
            "The file %s already exists. Overwrite? [Y/N]: " % outfile)):
            return None

    compute_function_name = compute_function.__name__
    compute_function_file = compute_function.__module__

    if menu_function:
        menu_function_name = menu_function.__name__
        menu_function_file = menu_function.__module__
        menu = True
    else:
        menu = False

    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults  = inspect.getargspec(compute_function).defaults

    # Add code for file upload only if it is strictly needed
    file_upload = False

    if menu:
        # FIXME: This should be replaced by a good regex
        filetxt = ("widget='file'", 'widget="file"',
                   "widget = 'file'", 'widget = "file"')
        menutxt = open(menu_function_file + ".py", 'r').read()
        for txt in filetxt:
            if txt in menutxt:
                file_upload = True
                break
    else:
        for name in arg_names:
            if 'filename' in name:
                file_upload = True
                break

    model_module = filename_model.replace('.py', '')

    code = '''\
import os
from flask import Flask, render_template, request, session
from %(compute_function_file)s import %(compute_function_name)s as compute_function
from %(model_module)s import %(classname)s
''' % vars()

    if file_upload:
        code += '''\
from werkzeug import secure_filename
'''
    code += '''
# Application object
app = Flask(__name__)
''' % vars()

    if menu:
        code += '''
# Menu object
from %(menu_function_file)s import %(menu_function_name)s as menu_function
menu = menu_function()
''' % vars()

    if file_upload:
        code += '''
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
''' % vars()

    code += '''
# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    form = %(classname)s(request.form)
    if request.method == 'POST' and form.validate():
''' % vars()
    if file_upload:
        # Need to write custom validation for files
        code = code.replace(" and form.validate()", "")
        code += '''
        # Save uploaded file if it exists and is valid
        if request.files:'''
        if menu:
            code += '''
            for name, file in request.files.iteritems():
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    menu.set_value(name, filename)
                else:
                    raise TypeError("Illegal filename")
'''
        else:
            code += '''
            file = request.files[form.filename.name]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                session["filename"] = filename
            else:
                session["filename"] = None
        else:
            session["filename"] = None
'''

    if menu:
        code += '''
        # Send data to Menu object
        for field in form:
            name = field.description
            value = field.data
            data_item = menu.set_value(name, value)

        result = compute(menu)
'''
    else:
        code += '''
        result = compute(form)
'''
    code += '''\

    else:
        result = None

    return render_template("%(filename_template)s", form=form, result=result)

''' % vars()

    if menu:
        code += '''\
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
                        % (compute_function_name, ', '.join(arg_names)))
    return result
'''
    else:
        code += '''\
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
''' % vars()

        if not file_upload:
            code += '''
    form_data = [value.data for value in form_values]
'''
        else:
            code += '''
    import wtforms
    form_data = []
    for value in form_values:
        if not isinstance(value, wtforms.fields.simple.FileField):
            form_data.append(value.data)
        else:
            form_data.append(session["filename"])
'''

        # Insert helper code if positional
        # arguments because the user must then convert form_data
        # elements explicitly.
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
        else:
            # We have default values: do right conversions
            code += '''
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
'''
        code += '''
    # Run computations
    result = compute_function(*form_data)
    return result
'''
    code += '''
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
