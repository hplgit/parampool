import os

STATIC_DIR = 'static/latex/'

def get_symbol(symbol, path=[], dpi=120):
    """Download a transparent LaTeX symbol."""

    # Remove space in dirname
    path = [p.replace(' ', '_') for p in path]

    subdir = "/".join(path)
    symdir = os.path.join(STATIC_DIR, subdir)
    if not os.path.isdir(symdir):
        os.makedirs(symdir)

    name = symbol.replace(' ', '_').replace('mbox', '').strip('\\{}') + '.png'
    filename = os.path.join(symdir, name)
    print 'XXX saving to file [%s]' % filename
    link = 'http://latex.codecogs.com/png.latex?\dpi{%(dpi)d}&space;%(symbol)s' \
            % vars()

    import urllib
    f = open(filename, 'wb')
    f.write(urllib.urlopen(link).read())
    f.close()
    return filename

def symbols_same_size():
    """Enforce the same dimensions on all symbols in each subdirectory."""
    from PIL import Image
    import commands

    for dir, subdirs, symbols in os.walk(STATIC_DIR):
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
            cmd = 'convert -extent %(max_width)dx%(height)d %(symdir)s %(symdir)s' \
                    % vars()
            print 'XXX running command\n', cmd
            failure, output = commands.getstatusoutput(cmd)
            if failure:
                import sys
                sys.stderr.write(output + '\nAbort!\n')
                sys.exit(failure)
