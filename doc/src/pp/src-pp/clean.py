import os, shutil

savefiles = ['generate.py', 'mydata.dat']
# Visit subdirs and clean
for name in os.listdir(os.curdir):
    if os.path.isdir(name) and \
           (name.startswith('flask') or name.startswith('django')):
        os.chdir(name)
        print 'cleaning', name
        for name2 in os.listdir(os.curdir):
            if name2 not in savefiles:
                print '  removing', name2
                if os.path.isfile(name2):
                    os.remove(name2)
                elif os.path.isdir(name2):
                    shutil.rmtree(name2)
        shutil.copy(os.path.join(os.pardir, 'compute.py'), 'compute.py')

