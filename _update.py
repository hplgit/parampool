"""Pack static directories as tarfiles in flask/django_generator."""
import os, tarfile

os.chdir(os.path.join('parampool', 'generator', 'flask'))
print 'packing tarfile in', os.getcwd()
archive = tarfile.open('static.tar.gz', mode='w:gz')
archive.add('static')
print 'flask tarfile:'
for name in archive.getnames():
    print name
archive.close()

os.chdir(os.path.join(os.pardir, 'django'))
print 'packing tarfile in', os.getcwd()
archive = tarfile.open('static.tar.gz', mode='w:gz')
archive.add('static')
print '\ndjango tarfile:'
for name in archive.getnames():
    print name
archive.close()


