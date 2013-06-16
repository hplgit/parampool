import os, sys

def fix_settings(projectname, appname):
    f = open("%(projectname)s/%(projectname)s/settings.py" % vars(), "r")
    lines = f.readlines()
    f.close()
    f = open("%(projectname)s/%(projectname)s/settings.py" % vars(), "w")
    apps = False
    for line in lines:
        if line.startswith("INSTALLED_APPS"):
            apps = True
        if apps:
            if "#" in line:
                f.write("    '%(appname)s',\n" % vars())
                apps = False
        f.write(line)
    f.close()

def fix_urls(projectname, appname):
    f = open("%(projectname)s/%(projectname)s/urls.py" % vars(), "w")
    f.write("""\
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', '%(appname)s.views.index', name='home'),
)""" % vars())
    f.close()

def start_all(projectname, appname):
    os.system("django-admin.py startproject %s" % projectname)
    os.chdir(projectname)
    os.system("django-admin.py startapp %s" % appname)
    os.chdir("../")

    fix_settings(projectname, appname)
    fix_urls(projectname, appname)
