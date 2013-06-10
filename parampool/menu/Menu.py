"""
Representation of a menu tree.
class Menu wraps class Tree and makes that class more suitable
for menus by renaming methods and adding functionality.
"""
from SubTree import SubTree
from DataItem import DataItem
from Tree import *

class Menu(Tree):
    def __init__(self, root=None, root_name='main'):
        Tree.__init__(self, root, root_name)
        for level in self.level_name:
            self.level_name[level] = \
            self.level_name[level].replace('tree', 'menu')

    def data_item(self, **data_item_attributes):
        self.add_leaf(DataItem(**data_item_attributes))

    submenu = Tree.subtree

    def update(self):
        self.paths2data_items = hash_all_leaves(self)
        self.paths = list(self.paths2data_items.keys())

    def get(self, data_item_name):
        """
        Return DataItem object corresponding to `data_item_name`,
        which can be a uniqu valid abbreviation of the full name.
        """
        try:
            return get_leaf(data_item_name, self.paths2data_items)
        except ValueError:
            raise ValueError('%s is not a unique data item name '
                  'among\n%s' % (data_item_name,
                  ', '.join(self.paths2data_items.keys())))

    def set_value(self, data_item_name, value):
        """
        Set value of DataItem object corresponding to `data_item_name`,
        which can be a uniqu valid abbreviation of the full name.
        """
        data_item = self.get(data_item_name)
        data_item.set_value(value)



import nose.tools as nt

def make_test_menu_dummy():
    return test_Menu()

def make_test_menu_drag():
    import UI
    return UI.test_listtree2Menu()

def test_Menu():
    m = Menu()
    m.data_item(name='item1', default=1.0)
    nt.assert_equal(m.locator.name, 'main')
    nt.assert_equal(m.locator.tree[-1].name, 'item1')

    m.data_item(name='item2', default=2.0)
    m.subtree('sub1')
    nt.assert_equal(m.locator.name, 'sub1')

    m.data_item(name='item3', default=3)
    nt.assert_equal(m.locator.name, 'sub1')
    nt.assert_equal(m.locator.tree[-1].name, 'item3')

    m.subtree('../sub2')
    m.data_item(name='item4', default=4)
    nt.assert_equal(m.locator.name, 'sub2')
    nt.assert_equal(m.locator.tree[-1].name, 'item4')
    nt.assert_equal(str(m.locator), '[DataItem "item4"]')
    nt.assert_equal(m.locator.get_parent().name, 'main')

    m.subtree('sub3')
    m.data_item(name='item5', default=5)
    m.subtree('sub4')
    m.data_item(name='item6', default=6)
    m.data_item(name='item7', default=7)
    m.data_item(name='item8', default=8)
    m.data_item(name='item9', default=9)
    m.subtree('..')
    nt.assert_equal(m.locator.name, 'sub3')

    m.data_item(name='item10', default=10)
    m.subtree('sub4')
    m.subtree('../../sub5')
    m.data_item(name='item11', default=11)
    m.subtree('/sub2/sub3/sub4')
    m.data_item(name='item12', default=12)
    reference = """\
item1
item2
sub menu "sub1" (level=0)
    item3
sub menu "sub2" (level=0)
    item4
    subsub menu "sub3" (level=1)
        item5
        subsubsub menu "sub4" (level=2)
            item6
            item7
            item8
            item9
            item12
        item10
    subsub menu "sub5" (level=1)
        item11"""
    nt.assert_equal(str(m), reference,
                    msg=diff_strings(str(m), reference))
    return m

if __name__ == '__main__':
    test_Menu()
