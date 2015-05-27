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
    # Plot
    # Return PNG embedded plot
    pass
