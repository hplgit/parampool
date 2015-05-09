"""User interfaces for Menu."""
from parampool.menu.Menu import Menu
from parampool.tree.Tree import TreePath
import sys, os, re

class CommandLineOptions:
    def __init__(self, menu):
        self.menu = menu
        self.update()

    def update(self):
        """Update the names of all command-line options."""
        self.menu.update()
        # Make a version of self.menu.paths2data_items where
        # the paths have underscores for blanks (need to
        # search in this for short versions of options).
        self.options2data_items = {
            path.replace(' ', '_'): self.menu.paths2data_items[path]
            for path in self.menu.paths2data_items}

    def set_values(self, args=sys.argv[1:], set_default=False):
        """
        Examine the command line (args) and set values in the menu.
        if `set_default`, the default value (and not the value) is set.
        """
        from parampool.tree.Tree import get_leaf
        for i, arg in enumerate(args):
            if arg.startswith('--'):
                arg = arg[2:]  # strip off leading --
                try:
                    data_item = get_leaf(arg, self.options2data_items)
                except ValueError:
                    raise ValueError('%s is not a unique data item name '
                          'among\n%s' % ('--' + arg,
                          ', '.join(['--' + opt
                                     for opt in
                                     self.options2data_items])))
                if i+1 >= len(args):
                    raise ValueError('no value for command-line option %s'
                                     % arg)
                value = args[i+1]
                if set_default:
                    data_item.data['default'] = value
                else:
                    data_item.set_value(value)


# Simplified function-based API

def set_defaults_from_command_line(menu):
    clo = CommandLineOptions(menu)
    clo.set_values(set_default=True, args=sys.argv)
    return menu

def set_values_from_command_line(menu):
    clo = CommandLineOptions(menu)
    clo.set_values(set_default=False, args=sys.argv)
    return menu

def set_defaults_from_file(menu, command_line_option='--menufile'):
    """Set default values in menu based on a file."""
    if command_line_option not in sys.argv:
        return menu
    else:
        i = sys.argv.index(command_line_option)
        if i+1 >= len(sys.argv):
            raise ValueError('missing value for command-line option %s'
                             % command_line_option)
        filename = sys.argv[i+1]
        del sys.argv[i]
        del sys.argv[i]

        if os.path.isfile(filename):
            return read_menufile(filename, menu, task='set defaults')
        else:
            raise IOError('file %s not found' % filename)

def set_defaults_in_model_file(model_filename, menu):
    """Change default values in a model file."""
    if os.path.isfile(model_filename):
        f = open(model_filename, 'r')
        text = f.read()
        f.close()
    else:
        raise IOError('filename %s does not exist' % model_filename)
    if 'wtf.Form' in text:
        # Flask model.py file
        pattern = r'class (.+)\(wtf.Form\):'
        m = re.search(pattern, text)
        if m:
            classname = m.group(1)
            from parampool.generator.flask.generate_model import generate_model_menu
            generate_model_menu(classname, model_filename, menu)
    elif 'models.Model' in text:
        # Django model.py file
        pattern = r'class (.+)\(models.Model\):'
        m = re.search(pattern, text)
        if m:
            classname = m.group(1)
            from parampool.generator.django.generate_models import generate_models_menu
            generate_models_menu(classname, model_filename, menu)


def _interpret_value(value):
    """
    Given the string `value`, try to convert it to bool, int,
    float, or keep it as string. Used to guess right str2type
    when initializing a menu from file.
    """
    # Do from math import * to local namespace
    # since DataItem has all math functions available
    # to eval
    import math
    from_math_import = 'from math import ' + \
       ', '.join([name for name in dir(math)
                  if not name.startswith('__')])
    exec(from_math_import)

    str2type = None
    try:
        value = int(value)
        str2type = int
        return str2type, str2type(value)
    except:
        pass
    try:
        value = float(value)
        str2type = float
        return str2type, str2type(value)
    except:
        pass
    from DataItem import str2bool
    try:
        value = str2bool(value)
        str2type = str2bool
        return str2type, str2type(value)
    except:
        pass
    try:
        value = eval(value, locals())
        str2type = eval
        return str2type, str2type(value)
    except:
        # Giving up - let it be a string
        str2type = str
        return str2type, str2type(value)

