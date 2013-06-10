"""User interfaces for Menu."""
from Menu import Menu

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

    def set_values(self, args):
        """Examine the command line (args) and set values in the menu."""
        from tree.Tree import get_leaf
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
                data_item.set_value(args[i+1])


def interpret_value(value):
    """
    Given the string `value`, try to convert it to bool, int,
    float, or keep it as string.
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

def read_menufile(filename):
    """Load tree from file."""
    if isinstance(filename, basestring):
        f = open(filename, 'r')
        data = f.read()
        f.close()
    elif hasattr(filename, 'read'):
        data = filename.read()

    menu = Menu()
    for line_no, line in enumerate(data.splitlines()):
        print line_no, line
        print menu

        if line.startswith('submenu'):
            name = ' '.join(line.split()[1:])
            menu.submenu(name)
        elif line.startswith('end'):
            menu.submenu('..')
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
            elif '#' in rest:
                value, help = rest.split('#')
            else:
                value = rest

            data = {'name': name.strip()}
            if value:
                str2type, value = interpret_value(value)
                data['default'] = value
                data['str2type'] = str2type
            if unit:
                data['unit'] = unit
            if help:
                data['help'] = help
            menu.data_item(**data)
        else:
            # line contains just the name of a data item
            data = {'name': line.strip()}
            menu.data_item(**data)
    return menu


def write_menufile(menu):
    """Dump menu to file."""

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
    return '\n'.join(outlines)


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
    from tree.Tree import TreePath

    def make_data_item(
        menu_path, level, data_item, menu):
        menu.data_item(**data_item)

    def make_submenu(
        menu_path, level, submenu, menu):
        path = TreePath(menu_path).to_str()
        menu.submenu(path)

    import tree.list_tree
    menu = Menu()
    tree.list_tree.traverse_list_tree(
        menu_tree,
        callback_leaf=make_data_item,
        callback_subtree_start=make_submenu,
        user_data=menu)
    return menu

import nose.tools as nt
from tree.Tree import diff_strings, dump

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
    nt.assert_equal(str(m), reference,
                    msg=diff_strings(str(m), reference))
    return m

def test_read_menufile():
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
    m = read_menufile(StringIO.StringIO(file_content))
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
    nt.assert_equal(str(m), reference,
                    msg=diff_strings(str(m), reference))
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
    nt.assert_equal(write_menufile(m), reference,
                    msg=diff_strings(write_menufile(m), reference))

def test_CommandLineOptions():
    import Menu
    menu = Menu.make_test_menu_drag()
    clo = CommandLineOptions(menu)
    clargs = '--/main/U 1.2 --rho 2.6 --mu 5.5E-5 '\
             '--/main/body_properties/d 0.2 --C_D 0.7'.split()
    clo.set_values(clargs)
    print dump(menu)


if __name__ == '__main__':
    test_read_menufile()
    test_listtree2Menu()
    test_CommandLineOptions()
