import os, shutil, glob
from parampool.misc.assert_utils import assert_equal_files

def test_generator_flask():
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_flask.py')
    assert failure == False, 'could not run generate_flask.py'
    assert_equal_files('model.py', 'reference_flask_model.py')
    assert_equal_files('controller.py', 'reference_flask_controller.py')
    assert_equal_files(os.path.join('templates', 'view.html'),
                       'reference_flask_view.html')
    if os.path.isfile('clean.sh'):
        os.system('sh clean.sh')  # clean up
    else:
        for name in ['static', 'templates', 'uploads', 'model.py',
                     'controller.py',] + glob.glob('*.pyc'):
            if os.path.isfile(name):
                os.remove(name)
            elif os.path.isdir(name):
                shutil.rmtree(name)

def test_generator_django():
    if os.path.isdir('myfunc'):
        shutil.rmtree('myfunc')
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_django.py')
    assert failure == False, 'could not run generate_flask.py'
    assert_equal_files(os.path.join('myfunc', 'app', 'models.py'),
                       'reference_django_models.py')
    assert_equal_files(os.path.join('myfunc', 'app', 'views.py'),
                       'reference_django_views.py')
    assert_equal_files(os.path.join('myfunc', 'app', 'templates', 'index.html'),
                       'reference_django_index.html')
    shutil.rmtree('myfunc')
    shutil.rmtree('static')

