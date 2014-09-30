from menu_data1 import menu_tree
import tree

tree.printer(menu_tree)
menu = tree.tree2dict(menu_tree)
import pprint;
pprint.pprint(menu)

cml_args = tree.make_command_line_arguments(menu_tree)
print cml_args

cml_arg = '--m'  # see if this uniquely matches any long argument (should!)
try:
    arg = tree.cml_arg_match(cml_arg, cml_args)
    print 'match:', arg
except ValueError, e:
    print e
