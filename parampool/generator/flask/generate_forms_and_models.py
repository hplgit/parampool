from generate_model import generate_model

def generate_forms_and_models(compute_function,
                              classname,
                              default_field,
                              pool,
                              filename_forms,
                              filename_db_models,
                              app_file):

    form_text = generate_model(compute_function, classname, outfile=None,
                               default_field=default_field, pool=pool)

    app_module = app_file.replace('.py', '')

    import inspect
    arg_names = inspect.getargspec(compute_function).args
    defaults = inspect.getargspec(compute_function).defaults
    longest_name = max(len(name) for name in arg_names)

    db_code = '''\
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from %(app_module)s import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    pwhash = db.Column(db.String())
    email = db.Column(db.String(120), nullable=True)
    notify = db.Column(db.Boolean())

    def __repr__(self):
        return '<User %%r>' %% (self.username)

    def check_password(self, pw):
        return check_password_hash(self.pwhash, pw)

    def set_password(self, pw):
        self.pwhash = generate_password_hash(pw)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

class %(classname)s(db.Model):
    id = db.Column(db.Integer, primary_key=True)

''' % vars()

    if not pool:
        if defaults:
            defaults = ["none"]*(len(arg_names)-len(defaults)) + list(defaults)
        else:
            defaults = ["none"]*len(arg_names)

        db_mapping = {type(1): 'Integer',
                      type(1.0): 'Float',
                      type(True): 'Boolean()'}

        for name, default in zip(arg_names, defaults):
            db_type = db_mapping.get(type(default), 'String()')
            db_code += '''\
    %%(name)-%ds = db.Column(db.%%(db_type)s)
''' % longest_name % vars()

    else:
        class CodeData():
            pass

        def leaf_func(tree_path, level, item, user_data):
            name = '_'.join(item.name.split())
            widget = item.data.get("widget")
            if 'integer' in widget:
                user_data.code += '''\
    %%(name)-%ds = db.Column(db.Integer)
''' % user_data.longest_name % vars()
            elif 'float' in widget:
                user_data.code += '''\
    %%(name)-%ds = db.Column(db.Float)
''' % user_data.longest_name % vars()
            elif widget == 'checkbox':
                user_data.code += '''\
    %%(name)-%ds = db.Column(db.Boolean())
''' % user_data.longest_name % vars()
            else:
                user_data.code += '''\
    %%(name)-%ds = db.Column(db.String())
''' % user_data.longest_name % vars()

        codedata = CodeData()
        codedata.code = db_code
        codedata.longest_name = longest_name

        pool.traverse(callback_leaf=leaf_func,
                      user_data=codedata,
                      verbose=False)

        db_code = codedata.code


    db_code += '''
    result   = db.Column(db.String())
    comments = db.Column(db.String(), nullable=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'))
    user     = db.relationship('User',
                backref=db.backref('%(classname)s', lazy='dynamic'))''' % vars()

    db = open(filename_db_models, 'w')
    db.write(db_code)
    db.close()

    form_data = form_text.replace("%(classname)s(wtf.Form)" % vars(),
                                  "%(classname)sForm(wtf.Form)" % vars())

    db_models_module = filename_db_models.replace('.py', '')

    if not pool:
        html5import = 'import flask.ext.wtf.html5 as html5'
    else:
        html5import = ''

    form = open(filename_forms, 'w')
    form.write(form_data + '''
from %(db_models_module)s import db, User
%(html5import)s

# Standard Forms
class register_form(wtf.Form):
    username = wtf.TextField('Username', [wtf.validators.Required()])
    password = wtf.PasswordField('Password', [wtf.validators.Required(),
                                              wtf.validators.EqualTo('confirm',
                                                message='Passwords must match')])
    confirm  = wtf.PasswordField('Confirm Password', [wtf.validators.Required()])
    email    = html5.EmailField('Email')
    notify   = wtf.BooleanField('Email notifications')

    def validate(self):
        if not wtf.Form.validate(self):
            return False

        if self.notify.data and not self.email.data:
            self.notify.errors.append('\
Cannot send notifications without a valid email address')
            return False

        if db.session.query(User).filter_by(username=self.username.data).count() > 0:
            self.username.errors.append('User already exists')
            return False

        return True

class login_form(wtf.Form):
    username = wtf.TextField('Username', [wtf.validators.Required()])
    password = wtf.PasswordField('Password', [wtf.validators.Required()])

    def validate(self):
        if not wtf.Form.validate(self):
            return False

        user = self.get_user()

        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        return True

    def get_user(self):
        return db.session.query(User).filter_by(username=self.username.data).first()''' % vars())
    form.close()
