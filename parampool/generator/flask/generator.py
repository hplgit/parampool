import os, shutil

from generate_controller import generate_controller
from generate_template import generate_template

def generate(compute_function,
             menu_function=None,
             classname=None,
             default_field='TextField',
             filename_template='view.html',
             overwrite_template=False,
             filename_controller='controller.py',
             overwrite_controller=False,
             filename_model='model.py',
             overwrite_model=False,
             MathJax=False,
             enable_login=False):
    """
    Given a function `compute_function` that takes a series of
    arguments, generate a Flask web form where

     * the arguments can be given values,
     * the `compute_function` is called with the given arguments, and
     * the return values from `compute_function` are presented.

    There are two basic ways to extract information about the input
    arguments to `compute_function`. Either a `menu` of type `Menu`)
    is specified, or the code can inspect the names of the arguments
    of the `compute_function`.

    The `menu` object organizes a tree of input parameters, each with
    at least two attribues: a name and a default value. Other
    attribures, such as widget (form) type, valid range of values,
    help string, etc., can also be assigned.  The `menu` object is
    mapped to a web form and `compute_function` is called with keyword
    arguments, each argument consisting of the name of the parameter
    in the menu and the value read from the web form. The names of the
    arguments in `compute_function` and the names of the parameters in
    the `menu` object must correspond exactly.

    If no `menu` object is given, the names of the arguments in
    `compute_function` are extracted and used in the web form.
    In the case where all arguments are positional (no default values),
    the web form consists of text fields for each argument, unless
    `default_field` is set to something else, e.g., `FloatField`.
    Since `TextField` is default, the user **must** go into the
    generated `filename_forms` file, find ``# Convert data to right types``
    and apply a data conversion as outlined in the example. Any
    keyword argument in `compute_function` can be used to detect the
    argument type and assign a proper web form type. We therefore
    recommend to use keyword arguments only in `compute_function`.
    """
    if classname is None:
        # Construct classname from the name of compute_function.
        # Ideas: 1) strip off any compute_ prefix, 2) split wrt _
        # and construct CapWords, otherwise just capitalize.
        if compute_function.__name__.startswith('compute_'):
            _compute_function_name = compute_function.__name__[8:]
        else:
            _compute_function_name = compute_function.__name__
        classname = ''.join([s.capitalize()
                             for s in _compute_function_name.split('_')])

    if menu_function:
        menu = menu_function()
    else:
        menu = None

    # Copy static files
    import os, shutil, tarfile
    if menu is not None:
        shutil.copy(os.path.join(os.path.dirname(__file__), 'static.tar.gz'),
                    os.curdir)
        archive = tarfile.open('static.tar.gz')
        archive.extractall()
        os.remove('static.tar.gz')
    else:
        if not os.path.isdir('static'):
            os.mkdir('static')

    # AEJ: I vaguely remember we concluded on these filenames
    # in the filename convention discussion. Now, I think it
    # would make more sense just to drop the name model.py,
    # call it forms.py (because that's what it really is, forms)
    # and write something about why we use the convention.
    #
    # Could have these also as args to generate(), but it may
    # cause confusion due to the model.py vs forms.py and
    # db_models.py problem.
    if enable_login:
        filename_forms = "forms.py"
        filename_db_models = "db_models.py"
        app_file = "app.py"

    generate_template(compute_function, classname, filename_template,
                      menu, overwrite_template, MathJax, login=enable_login)

    if enable_login:
        from generate_forms_and_models import generate_forms_and_models
        generate_forms_and_models(compute_function, classname,
                                  default_field, menu,
                                  filename_forms,
                                  filename_db_models,
                                  app_file)
        generate_controller(compute_function, classname, filename_controller,
                            filename_template, menu_function,
                            overwrite_controller, filename_model,
                            filename_forms, filename_db_models,
                            app_file, enable_login)
    else:
        from generate_model import generate_model
        generate_model(compute_function, classname, filename_model,
                       default_field, menu, overwrite_model)
        generate_controller(compute_function, classname, filename_controller,
                            filename_template, menu_function,
                            overwrite_controller, filename_model)

    # Generate clean-up script
    f = open('clean.sh', 'w')
    f.write("""\
#!/bin/sh
# Clean up files that can be regenerated
rm -rf uploads/ templates/ static/ %(filename_controller)s""" % vars())
    if enable_login:
        f.write(""" \
%(filename_forms)s %(filename_db_models)s %(app_file)s sqlite.db""" % vars())
    else:
        f.write(" %(filename_model)s" % vars())
    f.write(" *.pyc *~ clean.sh")
    f.close()
