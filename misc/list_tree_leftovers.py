from parampool.tree.list_tree import *

def tree2dict(tree):
    """
    Transform nested list tree to true nested dict:
    dict[menu][menu]...[item]
    """
    def leaf_dictptr(
        subtree_name, level, leaf, user_data):
        """Add leaf to the dict user_data."""
        # Make nested key look-up based on all names in subtree_name
        keys = ''.join(["['%s']" % name for name in subtree_name])
        statement = "user_data%s['%s'] = leaf" % (keys, leaf['name'])
        exec(statement)

    def subtree_start_dictptr(
        subtree_name, level, subtree, user_data):
        """Add a new empty dict in user_data for this subtree."""
        # Make nested key look-up based on all subtree names in subtree_name
        keys = ''.join(["['%s']" % name for name in subtree_name])
        if keys:
            statement = "user_data%s = {}" % keys
            exec(statement)  # new subtree level in the dict

    # More elegant versions avoiding exec

    def leaf_dictptr(
        subtree_name, level, leaf, user_data):
        """Add leaf to the dict user_data."""
        d = user_data
        for name in subtree_name:
            d = d[name]
        d[leaf['name']] = leaf

    def subtree_start_dictptr(
        subtree_name, level, subtree, user_data):
        """Add a new empty dict in user_data for this subtree."""
        # Make nested key look-up based on all subtree names in subtree_name
        d = user_data
        for name in subtree_name[:-1]:
            d = d[name]
        d[subtree_name[-1]] = {}  # new subtree

    dict_repr = {}
    traverse_list_tree(tree,
             callback_leaf=leaf_dictptr,
             callback_subtree_start=subtree_start_dictptr,
             user_data=dict_repr)

    return dict_repr

def make_command_line_arguments(tree):
    # Build command-line arguments
    def leaf_cml_arg(subtree_name, level, leaf, user_data):
        arg = '--' + '/'.join(subtree_name + [leaf['name']])
        arg = arg.replace(' ', '_')  # cannot have spaces
        user_data.append(arg)

    cml_args = []  # to be filled with valid command-line arguments
    traverse_list_tree(tree,
             callback_leaf=leaf_cml_arg,
             user_data=cml_args)
    return cml_args

def cml_arg_match(cml_arg, cml_args):
    """
    See of cml_arg is a unique short form of any of the valid
    arguments in cml_args.
    """
    cml_arg = cml_arg[2:]  # strip off -- prefix
    cml_args_short = [arg[-len(cml_arg):] for arg in cml_args]
    if cml_args_short.count(cml_arg) == 1:
        # return unique match
        index = cml_args_short.index(cml_arg)
        return cml_args[index]
    else:
        raise ValueError('non-unique command-line argument %s' % cml_arg)


# To set values it would be easier to operate the nested dict
# data structure. Should make a new traverse function for this.

def set_value(dict_tree, name, value):
    # Assume name is a tuple of subtree names and data item name
    d = dict_tree
    for n in name:  # nested look up
        d = d[n]
    leaf = d
    leaf['value'] = value
    # NOT TESTED!
    # Add code for unit conversion:
    # if 'unit' in leaf: check if value consists of 'number unit'
    # with a regex r'[Ee.0-9+-] *[A-Za-z0-9*/]'
    #
    # Allow multiple values to appear (best if that was some
    # MultipleValue object and not a list to distiguish it from
    # a plain list). Can use scitools.multipleloops to set up experiments!


def XML_dump(tree):
    """Write tree in XML format."""
    def leaf_xml(subtree_name, level, leaf, xml):
        indentation = '    '*level
        xml.append(
            '%s<dataitem %s/>\n' %
            (indentation, ', '.join(['%s="%s"' %
             (key, leaf[key]) for key in sorted(leaf)])))

    def subtree_start_xml(subtree_name, level, subtree, xml):
        indentation = '    '*level
        xml.append(
            '%s<subtree name="%s" level="%s">\n' % \
            (indentation, subtree_name[-1], level))

    def subtree_end_xml(subtree_name, level, subtree, xml):
        indentation = '    '*level
        xml.append('%s</subtree>\n' % indentation)

    xml = []  # lines of strings with XML data
    traverse_list_tree(tree,
             callback_leaf=leaf_xml,
             callback_subtree_start=subtree_start_xml,
             callback_subtree_end=subtree_end_xml,
             user_data=xml)
    return xml

# A GUI could be built using the same technique as the XML example
# Easy way in Tk: Tktreectrl, see http://tkinter.unpythonic.net/wiki/Widgets

# More to do:
#
# Make a function for setting values in the tree with unit conversion.
#
# Convert simple tree to a tree with objects: DataItem, MenuItem (subtree),
# and Menu. Provide Menu.traverse with the same capabilities of callbacks.
#
