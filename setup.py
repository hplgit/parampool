from distutils.core import setup
import parampool, os

setup(name='parampool',
      version=parampool.__version__,
      url='https://github.com/hplgit/parampool',
      author=parampool.__author__,
      description='',
      license='BSD',
      long_description=parampool.__doc__,
      platforms='any',
      package_dir={
          'parampool.flask_generator': os.path.join('parampool', 'flask_generator'),
          'parampool.django_generator': os.path.join('parampool', 'django_generator')},
      package_data={'parampool.flask_generator': ['static.tar.gz'],
                    'parampool.django_generator': ['static.tar.gz']},
      packages=['parampool',
                'parampool.tree',
                'parampool.menu',
                'parampool.flask_generator',
                'parampool.django_generator',
                'parampool.misc',
                ],)

