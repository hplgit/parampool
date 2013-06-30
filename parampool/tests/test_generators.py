import os, shutil, glob
from parampool.utils import assert_equal_files

# Test function with positional arguments and one keyword argument

def test_generator_flask1():
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_flask1.py')
    assert failure == False, 'could not run generate_flask1.py'
    assert_equal_files('model.py', 'reference_flask1_model.py')
    assert_equal_files('controller.py', 'reference_flask1_controller.py')
    assert_equal_files(os.path.join('templates', 'view.html'),
                       'reference_flask1_view.html')
    if os.path.isfile('clean.sh'):
        os.system('sh clean.sh')  # clean up
    else:
        for name in ['static', 'templates', 'uploads', 'model.py',
                     'controller.py',] + glob.glob('*.pyc'):
            if os.path.isfile(name):
                os.remove(name)
            elif os.path.isdir(name):
                shutil.rmtree(name)

def test_generator_django1():
    if os.path.isdir('mysimplefunc'):
        shutil.rmtree('mysimplefunc')
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_django1.py')
    assert failure == False, 'could not run generate_django1.py'
    assert_equal_files(os.path.join('mysimplefunc', 'app', 'models.py'),
                       'reference_django1_models.py')
    assert_equal_files(os.path.join('mysimplefunc', 'app', 'views.py'),
                       'reference_django1_views.py')
    assert_equal_files(os.path.join('mysimplefunc', 'app', 'templates', 'index.html'),
                       'reference_django1_index.html')
    shutil.rmtree('mysimplefunc')
    shutil.rmtree('static')

# Test function with keyword arguments only

def test_generator_flask2():
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_flask2.py')
    assert failure == False, 'could not run generate_flask2.py'
    assert_equal_files('model.py', 'reference_flask2_model.py')
    assert_equal_files('controller.py', 'reference_flask2_controller.py')
    assert_equal_files(os.path.join('templates', 'view.html'),
                       'reference_flask2_view.html')
    if os.path.isfile('clean.sh'):
        os.system('sh clean.sh')  # clean up
    else:
        for name in ['static', 'templates', 'uploads', 'model.py',
                     'controller.py',] + glob.glob('*.pyc'):
            if os.path.isfile(name):
                os.remove(name)
            elif os.path.isdir(name):
                shutil.rmtree(name)

def test_generator_django2():
    if os.path.isdir('myfunc'):
        shutil.rmtree('myfunc')
    if os.path.isfile('clean.sh'):
        failure = os.system('sh clean.sh')
        assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_django2.py')
    assert failure == False, 'could not run generate_django2.py'
    assert_equal_files(os.path.join('myfunc', 'app', 'models.py'),
                       'reference_django2_models.py')
    assert_equal_files(os.path.join('myfunc', 'app', 'views.py'),
                       'reference_django2_views.py')
    assert_equal_files(os.path.join('myfunc', 'app', 'templates', 'index.html'),
                       'reference_django2_index.html')
    shutil.rmtree('myfunc')
    shutil.rmtree('static')

