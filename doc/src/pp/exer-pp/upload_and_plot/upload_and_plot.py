def pool_def_api():
    from parampool.pool.Pool import Pool
    pool = Pool()
    pool.subpool('Main pool')
    pool.add_data_item(name='Filename', widget='file')
    return pool

def compute(pool):
    filename = pool.get_value('Filename')
    return upload_and_plot(filename)

def upload_and_plot(filename):
    import matplotlib.pyplot as plt
    import numpy as np
    data = np.loadtxt(filename)
    for i in range(1, data.shape[1]):
        plt.plot(data[:,0], data[:,i])
    from StringIO import StringIO
    figfile = StringIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = figfile.buf  # extract string
    import base64
    figdata_png = base64.b64encode(figdata_png)
    html_text = '<img src="data:image/png;base64,%s" width="400">' % \
                figdata_png
    return html_text
