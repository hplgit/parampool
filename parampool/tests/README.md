Run tests as this:

```
Terminal> py.test -s -x test_generators.py
```

Load `tmp_diff.html` into a browser, inspect differences, and copy new file
(left window) to the reference (name in the right window).

If differences (failures) occur, and new files seem correct, copy new
files to the reference (the filenames appear in the `tmp_diff*.html`
files that one should examine in a browser to see the differences.)
If new files are missing, it may be because py.test allows
`test_generators.py` to continue with cleaning up files. Find the
function in `test_generators.py` that triggered the failure and
run manually the corresponding script (e.g., `python generate_flask2.py`)
which will regenerate the files but not remove them.
