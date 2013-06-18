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
          'parampool.generator.flask':
          os.path.join('parampool', 'generator', 'flask'),
          'parampool.generator.django':
          os.path.join('parampool', 'generator', 'django')},
      package_data={'parampool.generator.flask':  ['static.tar.gz'],
                    'parampool.generator.django': ['static.tar.gz']},
      packages=['parampool',
                'parampool.tree',
                'parampool.menu',
                'parampool.generator',
                'parampool.generator.flask',
                'parampool.generator.django',
                'parampool.html5',
                'parampool.html5.flask',
                'parampool.html5.django',
                'parampool.misc',
                ],)

