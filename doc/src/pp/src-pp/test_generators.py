from parampool.generator.flask import generate as flask_generate
from parampool.generator.django import generate as django_generate
from parampool.utils import assert_equal_files
import shutil, os

test_dir = 'test'
reference_dir = '.reference_files'

def _flask_tester(func, menu_function=None):
    print '\n\n-------- Testing flask generator for', func.__name__, '\n'
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    os.mkdir(test_dir)
    shutil.copy('compute.py', test_dir)
    os.chdir(test_dir)
    menu_function_name = '_' + menu_function.__name__ if menu_function is not None else ''
    template = '%s%s_view.html' % (func.__name__, menu_function_name)
    controller = '%s%s_controller.py' % (func.__name__, menu_function_name)
    model = '%s%s_model.py' % (func.__name__, menu_function_name)
    flask_generate(func,
                   default_field='FloatField',
                   filename_template=template,
                   filename_controller=controller,
                   filename_model=model,
                   menu_function=menu_function)
    # Move all generated files to test_dir
    os.rename(os.path.join('templates', template), template)
    os.chdir(os.pardir)
    filenames = template, controller, model
    for filename in filenames:
        assert_equal_files(
            os.path.join(reference_dir, filename),
            os.path.join(test_dir, filename),
            os.path.join(reference_dir, filename),
            os.path.join(test_dir, filename),
            msg='failure in test ' + func.__name__)
    shutil.rmtree(test_dir)

def _django_tester(func, menu_function=None):
    print '\n\n-------- Testing django generator for', func.__name__, '\n'
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    os.mkdir(test_dir)
    shutil.copy('compute.py', test_dir)
    os.chdir(test_dir)
    menu_function_name = '_' + menu_function.__name__ if menu_function is not None else ''
    template = '%s%s_index.html' % (func.__name__, menu_function_name)
    views = '%s%s_views.py' % (func.__name__, menu_function_name)
    models = '%s%s_models.py' % (func.__name__, menu_function_name)
    django_generate(func,
                    default_field='FloatField',
                    filename_template=template,
                    filename_views=views,
                    filename_models=models,
                    menu_function=menu_function)
    # Move all generated files to test_dir
    appdir = os.path.join(func.__name__, 'app').replace('compute_', '')
    os.rename(os.path.join(appdir, 'templates', template), template)
    os.rename(os.path.join(appdir, models), models)
    os.rename(os.path.join(appdir, views), views)
    os.chdir(os.pardir)
    filenames = template, views, models
    for filename in filenames:
        generated = os.path.join(test_dir, filename)
        original = os.path.join(reference_dir, filename)
        print 'comparing', filename, '...'
        assert_equal_files(
            original,
            generated,
            original,
            generated,
            msg='failure in test ' + func.__name__)
        # Test login.html, old.html, reg.html if they exist...
    shutil.rmtree(test_dir)

def test_compute_drag_free_landing():
    from compute import compute_drag_free_landing as func
    _flask_tester(func)
    _django_tester(func)

def test_compute_drag_free_motion_plot():
    from compute import compute_drag_free_motion_plot as func
    _flask_tester(func)
    _django_tester(func)

def test_compute_motion_and_forces():
    from compute import compute_motion_and_forces as func
    _flask_tester(func)
    _django_tester(func)

def test_compute_average():
    from compute import compute_average as func
    _flask_tester(func)
    _django_tester(func)

def test_compute_motion_and_forces_with_menu():
    from compute import compute_motion_and_forces_with_menu as func, \
         menu_definition_list, menu_definition_api, \
         menu_definition_api_with_separate_submenus
    menu_function = menu_definition_list
    _flask_tester(func, menu_function)
    _django_tester(func, menu_function)

    menu_function = menu_definition_api
    _flask_tester(func, menu_function)
    _django_tester(func, menu_function)

    menu_function = menu_definition_api_with_separate_submenus
    _flask_tester(func, menu_function)
    _django_tester(func, menu_function)

    # Test setting menu values
    m = menu_function()
    m.set_value('Radius', '0.11*100 cm')
    v = m.get_value('Radius')
    assert v == 0.11, 'Wrong value %s, not 0.11' % v


if __name__ == '__main__':
    test_compute_drag_free_landing()
    test_compute_drag_free_motion_plot()
    test_compute_motion_and_forces()
    test_compute_average()
    test_compute_motion_and_forces_with_menu()
