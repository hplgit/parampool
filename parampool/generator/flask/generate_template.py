import os, sys, shutil, re
from distutils.util import strtobool
import parampool.utils

def generate_template_std(classname, outfile, doc='', MathJax=False, login=False):
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
''' % vars()
    if MathJax:
        code += '''
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js"]
  }
});
</script>
<script type="text/javascript"
 src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
<!-- Fix slow MathJax rendering in IE8 -->
<meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7">
'''
    if login:
        code += '''
  {% if user.is_anonymous() %}
  <p align="right"><a href="/login">Login</a>
  / <a href="/reg">Register</a></p>
  {% else %}
  <p align="right">Logged in as {{user.username}}<br>
    <a href="/old">Previous simulations<a/><br>
    <a href="/logout">Logout</a></p>
  {% endif %}
'''
    code += '''\
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>

      <form method=post action="" enctype="multipart/form-data">
        <table>
          {%% for field in form %%}
            <tr><td>{{ field.name }}</td>
                <td>{{ field(size=20) }}</td>
                <td>{%% if field.errors %%}
                  <ul class=errors>
                  {%% for error in field.errors %%}
                    <li>{{ error }}</li>
                  {%% endfor %%}</ul>
                {%% endif %%}</td></tr>
          {%% endfor %%}
        </table>
        <p><input type="submit" value="Compute">
    </form></p>
  </td>

  <td valign="top">
    {%% if result != None %%}
      <h2>Results:</h2>
        {{ result|safe }}
''' % vars()

    if login:
        code +='''
      {% if not user.is_anonymous() %}
        <h3>Comments:</h3>
        <form method=post action="/add_comment">
            <textarea name="comments" rows="4" cols="40"></textarea>
            <p><input type="submit" value="Add">
        </form>
        {% endif %}
'''
    code += '''
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
                            pool, outfile, doc, align='left',
                            MathJax=False, login=False,
                            latex_name='text, symbol'):

    # TODO: Support for right align in 'parent' functions
    from latex_symbols import get_symbol, symbols_same_size
    import inspect
    args = inspect.getargspec(compute_function).args
    compute_function_name = compute_function.__name__
    from parampool.pool.DataItem import DataItem
    default_widget_size = DataItem.defaults['widget_size']

    pre_code = """\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Flask %(compute_function_name)s app</title>
    <link rel="StyleSheet" href="static/dtree.css" type="text/css" />
    <script type="text/javascript" src="static/dtree.js"></script>
  </head>
  <body>
""" % vars()
    if MathJax:
        pre_code += '''
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
  }
});
</script>
<script type="text/javascript"
 src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
'''
    if login:
        pre_code += """
  {% if user.is_anonymous() %}
  <p align="right"><a href="/login">Login</a>
  / <a href="/reg">Register</a></p>
  {% else %}
  <p align="right">Logged in as {{user.username}}<br>
    <a href="/old">Previous simulations<a/><br>
    <a href="/logout">Logout</a></p>
  {% endif %}
"""

    pre_code += """
  %(doc)s

  <!-- Input and Results are typeset as a two-column table -->
  <table>
  <tr>
  <td valign="top">
    <h2>Input:</h2>
    <div class="dtree">
    <p><a href="javascript: d.openAll();">open all</a> | <a href="javascript: d.closeAll();">close all</a></p>
    <form method=post action="" enctype="multipart/form-data">
      <script type="text/javascript">
        d = new dTree('d');
""" % vars()

    post_code = """\
        document.write(d);
      </script>
    </div>
    <p>
    <input type="submit" value="Compute">
    </form>
    </p>
    </td>

    <td valign="top">
      {% if result != None %}
        <h2>Result:</h2>
        {{ result|safe }}
"""
    if login:
        post_code += """
        {% if not user.is_anonymous() %}
        <h3>Comments:</h3>
        <form method=post action="/add_comment">
            <textarea name="comments" rows="4" cols="40"></textarea>
            <p><input type="submit" value="Add">
        </form>
        {% endif %}
"""
    post_code += """
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
        field_name = parampool.utils.legal_variable_name(name)

        widget_size = item.get('widget_size', default=default_widget_size)
        if item.data.get('widget', None) == 'select':
            widget_size = ''  # no specification of size for option list
        else:
            widget_size = '(size=%s)' % widget_size

        form = """\
