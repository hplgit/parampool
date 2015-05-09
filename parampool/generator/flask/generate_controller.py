import os
from distutils.util import strtobool

def generate_controller(compute_function, classname,
                        outfile, filename_template,
                        menu_function, overwrite,
                        filename_model, filename_forms=None,
                        filename_db_models=None, app_file=None,
                        login=False):

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

    if login:
        forms_module = filename_forms.replace('.py', '')
        db_models_module = filename_db_models.replace('.py', '')
        app_module = app_file.replace('.py', '')
    else:
        pass
    # Should be in the else-block, but that will lead
    # to an error in the comment on line 65.
    # See the TODO on line 67.
    model_module = filename_model.replace('.py', '')

    code = '''\
import os
from %(compute_function_file)s import %(compute_function_name)s as compute_function
''' % vars()
    if menu:
        code += '''
# Menu object (must be imported before %(model_module)s)
# AEJ: Why? With login we don't even have this file.
# TODO: Find out the reason for this order of imports.
from %(menu_function_file)s import %(menu_function_name)s as menu_function
menu = menu_function()

# Can define other default values in a file: --menufile name
from parampool.menu.UI import set_defaults_from_file
menu = set_defaults_from_file(menu)
# Can override default values on the command line
from parampool.menu.UI import set_values_from_command_line
menu = set_values_from_command_line(menu)
''' % vars()
    code += '''
from flask import Flask, render_template, request'''
    if file_upload:
        code += ', session'
    if login:
        code += ', redirect, url_for'
        code += '''
from %(forms_module)s import %(classname)sForm
from %(db_models_module)s import db, User, %(classname)s
from flask.ext.login import LoginManager, current_user, login_user, logout_user, login_required
from %(app_module)s import app
''' % vars()
    else:
        code += '''
from %(model_module)s import %(classname)s
''' % vars()

    if file_upload:
        code += '''\
from werkzeug import secure_filename
'''

    if login:
        if file_upload:
            code += '''
# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['txt', 'dat', 'npy'])

# Relative path of folder for uploaded files
UPLOAD_DIR = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
'''

        code += '''
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    user = current_user
    form = %(classname)sForm(request.form)
    if request.method == "POST":''' % vars()

        if file_upload:
            code += '''
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
        else:
            code += '''
        if form.validate():
'''
        if menu:
            code += '''
            # Send data to Menu object
            for field in form:
                if field.name not in request.files:
                    name = field.description
                    value = field.data
                    menu.set_value(name, value)

            result = compute(menu)
            if user.is_authenticated():
                object = %(classname)s()
                form.populate_obj(object)
                object.result = result
                object.user = user
''' % vars()
            if file_upload:
                code += '''\
                for name, file in request.files.iteritems():
                    setattr(object, name, menu.get(name).get_value())
'''
            code += '''\
                db.session.add(object)
                db.session.commit()

                # Send email notification
                if user.notify and user.email:
                    send_email(user)
'''
        else:
            if file_upload:
                code += '''
        result = compute(form)

        if user.is_authenticated():
            object = %(classname)s()
            form.populate_obj(object)
            object.result = result
            object.user = user
            object.filename = session["filename"]
            db.session.add(object)
            db.session.commit()

            # Send email notification
            if user.notify and user.email:
                send_email(user)
''' % vars()
            else:
                code += '''

            result = compute(form)
            if user.is_authenticated():
                object = %(classname)s()
                form.populate_obj(object)
                object.result = result
                object.user = user
                db.session.add(object)
                db.session.commit()

                # Send email notification
                if user.notify and user.email:
                    send_email(user)
''' % vars()
        code += '''
    else:
        if user.is_authenticated():
            if user.%(classname)s.count() > 0:
                instance = user.%(classname)s.order_by('-id').first()
                result = instance.result
                form = populate_form_from_instance(instance)

    return render_template("%(filename_template)s", form=form, result=result, user=user)
''' % vars()

    else:
        code += '''
# Application object
app = Flask(__name__)
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
            if field.name not in request.files:
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
        code += '''
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
'''
    else:
        code += '''
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
    if login:
        code += '''
def populate_form_from_instance(instance):
    """Repopulate form with previous values"""
    form = %(classname)sForm()
    for field in form:
        field.data = getattr(instance, field.name)
    return form

def send_email(user):
    from flask.ext.mail import Mail, Message
    mail = Mail(app)
    msg = Message("%(classname)s Computations Complete",
                  recipients=[user.email])
    msg.body = """\
A simulation has been completed by the Flask %(classname)s app. Please log in at

http://localhost:5000/login

to see the results.

---
This email has been automatically generated by the %(classname)s app created by
Parampool. If you don't want email notifications when a result is found, please
register a new user and leave the 'notify' field unchecked."""
    mail.send(msg)

@app.route('/reg', methods=['GET', 'POST'])
def create_login():
    from %(forms_module)s import register_form
    form = register_form(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        form.populate_obj(user)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    return render_template("reg.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from %(forms_module)s import login_form
    form = login_form(request.form)
    if request.method == 'POST' and form.validate():
        user = form.get_user()
        login_user(user)
        return redirect(url_for('index'))
    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/old')
@login_required
def old():
    data = []
    user = current_user
    if user.is_authenticated():
        instances = user.%(classname)s.order_by('-id').all()
        for instance in instances:
            form = populate_form_from_instance(instance)

            result = instance.result
            if instance.comments:
                result += "<h3>Comments</h3>" + instance.comments
            data.append({'form':form, 'result':result, 'id':instance.id})

    return render_template("old.html", data=data)

@app.route('/add_comment', methods=['GET', 'POST'])
@login_required
def add_comment():
    user = current_user
    if request.method == 'POST' and user.is_authenticated():
        instance = user.%(classname)s.order_by('-id').first()
        instance.comments = request.form.get("comments", None)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id):
    id = int(id)
    user = current_user
    if user.is_authenticated():
        if id == -1:
            instances = user.%(classname)s.delete()
        else:
            try:
                instance = user.%(classname)s.filter_by(id=id).first()
                db.session.delete(instance)
            except:
                pass

        db.session.commit()
    return redirect(url_for('old'))

if __name__ == '__main__':
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'sqlite.db')):
        db.create_all()
    app.run(debug=True)
''' % vars()
    else:
        code += '''
if __name__ == '__main__':
    app.run(debug=True)
''' % vars()

    if menu:
        code += """
    from parampool.menu.UI import write_menufile
    write_menufile(menu, '.tmp_menu.dat')
"""

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()
        print "Flask main application written to %s." % outfile
        print "Usage: python %s" % outfile

    if login:
        app = open(app_file, 'w')
        import base64
        password = base64.encodestring('DifficultPW!').strip()
        app.write("""\
import os
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.secret_key = os.urandom(24)

# Email settings
import base64
app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME = 'cbcwebsolvermail@gmail.com',
        MAIL_PASSWORD = base64.decodestring('%(password)s'),
        MAIL_DEFAULT_SENDER = 'Flask %(classname)s Email <cbcwebsolvermail@gmail.com>'
        )""" % vars())
        app.close()

# No tests
