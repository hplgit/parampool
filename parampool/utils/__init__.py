def legal_variable_name(name):
    """
    Make a variable name from the string name.
    Replace space by underscore and remove all illegal
    characters in a Python variable name.
    """
    var_name = name.replace(' ', '_').replace('/', '__')
    for char in r'''[]{}\^%$#@!+-<>?|'"=~`,.;:''':
        if char in var_name:
            var_name = var_name.replace(char, '')
    for char in var_name:
        if ord(char) > 127:  # remove non-ascii characters
            var_name = var_name.replace(char, '')
    return var_name


def save_png_to_str(plt, plotwidth=400):
    """
    Given a matplotlib.pyplot object plt, the current figure
    is saved to a PNG string which is embedded in an HTML
    image tag and returned.
    """
    from StringIO import StringIO
    figfile = StringIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = figfile.buf  # extract string
    import base64
    figdata_png = base64.b64encode(figdata_png)
    html_text = '<img src="data:image/png;base64,%(figdata_png)s" width="%(plotwidth)s">' % vars()
    return html_text

def dolfinxml2pool(xmlfile, pool=None):
    """Return a Pool tree from an XML file with DOLFIN parameters."""
    if pool is None:
        from parampool.pool.Pool import Pool
        pool = Pool()
        pool.subpool('Main menu')
    # else: add menus wherever we are in a pool tree
    import xml.etree.ElementTree as ET
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    def iterate(element):
        if element.tag == 'parameters':
            # New subpool of parameters
            pool.subpool(element.attrib['name'])
        elif element.tag == 'parameter':
            # Add data item
            value = element.attrib['value']
            if value == '':
                value = 'emptystring'  # just a magic code, the value gets transformed back to '' in set_dolfin_prm
            widget = 'textline'
            if element.attrib['type'] == 'double':
                str2type = float
                value = str2type(value)
                widget = 'float'
            elif element.attrib['type'] == 'int':
                str2type = int
                value = str2type(value)
                widget = 'integer'
            elif element.attrib['type'] == 'string':
                str2type = str
                value = str2type(value)
            elif element.attrib['type'] == 'bool':
                value = value.capitalize()  # True/False, not true/false
                # Short call to make sure bools are correctly handled
                pool.add_data_item(
                    name=element.attrib['key'],
                    default=value,
                    widget='checkbox')
            else:
                raise ValueError('Not impl element.attrib["type"]=%s' % element.attrib['type'])

            if element.attrib['type'] != 'bool':
                pool.add_data_item(
                    name=element.attrib['key'],
                    default=value,
                    str2type=str2type,
                    widget=widget)
        for child in element:
            iterate(child)
        if element.tag == 'parameters' and \
               pool.get_current_subpool().name != 'Main menu':
            pool.change_subpool('..')

    iterate(root)
    return pool

def set_dolfin_prm(path, level, item, dolfin_parameters):
    """
    Fill parameters dict in DOLFIN from a leaf in the Pool tree.
    Callback function for leaf in Pool tree in a FEniCS program:
    pool.traverse(set_dolfin_prm, user_data=dolfin.parameters).
    """
    submenu = path[2:]  # drop considering Main menu, dolfin
    value = item.get_value()
    changed_value = False
    if value in ('False', 'True'):
        if value != item.data['default']:
            changed_value = True
        value = value == 'True'
    if value == 'emptystring':  # code for empty string that GUIs don't like
        value = ''
        changed_value = False
    if (not isinstance(value, bool)) and value != item.data['default']:
        #print('parameter %s changed from %s to %s' % (item.name, item.data['default'], value))
        changed_value = True

    if not changed_value:
        return

    if len(submenu) == 0:
        try:
            dolfin_parameters[item.name] = value
        except KeyError:
            pass # user's parameter, not in DOLFIN's parameters
    elif len(submenu) == 1:
        try:
            dolfin_parameters[submenu[0]][item.name] = value
        except KeyError:
            pass # user's parameter, not in DOLFIN's parameters
    elif len(submenu) == 2:
        try:
            dolfin_parameters[submenu[0]][submenu[1]][item.name] = value
        except KeyError:
            pass # user's parameter, not in DOLFIN's parameters
    elif len(submenu) == 3:
        try:
            dolfin_parameters[submenu[0]][submenu[1]][submenu[2]][item.name] = value
        except KeyError:
            pass # user's parameter, not in DOLFIN's parameters
    else:
        raise ValueError('DOLFIN XML parameter trees are not so deeply nested')

def pydiff(text1, text2, text1_name='text1', text2_name='text2',
           prefix_diff_files='tmp_diff', n=3):
    """
    Use Python's ``difflib`` module to compute the difference
    between strings `text1` and `text2`.
    Produce text and html diff in files with `prefix_diff_files`
    as prefix. The `text1_name` and `text2_name` arguments can
    be used to label the two texts in the diff output files.
    No files are produced if the texts are equal.
    """
    if text1 == text2:
        return False

    # Else:
    import difflib, time, os

    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()

    diff_html = difflib.HtmlDiff().make_file(
        text1_lines, text2_lines, text1_name, text2_name,
        context=True, numlines=n)
    diff_plain = difflib.unified_diff(
        text1_lines, text2_lines, text1_name, text2_name, n=n)
    filename_plain = prefix_diff_files + '.txt'
    filename_html  = prefix_diff_files + '.html'

    f = open(filename_plain, 'w')
    # Need to add newlines despite doc saying that trailing newlines are
    # inserted...
    diff_plain = [line + '\n' for line in diff_plain]
    f.writelines(diff_plain)
    f.close()

    f = open(filename_html, 'w')
    f.writelines(diff_html)
    f.close()
    return True


def assert_equal_text(text1, text2,
                      text1_name='text1', text2_name='text2',
                      prefix_diff_files='tmp_diff',
                      msg=''):
    if msg != '' and msg[-1] not in ('.', '?', ':', ';', '!'):
        msg += '.'
    if msg != '':
        msg += '\n'
    msg += 'Load tmp_diff.html into a browser to see differences.'
    assert not pydiff(text1, text2, text1_name, text2_name,
                      prefix_diff_files, n=3), msg

def assert_equal_files(file1, file2,
                      text1_name='text1', text2_name='text2',
                      prefix_diff_files='tmp_diff',
                      msg=''):
    text1 = open(file1, 'r').read()
    text2 = open(file2, 'r').read()
    assert_equal_text(text1, text2,
                      text1_name=file1, text2_name=file2,
                      prefix_diff_files=prefix_diff_files,
                      msg=msg)
