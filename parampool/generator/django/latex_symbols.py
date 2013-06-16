import os

def get_symbol(symbol, static_dir, path=[], dpi=120):
    """Download a transparent LaTeX symbol."""

    static_dir = os.path.join(static_dir, "latex")

    # Remove space in dirname
    path = [p.replace(' ', '_') for p in path]

    subdir = "/".join(path)
    symdir = os.path.join(static_dir, subdir)
    if not os.path.isdir(symdir):
        os.makedirs(symdir)

    name = symbol.strip('\\') + '.png'
    filename = os.path.join(symdir, name)
    link = 'http://latex.codecogs.com/png.latex?\dpi{%(dpi)d}&space;%(symbol)s' \
            % vars()

    import urllib
    f = open(filename, 'wb')
    f.write(urllib.urlopen(link).read())
    f.close()
    return filename

def symbols_same_size(static_dir):
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
            cmd = 'convert -extent %(max_width)dx%(height)d %(symdir)s %(symdir)s' \
                    % vars()
            status, output = commands.getstatusoutput(cmd)
            if status:
                import sys
                sys.stderr.write(output + '\n')
                sys.exit(status)
