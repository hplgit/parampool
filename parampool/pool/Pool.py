"""
Representation of a pool tree.
class ``Pool`` wraps class ``Tree`` and makes that class more suitable
for pools by renaming methods and adding functionality.
"""
from parampool.tree.SubTree import SubTree
from parampool.pool.DataItem import DataItem
from parampool.tree.Tree import Tree, hash_all_leaves, get_leaf
from parampool.PhysicalQuantities import PhysicalQuantity as PQ

class Pool(Tree):
    def __init__(self, root=None, root_name='main'):
        Tree.__init__(self, root, root_name)
        for level in self.level_name:
            self.level_name[level] = \
            self.level_name[level].replace('tree', 'pool')

    def add_data_item(self, **data_item_attributes):
        """
        Add a new ``DataItem`` object at the current location
        in the pool tree. The keyword arguments sets various
        attributes in the data item. At least ``name`` must
        be given.
        """
        self.add_leaf(DataItem(**data_item_attributes))

    subpool = Tree.subtree
    change_subpool = Tree.change_subtree

    def update(self):
        self.paths2data_items = hash_all_leaves(self)
        self.paths = list(self.paths2data_items.keys())

    def get(self, data_item_name):
        """
        Return ``DataItem`` object corresponding to `data_item_name`,
        which can be a unique valid abbreviation of the full name.
        """
        if not hasattr(self, 'paths2data_items'):
            raise ValueError('pool.get("%s") does not work because pool construction is not finalized with pool.update()' % data_item_name)
        try:
            return get_leaf(data_item_name, self.paths2data_items)
        except ValueError:
            raise ValueError('%s is not a unique data item name '
                  'among\n%s' % (data_item_name,
                  ', '.join(self.paths2data_items.keys())))

    def get_value(self, data_item_name, default=None):
        """
        Return value set in ``DataItem`` object with name `data_item_name`.
        If name is not found, an exception is raised if `default` is None,
        otherwise `default` is returned.
        """
        try:
            data_item = self.get(data_item_name)
            return data_item.get_value()
        except ValueError, e:
            if default is None:
                raise e
            else:
                return default

    def get_values(self, data_item_name, default=None):
        """
        Return all values set in ``DataItem`` object with name `data_item_name`.
        If name is not found, an exception is raised if `default` is None,
        otherwise `default` is returned.
        """
        try:
            data_item = self.get(data_item_name)
            return data_item.get_values()
        except ValueError, e:
            if default is None:
                raise e
            else:
                return default

    def set_value(self, data_item_name, value):
        """
        Set value of ``DataItem`` object corresponding to `data_item_name`,
        which can be a uniqu valid abbreviation of the full name.
        """
        data_item = self.get(data_item_name)
        data_item.set_value(value)
        return data_item  # for convenience

    def get_unit(self, data_item_name):
        """
        Return unit set in ``DataItem`` object with name `data_item_name`,
        if unit is registered, otherwise return None.
        """
        try:
            data_item = self.get(data_item_name)
            if 'unit' in data_item.data:
                return data_item.data['unit']
            else:
                return None
        except ValueError, e:
            raise NameError('Cannot find DataItem object with name "%s"' %
                            data_item_name)

    def get_value_unit(self, data_item_name, default=None):
        """
        Return PhysicalQuantity object with value and unit for
        the ``DataItem`` object with name `data_item_name`,
        if unit is not registered, an exception is raised.
        """
        try:
            value = self.get_value(data_item_name, default)
            unit = self.get_unit(data_item_name)
        except ValueError, e:
            raise NameError('Cannot find DataItem object with name "%s"' %
                            data_item_name)
        if unit is None:
            raise ValueError('Pool.get_value_unit: unit is not registered for "%s"' % data_item_name)
        return PQ('%g %s' % (value, unit))

import nose.tools as nt
from parampool.utils import assert_equal_text

def test_Pool():
    p = Pool()
    p.add_data_item(name='item1', default=1.0)
    nt.assert_equal(p.locator.name, 'main')
    nt.assert_equal(p.locator.tree[-1].name, 'item1')

    p.add_data_item(name='item2', default=2.0)
    p.subtree('sub1')
    nt.assert_equal(p.locator.name, 'sub1')

    p.add_data_item(name='item3', default=3)
    nt.assert_equal(p.locator.name, 'sub1')
    nt.assert_equal(p.locator.tree[-1].name, 'item3')

    p.subtree('../sub2')
    p.add_data_item(name='item4', default=4)
    nt.assert_equal(p.locator.name, 'sub2')
    nt.assert_equal(p.locator.tree[-1].name, 'item4')
    nt.assert_equal(str(p.locator), '[DataItem "item4"]')
    nt.assert_equal(p.locator.get_parent().name, 'main')

    p.subtree('sub3')
    p.add_data_item(name='item5', default=5)
    p.subtree('sub4')
    p.add_data_item(name='item6', default=6)
    p.add_data_item(name='item7', default=7)
    p.add_data_item(name='item8', default=8)
    p.add_data_item(name='item9', default=9)
    p.subtree('..')
    nt.assert_equal(p.locator.name, 'sub3')

    p.add_data_item(name='item10', default=10)
    p.subtree('sub4')
    p.subtree('../../sub5')
    p.add_data_item(name='item11', default=11)
    p.subtree('/sub2/sub3/sub4')
    p.add_data_item(name='item12', default=12)
    p.update()

    reference = """\
item1
item2
sub pool "sub1" (level=0)
    item3
sub pool "sub2" (level=0)
    item4
    subsub pool "sub3" (level=1)
        item5
        subsubsub pool "sub4" (level=2)
            item6
            item7
            item8
            item9
            item12
        item10
    subsub pool "sub5" (level=1)
        item11"""
    assert_equal_text(str(p), reference)

    # Test setting values
    return p

if __name__ == '__main__':
    test_Pool()
