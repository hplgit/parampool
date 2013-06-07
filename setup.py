from distutils.core import setup
import parampool

setup(name='parampool',
      version=parampool.__version__,
      url='',
      author=parampool.__author__,
      description='',
      license='BSD',
      long_description=parampool.__doc__,
      platforms='any',
      #package_data={'name': ['parampool/*.dat'],},
      packages=['parampool', 'parampool.tree', 'parampool.menu',
                'parampool.generator'])

