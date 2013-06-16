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
        msg = '.'
    if msg != '':
        msg += '\n'
    msg += 'Load tmp_diff.html into a browser to see differences.'
    assert not pydiff(text1, text2, text1_name, text2_name,
                      prefix_diff_files, n=3), msg

