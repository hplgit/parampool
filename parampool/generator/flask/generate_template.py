import os, sys, shutil, re
from distutils.util import strtobool

def generate_template_std(classname, outfile, doc=''):
    """
    Generate a simple standard template with
    input form. Show result at the bottom of
    the page.
    """
    code = '''\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Flask %(classname)s app</title>
  </head>
  <body>
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>

      <form method=post action="" enctype=multipart/form-data>
        <table>
          {%% for field in form %%}
            <tr><td>{{ field.name }}</td>
                <td>{{ field }}</td>
                <td>{%% if field.errors %%}
                  <ul class=errors>
                  {%% for error in field.errors %%}
                    <li>{{ error }}</li>
                  {%% endfor %%}</ul>
                {%% endif %%}</td></tr>
          {%% endfor %%}
        </table>
        <p><input type=submit value=Compute>
    </form></p>
  </td>

  <td valign="top">
    {%% if result != None %%}
      <h2>Results:</h2>
        {{ result|safe }}
    {%% endif %%}
  </td>
  </tr>
  </table>
  </body>
</html>''' % vars()

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_template_dtree(compute_function, classname,
                            menu, outfile, doc, align='left'):

    # TODO: Support for right align in 'parent' functions
    from latex_symbols import get_symbol, symbols_same_size
    from progressbar import ProgressBar, Percentage, Bar, ETA, RotatingMarker
    import inspect
    args = inspect.getargspec(compute_function).args

    pre_code = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Flask %(classname)s app</title>
    <link rel="StyleSheet" href="static/dtree.css" type="text/css" />
    <script type="text/javascript" src="static/dtree.js"></script>
  </head>
  <body>
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>
    <div class="dtree">
    <p><a href="javascript: d.openAll();">open all</a> | <a href="javascript: d.closeAll();">close all</a></p>
    <form method=post action="" enctype=multipart/form-data>
      <script type="text/javascript">
        d = new dTree('d');
""" % vars()
    post_code = """\
        document.write(d);
      </script>
    </div>
    <p><input type=submit value=Compute></form></p>
    </td>

    <td valign="top">
      {% if result != None %}
        <h2>Result:</h2>
        {{ result|safe }}
    {% endif %}
    </td>
    </tr>
    </table>
  </body>
</html>"""

    def leaf_func(tree_path, level, item, user_data):
        id = user_data.id
        parent_id = user_data.parent_id[-1]
        name = item.name
        form = """\
&nbsp; {{ form.%(name)s }} {%% if form.%(name)s.errors %%} \
{%% for error in form.%(name)s.errors %%} <err> {{error}} </err> \
{%% endfor %%}{%% endif %%} """ % vars()

        user_data.pb.update(user_data.pbid)
        user_data.pbid += 1

        if item.data.has_key("symbol"):
            symbol = item.data["symbol"]
        else:
            symbol = "\\mbox{%s}" % name
        imgsrc = get_symbol(symbol, tree_path)

        # Use slider and show current value
        if item.data.get("widget", None) in ("range", "integer_range"):
            showvalue = ' &nbsp; <span id="range"></span>'
        else:
            showvalue = ""

        # Make label
        label = ""
        if item.data.has_key("help"):
            label += item.data["help"]
        if item.data.has_key("unit"):
            label += " (" + item.data["unit"] + ")"

        if align == "right":
            line = '%(form)s<img src="%(imgsrc)s" />' % vars()
            line += showvalue
            user_data.code += """\
                    d.add(%(id)i, %(parent_id)i, '%(line)s', '#', '%(label)s');
""" % vars()
        else:
            form += showvalue
            user_data.code += """\
                    d.add(%(id)i, %(parent_id)i, '%(form)s', '#', '%(label)s', '', '%(imgsrc)s');
""" % vars()
        user_data.id += 1

    def subtree_start_func(tree_path, level, item, user_data):
        id = user_data.id
        parent_id = user_data.parent_id[-1]
        name = item.name
        user_data.code += """\
                    d.add(%(id)i, %(parent_id)i, '%(name)s');
""" % vars()
        user_data.parent_id.append(user_data.id)
        user_data.id += 1

    def subtree_end_func(tree_path, level, item, user_data):
        del user_data.parent_id[-1]

    class CodeData:
        """Object to hold output code through tree recursion."""
        id = 0
        pbid = 0
        parent_id = [-1]

    # Progressbar
    widgets = ['Generating: ', Percentage(), ' ',
               Bar(marker=RotatingMarker()), ' ', ETA()]
    num_widgets = len(args) if menu is None else len(menu.paths2data_items)
    pb = ProgressBar(widgets=widgets, maxval=num_widgets-1).start()
    codedata = CodeData()
    codedata.pb = pb
    codedata.code = pre_code
    menu.traverse(callback_leaf=leaf_func,
          callback_subtree_start=subtree_start_func,
          callback_subtree_end=subtree_end_func,
          user_data=codedata,
          verbose=False)
    pb.finish()
    code = codedata.code + post_code
    symbols_same_size()

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def run_doconce_on_text(doc):
    if doc is None:
        return ''

    def wrap_in_pre_tags(text):
        return '<code><pre>\n%s\n</pre></code>\n' % text

    if re.search(r'#\s*\(?[Dd]oconce', doc):
        from doconce.common import fix_backslashes
        doc = fix_backslashes(doc)
        # Remove indentation
        lines = doc.splitlines()
        for i in range(len(lines)):
            if lines[i][0:4] == '    ':
                lines[i] = lines[i][4:]
        doc = '\n'.join(lines)

        # Run doconce
        print 'Found doc string in doconce format:'
        filename = 'tmp1'
        f = open(filename + '.do.txt', 'w')
        f.write(doc)
        f.close()
        print 'Running doconce on help file', filename + '.do.txt'
        failure = os.system('doconce format html %s' % filename)
        if not failure:
            f = open(filename + '.html', 'r')
            doc = f.read()
            f.close()
            files = [filename + '.do.txt',
                     filename + '.html',
                     '.' + filename + '_html_file_collection']
            #for name in files:
            #    os.remove(name)
        else:
            doc = wrap_in_pre_tags(doc)
    else:
        doc = wrap_in_pre_tags(doc)
    return doc

def generate_template(compute_function, classname, outfile, menu=None, overwrite=False):
    doc = run_doconce_on_text(compute_function.__doc__)

    if outfile is not None:
        if not os.path.isdir("templates"):
            os.mkdir("templates")
        outfile = os.path.join("templates", outfile)

        # Check if file should be overwritten
        if not overwrite and os.path.isfile(outfile):
            if not strtobool(raw_input(
                "The file %s already exists. Overwrite? [Y/N]: " % outfile)):
                return None

    if menu is not None:
        return generate_template_dtree(
                compute_function, classname, menu, outfile, doc)
    else:
        return generate_template_std(classname, outfile, doc)
