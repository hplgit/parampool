import os
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
    <title>Django %(classname)s app</title>
  </head>
  <body>
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>

      <form method=post action="" enctype=multipart/form-data>{%% csrf_token %%}
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
    app_dir = outfile.split("templates")[0]
    static_dir = os.path.join(app_dir, "static")

    pre_code = """\
<html>
  <head>
    <meta charset="utf-8" />
    <title>Django %(classname)s app</title>
    <link rel="StyleSheet" href="static/dtree.css" type="text/css" />
    <script type="text/javascript" src="static/dtree.js"></script>
  </head>
  <body>
    <div class="dtree">
    %(doc)s
    <h2>Input:</h2>
    <p><a href="javascript: d.openAll();">open all</a> | <a href="javascript: d.closeAll();">close all</a></p>
    <form method=post action="">{%% csrf_token %%}
      <script type="text/javascript">
        d = new dTree('d');
""" % vars()
    post_code = """\
        document.write(d);
      </script>
    </div>
    <p><input type=submit value=Compute></form></p>

    {% if result != None %}
      <h2>Result:</h2>
        {{ result }}
    {% endif %}
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
        imgsrc = get_symbol(symbol, static_dir, tree_path)
        imgsrc = '/'.join(imgsrc.split('/')[2:])

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
    pb = ProgressBar(widgets=widgets, maxval=len(args)-1).start()
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
    symbols_same_size(static_dir)

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_template(compute_function, classname, outfile, menu=None):
    from parampool.generator.flask.generate_template import run_doconce_on_text
    doc = run_doconce_on_text(compute_function.__doc__)

    if menu:
        return generate_template_dtree(
            compute_function, classname, menu, outfile, doc)
    else:
        return generate_template_std(classname, outfile, doc)
