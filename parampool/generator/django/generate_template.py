import os
from distutils.util import strtobool
import parampool.utils

def generate_template_std(classname, outfile, doc='', login=False):
    """
    Generate a simple standard template with
    input form in the left column and results in
    the right column.
    """
    code = '''\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Django %(classname)s app</title>
  </head>
  <body>
''' % vars()

    if login:
        code += '''\
  {% if user.is_anonymous %}
  <p align="right"><a href="/login">Login</a> / <a href="/reg">Register</a></p>
  {% else %}
  <p align="right">Logged in as {{user}}<br><a href="/logout">Logout</a>
  {% endif %}
''' % vars()

    code += '''\
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
''' % vars()

    if login:
        code += '''
        {% if not user.is_anonymous %}
        <h3>Comments:</h3>
        <form method=post action="/add_comment/">{% csrf_token %}
            <textarea name="comments" rows="4" cols="40"></textarea>
            <p><input type=submit value=Add>
        </form>
        {% endif %}
'''
    code +='''
    {% endif %}
  </td>
  </tr>
  </table>
  </body>
</html>'''

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_template_dtree(compute_function, classname,
                            menu, outfile, doc, login, align='left'):

    # TODO: Support for right align in 'parent' functions
    from parampool.generator.flask.latex_symbols import \
         get_symbol, symbols_same_size
    import inspect
    args = inspect.getargspec(compute_function).args
    app_dir = outfile.split("templates")[0]
    static_dir = os.path.join(app_dir, "static")

    pre_code = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Django %(classname)s app</title>
    <link rel="StyleSheet" href="static/dtree.css" type="text/css" />
    <script type="text/javascript" src="static/dtree.js"></script>
  </head>
  <body>
""" % vars()

    if login:
        pre_code += '''\
  {% if user.is_anonymous %}
  <p align="right"><a href="/login">Login</a> / <a href="/reg">Register</a></p>
  {% else %}
  <p align="right">Logged in as {{user}}<br><a href="/old">Previous simulations</a><br><a href="/logout">Logout</a></p>
  {% endif %}
'''

    pre_code += """\
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>
    <div class="dtree">
    <p><a href="javascript: d.openAll();">open all</a> | <a href="javascript: d.closeAll();">close all</a></p>
    <form method=post action="" enctype=multipart/form-data>{%% csrf_token %%}
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
"""

    if login:
        post_code += '''
      {% if not user.is_anonymous %}
      <h3>Comments:</h3>
      <form method=post action="/add_comment/">{% csrf_token %}
        <textarea name="comments" rows="4" cols="40"></textarea>
        <p><input type=submit value=Add>
      </form>
      {% endif %}
'''
    post_code +='''
    {% endif %}
  </td>
  </tr>
  </table>
  </body>
</html>'''

    def leaf_func(tree_path, level, item, user_data):
        id = user_data.id
        parent_id = user_data.parent_id[-1]
        name = item.name
        field_name = parampool.utils.legal_variable_name(name)
        form = """\
&nbsp; {%% spaceless %%} {{ form.%(field_name)s }} {%% endspaceless %%} \
{%% if form.%(field_name)s.errors %%} \
{%% for error in form.%(field_name)s.errors %%} \
<err> {{error}} </err> \
{%% endfor %%}{%% endif %%} """ % vars()

        if hasattr(user_data, 'pb'):
            user_data.pb.update(user_data.pbid)
            user_data.pbid += 1

        if item.data.has_key("symbol"):
            symbol = item.data["symbol"]
        else:
            symbol = "\\mbox{%s}" % name
        imgsrc = get_symbol(symbol, static_dir, tree_path)
        imgsrc = os.sep + "static" + imgsrc.split("static")[-1]

        # Use slider and show current value
        if item.data.get("widget", None) in ("range", "integer_range"):
            showvalue = ' &nbsp; <span id="range"></span>'
        else:
            showvalue = ""

        # Make label
        label = []
        if 'help' in item.data:
            label.append(item.data['help'])
        if 'unit' in item.data:
            label.append('Unit: ' + item.data['unit'])
        label = ' '.join(label)

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

    codedata = CodeData()
    codedata.code = pre_code
    # Display a progressbar if we have many data items
    num_widgets = len(args) if menu is None else len(menu.paths2data_items)
    display_progressbar = num_widgets > 20
    if display_progressbar:
        from progressbar import \
             ProgressBar, Percentage, Bar, ETA, RotatingMarker
        widgets = ['Generating: ', Percentage(), ' ',
                   Bar(marker=RotatingMarker()), ' ', ETA()]
        pb = ProgressBar(widgets=widgets, maxval=num_widgets-1).start()
        codedata.pb = pb
    menu.traverse(callback_leaf=leaf_func,
          callback_subtree_start=subtree_start_func,
          callback_subtree_end=subtree_end_func,
          user_data=codedata,
          verbose=False)
    if display_progressbar:
        pb.finish()

    code = codedata.code + post_code
    symbols_same_size(static_dir)

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_form_templates(outfile):
    path = os.path.split(outfile)[0]
    login_file = os.path.join(path, "login.html")
    reg_file = os.path.join(path, "reg.html")
    old_file = os.path.join(path, "old.html")

    login = open(login_file, 'w')
    login.write("""\
<form method="post" action="">{% csrf_token %}
<table>
  {{form.as_table}}
  <tr><td>&nbsp;</td><td><input type="submit" value="Login" /></td></tr>
</table>
</form>""")
    login.close()
    reg = open(reg_file, 'w')
    reg.write("""\
<form method="post" action="">{% csrf_token %}
<table>
  {{form.as_table}}
  <tr><td>&nbsp;</td><td><input type="submit" value="Create User" /></td></tr>
</table>
</form>
{% for e in errors %}
{{ e }}
{% endfor %}""")
    reg.close()

    old = open(old_file, 'w')
    old.write('''\
<!DOCTYPE html>
<html lang="en">
  <head>
      <meta charset="utf-8" />
  </head>
  <body>
      <h2>Previous simulations</h2>
      <p align="right"><a href="/">Back to index</a></p>
      {% if results %}
      {% load extras %}
        {% for form, result in forms|zip:results %}
        <hr>
        <table>
            <tr>
                <td valign="top" width="20%">
                    <h3>Input</h3>
                    <table>
                    {% for field in form %}
                      <tr><td>{{ field.name }}:&nbsp;</td>
                        <td>{{ field.value }}</td></tr>
                    {% endfor %}
                    </table>
                    </td><td valign="top" width="80%">
                    <h3>Results</h3>
                    {{ result|safe }}
            </td></tr>
        </table>
        {% endfor %}
      {% else %}
          No previous simulations
      {% endif %}
  </body>
</html>''')
    old.close()

    app = path.strip("templates")
    tagsdir = app + os.sep + "templatetags"
    os.mkdir(tagsdir)
    f = open(os.path.join(tagsdir, "extras.py"), 'w')
    f.write('''\
from django import template
register = template.Library()
@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)''')
    f.close()
    f = open(os.path.join(tagsdir, "__init__.py"), 'w')
    f.write('')
    f.close()

def generate_template(compute_function, classname,
                      outfile, menu=None, login=False):
    from parampool.generator.flask.generate_template import run_doconce_on_text
    doc = run_doconce_on_text(compute_function.__doc__)

    if login:
        generate_form_templates(outfile)

    if menu:
        return generate_template_dtree(
                compute_function, classname, menu, outfile, doc, login)
    else:
        return generate_template_std(classname, outfile, doc, login)