&nbsp; {{ form.%(field_name)s%(widget_size)s }} {%% if form.%(field_name)s.errors %%} \
{%% for error in form.%(field_name)s.errors %%} <err> {{error}} </err> \
{%% endfor %%}{%% endif %%} """ % vars()

        if hasattr(user_data, 'pb'):
            user_data.pb.update(user_data.pbid)
            user_data.pbid += 1

        if 'symbol' in item.data:
            if latex_name == 'symbol':
                symbol = item.data["symbol"]
            elif latex_name == 'text, symbol':
                symbol = "\\mbox{%s}" % name + ',\\ ' + item.data["symbol"]
        else:
            symbol = "\\mbox{%s}" % name
        imgsrc = get_symbol(symbol, 'static', tree_path)

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
            line = '%(form)s<img src="%(imgsrc)s" height="18" />' % vars()
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
    pool.update()
    num_widgets = len(args) if pool is None else len(pool.paths2data_items)
    display_progressbar = num_widgets >= 10
    if display_progressbar:
        from progressbar import \
             ProgressBar, Percentage, Bar, ETA, RotatingMarker
        widgets = ['Generating: ', Percentage(), ' ',
                   Bar(marker=RotatingMarker()), ' ', ETA()]
        pb = ProgressBar(widgets=widgets, maxval=num_widgets-1).start()
        codedata.pb = pb
    pool.traverse(callback_leaf=leaf_func,
          callback_subtree_start=subtree_start_func,
          callback_subtree_end=subtree_end_func,
          user_data=codedata,
          verbose=False)
    if display_progressbar:
        pb.finish()
    code = codedata.code + post_code
    symbols_same_size('static')

    if outfile is None:
        return code
    else:
        f = open(outfile, 'w')
        f.write(code)
        f.close()

def generate_login_templates(classname):
    login_template = os.path.join("templates", "login.html")
    reg_template = os.path.join("templates", "reg.html")
    old_template = os.path.join("templates", "old.html")

    header = '''\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Flask %(classname)s app</title>
  </head>
  <body>
''' % vars()

    login = open(login_template, 'w')
    login.write(header)
    login.write('''\
    <h2>Login:</h2>
      <form method=post action="">
        <table>
          {% for field in form %}
            <tr><td>{{ field.label }}</td>
                <td>{{ field(size=20) }}</td>
                <td>{% if field.errors %}
                  <ul class=errors>
                  {% for error in field.errors %}
                    <li>{{ error }}</li>
                  {% endfor %}</ul>
                {% endif %}</td></tr>
          {% endfor %}
        </table>
        <p><input type="submit" value="Login">
    </form>
  </body>
</html>''')
    login.close()

    reg = open(reg_template, 'w')
    reg.write(header)
    reg.write('''\
<h2>Register:</h2>
  <form method=post action="">
    <table>
      {% for field in form %}
        <tr><td>{{ field.label }}</td>
            <td>{{ field(size=20) }}</td>
            <td>
            {% if field.errors %}
              <ul class=errors>
              {% for error in field.errors %}
                <li>{{ error }}</li>
              {% endfor %}</ul>
            {% endif %}
            </td>
        </tr>
      {% endfor %}
    </table>
    <p><input type="submit" value="Register">
</form>
</body>
</html>''')
    reg.close()

    old = open(old_template, 'w')
    old.write(header)
    old.write('''
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  TeX: {
     equationNumbers: {  autoNumber: "AMS"  },
     extensions: ["AMSmath.js", "AMSsymbols.js", "autobold.js", "color.js"]
  }
});
</script>
<script type="text/javascript"
 src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
''')
    old.write('''\
<h2>Previous simulations</h2>
<p align="right"><a href="/">Back to index</a></p>

{% if data %}
  {% for post in data %}
  <hr>
  <table>
  <tr>
    <td valign="top" width="30%">
      <h3>Input</h3>
      <table>
      {% for field in post.form %}
         <tr><td>{{ field.label }}:&nbsp;</td>
             <td>{{ field.data }}</td></tr>
      {% endfor %}
      </table>
    </td>
    <td valign="top" width="60%">
      <h3>Results</h3>
      {{ post.result|safe }}
    </td><td valign="top" width="10%">
    <p>
    <form method="POST" action="/delete/{{ post.id }}">
      <input type="submit" value="Delete"
       title="Delete this post from database">
    </form>
    </td></tr>
  </table>
  {% endfor %}
  <hr>
  <center>
  <form method="POST" action="/delete/-1">
      <input type="submit" value="Delete all">
  </form>
  </center>
{% else %}
    No previous simulations
{% endif %}
</body>
</html>''')
    old.close()


def run_doconce_on_text(doc):
    if doc is None:
        return ''

    def wrap_in_pre_tags(text):
        return '<code><pre>\n%s\n</pre></code>\n' % text

    if re.search(r'#\s*\(?[Dd]oc[Oo]nce', doc):
        from doconce.common import fix_backslashes
        doc = fix_backslashes(doc)
        # Remove indentation
        lines = doc.splitlines()
        for i in range(len(lines)):
            if lines[i][0:4] == '    ':
                lines[i] = lines[i][4:]
        doc = '\n'.join(lines)

        # Run doconce using a lib version of the doconce format command
        from doconce import doconce_format, DocOnceSyntaxError
        stem = 'tmp_doc_string'
        try:
            print 'Found doc string in doconce format:'
            print 'Running doconce on help file', stem + '.do.txt'
            doc = doconce_format('html', doc, filename_stem=stem,
                                 cleanup=False)
            # grab parts
            pattern = r'(<!-- tocinfo.+------ end of main content ---.+?-->)'
            m = re.search(pattern, doc, flags=re.DOTALL)
            if m:
                doc = m.group(1) + '\n'
                doc = doc.replace('<body>\n', '')
            files = [stem + '.do.txt',
                     stem + '.html',
                     '.' + stem + '_html_file_collection']
            #for name in files:
            #    os.remove(name)
        except DocOnceSyntaxError, e:
            print e
            doc = wrap_in_pre_tags(doc)
    else:
        doc = wrap_in_pre_tags(doc)
    return doc

def generate_template(compute_function, classname, outfile,
                      pool=None, overwrite=False, MathJax=False,
                      doc='', login=False, latex_name='text, symbol'):
    if doc == '':
        # Apply doc string as documentation
        doc = run_doconce_on_text(compute_function.__doc__)

    if 'MathJax.Hub.Config' in doc:
        MathJax = False  # no need to enable MathJax - it's in the doc HTML

    if outfile is not None:
        if not os.path.isdir("templates"):
            os.mkdir("templates")
        outfile = os.path.join("templates", outfile)

        # Check if file should be overwritten
        if not overwrite and os.path.isfile(outfile):
            if not strtobool(raw_input(
                "The file %s already exists. Overwrite? [Y/N]: " % outfile)):
                return None

    if login:
        generate_login_templates(classname)

    if pool is not None:
        return generate_template_dtree(
            compute_function, classname, pool, outfile, doc,
            MathJax=MathJax, login=login, latex_name=latex_name)
    else:
        return generate_template_std(classname, outfile, doc, MathJax, login)