def load_from_file(filename):
    """
    Create a new Menu object from a file definition. A typical
    definition of a data item is::

      name1 = value ! unit # help widget=...

    Example::

      submenu Main menu
          rho = 1.2  ! kg/m**3  # Density. widget=float
          submenu Numerical parameters
              dt = 0.1 ! s # Time step (None: automatically set, otherwise float value). widget=textline
          end
      end
    """
    menu = Menu()
    return read_menufile(filename, menu, task='create')

def read_menufile(filename, menu, task='create'):
    """Read menu file and initialize a menu or set default values."""
    if isinstance(filename, basestring):
        f = open(filename, 'r')
        data = f.read()
        f.close()
    elif hasattr(filename, 'read'):
        data = filename.read()

    levels = []
    for line_no, line in enumerate(data.splitlines()):
        #print line_no, line
        #print menu

        if line.startswith('submenu'):
            name = ' '.join(line.split()[1:])
            menu.submenu(name)
            levels.append(name)
        elif line.startswith('end'):
            menu.submenu('..')
            levels.pop()
        elif line.strip() == '':
            continue
        elif '=' in line:
            for char in '=', '!', '#':
                if line.count(char) > 1:
                    raise ValueError(
                    'wrong syntax in %s, line %d: more than '
                    'one "%s"\n%s' %
                    (filename, line_no+1, char, line))

            value = unit = help = None
            name, rest = line.split('=')
            if '!' in rest:
                value, rest = rest.split('!')
                if '#' in rest:
                    unit, help = rest.split('#')
                else:
                    unit = rest
            elif '#' in rest:
                value, help = rest.split('#')
            else:
                value = rest

            data = {'name': name.strip()}
            if task == 'create':
                if value:
                    str2type, value = _interpret_value(value)
                    data['default'] = value
                    data['str2type'] = str2type

                if unit:
                    data['unit'] = unit
                if help:
                    if 'widget=' in help:
                        help, widget = help.split('widget=')
                        help = help.strip()
                    data['help'] = help
                menu.add_data_item(**data)
            elif task == 'set defaults':
                data_item = menu.get(TreePath(levels + [data['name']]).to_str())
                if unit:
                    data_item.set_value('%s %s' % (value, unit))
                else:
                    data_item.set_value(value)
                value = data_item.get_value()
                data_item.data['default'] = value # without unit
        else:
            # line contains just the name of a data item
            data = {'name': line.strip()}
            if task == 'create':
                menu.add_data_item(**data)
            else:
                raise SyntaxError('Wrong syntax in menu file: no value\n%s' %
                                  line)
    return menu

def write_menufile(menu, filename=None):
    """
    Return menu as a string which can be dumped to file
    if filename is None, otherwise write the string to file.
    """

    def data_item_output(menu_path, level, data_item, outlines):
        indentation = '    '*level
        s = data_item.name
        if data_item.get_value() is not None:
            s += ' = ' + ' & '.join(
                ['%s' % v for v in data_item.get_values()])
        try:
            unit = data_item.get('unit')
            s += '   ! ' + unit
        except ValueError:
            pass
        try:
            help = data_item.get('help')
            s += '   # ' + help
            has_help = True
        except ValueError:
            has_help = False
        try:
            widget = data_item.get('widget')
            if not has_help:
                s += '   #'
            s += ' widget=' + widget
        except ValueError:
            pass
        outlines.append('%s%s' % (indentation, s))

    def submenu_start_output(menu_path, level, submenu, outlines):
        indentation = '    '*level
        outlines.append('%ssubmenu %s' % (indentation, menu_path[-1]))

    def submenu_end_output(menu_path, level, submenu, outlines):
        indentation = '    '*level
        outlines.append('%send\n' % indentation)

    outlines = []   # list of strings (to be printed)
    menu.traverse(
        callback_leaf=data_item_output,
        callback_subtree_start=submenu_start_output,
        callback_subtree_end=submenu_end_output,
        user_data=outlines)
    text = '\n'.join(outlines)
    if filename is not None:
        f = open(filename, 'w')
        f.write(text)
        f.close()
    return text

def set_data_item_attribute(menu, attribute_name, value):
    """Set an attribute for all data items in the menu."""
    attr = {attribute_name: value}
    menu.traverse(
        callback_leaf=lambda menu_path, level, data_item, attr: \
                      data_item.data.update(attr),
        user_data=attr)
    return menu


