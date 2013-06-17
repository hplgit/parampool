import os
from parampool.misc.assert_utils import assert_equal_files

def test_generator_flask():
    failure = os.system('sh clean.sh')
    assert failure == False, 'could not run clean.sh'
    failure = os.system('python generate_flask.py')
    assert failure == False, 'could not run generate_flask.py'
    assert_equal_files('model.py', 'reference_model.py')
    assert_equal_files('controller.py', 'reference_controller.py')
    assert_equal_files(os.path.join('templates', 'view.html'),
                       'reference_view.html')
    os.system('sh clean.sh')  # clean up

