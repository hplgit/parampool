"""
Functions for processing tree structures composed as
nested list of strings or dicts.

Example::

    tree = [
        'main', [
            dict(name='U', default=120, unit='km/h',
                 help='velocity of body', str2type=eval),
            'fluid properties', [
                dict(name='rho', default=1.2, unit='kg/m**3',
                     help='density'),
                dict(name='mu', default=2E-5, help='viscosity'),
                ],
            'body properties', [
                dict(name='m', default=0.43, unit='kg', help='mass'),
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

def traverse_list_tree(
    tree,
    callback_leaf=None,
    callback_subtree_start=None,
    callback_subtree_end=None,
    level=0,
    subtree_name=None,
    user_data=None):
    """
    Traverse a tree and call callback functions such that
    a user can extract data from the tree.
    The tree data structure is a list of strings, lists,
    and dicts. A string indicates a name of a subtree, and
    the next element in the list is then a list which is
    the subtree. The leaves in the tree are dicts.
    When traversing the tree list one either has a string
    and a following list with a subtree, or a dict.
    """
    # tree is list of dicts and subtree_name followed by new tree list
    i = 0
    while i < len(tree):
        item = tree[i]
        if isinstance(item, basestring):
            # Hit a subtree name, find name, type and recurse on the subtree
            if subtree_name is None:
                subtree_name = []  # stack of super trees
            subtree_name.append(tree[i])
            subtree = tree[i+1]
            if not isinstance(subtree, list):
                print 'wrong type %s, value %s' % (type(subtree), str(subtree))

            if callable(callback_subtree_start):
                callback_subtree_start(
                    subtree_name, level, subtree, user_data)

            traverse_list_tree(
                subtree,
                callback_leaf=callback_leaf,
                callback_subtree_start=callback_subtree_start,
                callback_subtree_end=callback_subtree_end,
                level=level+1,
                subtree_name=subtree_name,
                user_data=user_data)

            if callable(callback_subtree_end):
                callback_subtree_end(
                    subtree_name, level, subtree, user_data)

            del subtree_name[-1]  # remove this subtree before we proceed
            # We have already processed the subtree, i.e.,
            # treated the next item in this list
            i = i + 1
        elif isinstance(item, dict):
            # This is a data item
            if callable(callback_leaf):
                callback_leaf(subtree_name, level, item, user_data)
        else:
            print 'wrong type %s, value %s' % (type(item), str(item))
        i = i + 1  # proceed with next item

def printer(tree):
    """Print the parts of the tree."""

    def leaf_printer(
        subtree_name, level, leaf, user_data):
        indentation = '    '*level
        user_data[0] += '%s %s\n' % (indentation, leaf['name'])

    def subtree_start_printer(
        subtree_name, level, subtree, user_data):
        menu_type = subtree_name[level]
        indentation = '    '*level
        user_data[0] += '%s %s "%s" (level=%d)\n' % \
               (indentation, menu_type, subtree_name[-1], level)

    output = ''
    user_data = [output]
    traverse_list_tree(
        tree,
        callback_leaf=leaf_printer,
        callback_subtree_start=subtree_start_printer,
        user_data=user_data)
    return user_data[0]

def test_traverse():
    from math import pi
    tree = [
        'main', [
            dict(name='U', default=120, unit='km/h',
                 help='velocity of body', str2type=eval),
            'fluid properties', [
                dict(name='rho', default=1.2, unit='kg/m**3',
                     help='density'),
                dict(name='mu', default=2E-5, help='viscosity'),
                ],
            'body properties', [
                dict(name='m', default=0.43, unit='kg', help='mass'),
                dict(name='A', default=pi*0.11**2, unit='m**2',
                     help='cross section area'),
                dict(name='d', default=2*0.11, unit='m',
                     help='diameter'),
                dict(name='C_D', default=0.2, minmax=[0,1],
                     help='drag coefficient'),
                ],
            ],
        ]
    actual = printer(tree)
    reference = """\
 main "main" (level=0)
     U
     fluid properties "fluid properties" (level=1)
         rho
         mu
     body properties "body properties" (level=1)
         m
         A
         d
         C_D
"""
    assert actual == reference

if __name__ == '__main__':
    test_traverse()




