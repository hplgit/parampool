import os, re

_contacted_latex_codecogs_com = False

def get_symbol(symbol, static_dir='static', path=[], dpi=300):
    """Download a transparent LaTeX symbol."""

    static_dir = os.path.join(static_dir, "latex")

    # Remove space in dirname
    path = [p.replace(' ', '_') for p in path]

    subdir = "/".join(path)
    symdir = os.path.join(static_dir, subdir)
    if not os.path.isdir(symdir):
        os.makedirs(symdir)

    name = symbol.replace(' ', '_').replace('mbox', '')
    for c in '''$^[]!@#%+=|/<>,.`~"'\\{}''':
        name = name.replace(c, '')
    name += '.png'
    filename = os.path.join(symdir, name)
    link = 'http://latex.codecogs.com/png.latex?\dpi{%(dpi)d}&space;%(symbol)s' \
            % vars()

    if not _contacted_latex_codecogs_com:
        print '....contacting http://latex.codecogs.com to convert latex symbols to png files\n'
        global _contacted_latex_codecogs_com
        _contacted_latex_codecogs_com = True
    import urllib
    try:
        code = urllib.urlopen(link).read()
    except IOError:
        raise IOError('No Internet connection? Cannot open http://latex.codecogs.com/png.latex...')
    f = open(filename, 'wb')
    f.write(code)
    f.close()
    failure = os.system('convert %s -resize x15 %s' % (filename, filename))
    if failure:
        print 'Could not resize latex image', filename

    return filename

def symbols_same_size(static_dir='static'):
    """Enforce the same dimensions on all symbols in each subdirectory."""
    from PIL import Image
    import commands

    static_dir = os.path.join(static_dir, "latex")

    for dir, subdirs, symbols in os.walk(static_dir):
        max_width  = 0
        dir = dir.replace(' ', '_')

        # Get largest dimensions
        for symbol in symbols:
            symdir = os.path.join(dir, symbol)
            img = Image.open(symdir)
            max_width = max(max_width, img.size[0])

        # Set all symbols to the same dimensions by filling up with white-space
        for symbol in symbols:
            symdir = os.path.join(dir, symbol)
            img = Image.open(symdir)
            height = img.size[1]
            cmd = 'convert -extent %(max_width)dx%(height)d %(symdir)s %(symdir)s' % vars()
            failure, output = commands.getstatusoutput(cmd)
            if failure:
                import sys
                sys.stderr.write(output + '\nAbort!\n')
                sys.exit(failure)