def listtree2Menu(menu_tree):
    """
    Transform menu_tree, a nested list of strings and dicts,
    to Menu representation.

    Example::

    >>> menu_tree = [
            'main', [
                dict(name='print intermediate results', default=False),
                dict(name='U', default=120, unit='km/h',
                     help='velocity of body', str2type=eval),
                'fluid properties', [
                    dict(name='rho', default=1.2, unit='kg/m**3',
                         help='density'),
                    dict(name='mu', default=2E-5, help='viscosity'),
                    ],
                'body properties', [
                    dict(name='m', default=0.43, unit='kg', help='mass'),
                    dict(name='V', default=pi*0.11**3, help='volume'),
                    dict(name='A', default=pi*0.11**2, unit='m**2',
                         help='cross section area'),
                    dict(name='d', default=2*0.11, unit='m',
                         help='diameter'),
                    dict(name='C_D', default=0.2, minmax=[0,1],
                         help='drag coefficient'),
                    ],
                ],
            ]

    """

    def make_data_item(
        menu_path, level, data_item, menu):
        menu.add_data_item(**data_item)

    def make_submenu(
        menu_path, level, submenu, menu):
        path = TreePath(menu_path).to_str()
        menu.submenu(path)

    from parampool.tree import list_tree
    menu = Menu()
    list_tree.traverse_list_tree(
        menu_tree,
        callback_leaf=make_data_item,
        callback_subtree_start=make_submenu,
        user_data=menu)
    menu.update()
    return menu

import nose.tools as nt
from parampool.tree.Tree import dump
from parampool.utils import assert_equal_text

def test_listtree2Menu():
    from math import pi
    tree = [
        'main', [
            dict(name='print intermediate results', default=False),
            dict(name='U', default=120, unit='km/h',
                 help='velocity of body', str2type=eval),
            'fluid properties', [
                dict(name='rho', default=1.2, unit='kg/m**3',
                     help='density'),
                dict(name='mu', default=2E-5, help='viscosity'),
                ],
            'body properties', [
                dict(name='m', default=0.43, unit='kg', help='mass'),
                dict(name='V', default=pi*0.11**3, help='volume'),
                dict(name='A', default=pi*0.11**2, unit='m**2',
                     help='cross section area'),
                dict(name='d', default=2*0.11, unit='m',
                     help='diameter'),
                dict(name='C_D', default=0.2, minmax=[0,1],
                     help='drag coefficient'),
                ],
            ],
        ]
    m = listtree2Menu(tree)
    reference = """\
sub menu "main" (level=0)
    print intermediate results
    U
    subsub menu "fluid properties" (level=1)
        rho
        mu
    subsub menu "body properties" (level=1)
        m
        V
        A
        d
        C_D"""
    assert_equal_text(str(m), reference)
    return m

def test_load_menu_from_file():
    import StringIO
    file_content = """
submenu main
print intermediate results
U = 1.0      ! m/s  # velocity

submenu fluid properties
rho = 1.2    ! kg/m**3  # density
mu = 5E.5
end

submenu body properties
m = 3  ! kg  # mass
V = 4  ! m/s
A
d
C_D
end
"""
    m = load_menu_from_file(StringIO.StringIO(file_content))
    print m
    reference = """\
sub menu "main" (level=0)
    print intermediate results
    U
    subsub menu "fluid properties" (level=1)
        rho
        mu
    subsub menu "body properties" (level=1)
        m
        V
        A
        d
        C_D"""
    assert_equal_text(str(m), reference)

    reference = """\
submenu main
    print intermediate results
    U = 1.0   !  m/s     #  velocity
    submenu fluid properties
        rho = 1.2   !  kg/m**3     #  density
        mu =  5E.5
    end

    submenu body properties
        m = 3   !  kg     #  mass
        V = 4
        A
        d
        C_D
    end

end
"""
    assert_equal_text(write_menufile(m), reference)

def test_CommandLineOptions():
    import parampool.menu.Menu as Menu
    menu = Menu.make_test_menu_drag()
    clo = CommandLineOptions(menu)
    clargs = '--/main/U 1.2 --rho 2.6 --mu 5.5E-5 '\
             '--/main/body_properties/d 0.2 --C_D 0.7'.split()
    clo.set_values(clargs)
    print dump(menu)


if __name__ == '__main__':
    test_load_menu_from_file()
    test_listtree2Menu()
    test_CommandLineOptions()
