#!/bin/bash
# Script for installing various kind of math software on
# Wakari.

set -e

PREFIX=$HOME/local

export CPPFLAGS="-I$PREFIX/include"
export LDFLAGS="-L$PREFIX/lib"

export BINARY_PATH=$PREFIX/bin
export INCLUDE_PATH=$PREFIX/include
export LIBRARY_PATH=$PREFIX/lib

export PATH=$PREFIX:$PREFIX/bin:$PATH
export PYTHONPATH=$PREFIX/lib/python2.7/site-packages:$PYTHONPATH
export PKG_CONFIG_PATH=$PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

parampool=parampool
parampoolURL=https://github.com/hplgit/$parampool.git

ScientificPython=ScientificPython-2.9.2
ScientificPythonURL=https://sourcesup.renater.fr/frs/download.php/4153/$ScientificPython.tar.gz

progressbar=progressbar-2.3
progressbarURL=http://python-progressbar.googlecode.com/files/$progressbar.tar.gz

flaskWTF=flask-wtf
flaskWTFURL=https://github.com/ajford/$flaskWTF.git

djangoversion=1.4.5
django=Django-$djangoversion
djangoURL=http://www.djangoproject.com/download/1.4.5/tarbal/

zlib=zlib-1.2.8
zlibURL=zlib.net/$zlib.tar.gz

libpngversion=16
libpngpatch=1.6.2
libpng=libpng-$libpngpatch
libpngURL=http://sourceforge.net/projects/libpng/files/libpng$libpngversion/$libpngpatch/$libpng.tar.gz

libgd=libgd-2.1.0-rc2
libgdURL=https://bitbucket.org/libgd/gd-libgd/downloads/$libgd.tar.gz

gnuplotversion=4.6.2
gnuplot=gnuplot-$gnuplotversion
gnuplotURL=http://sourceforge.net/projects/gnuplot/files/gnuplot/$gnuplotversion/$gnuplot.tar.gz

imagemagick=ImageMagick-6.8.5-10
imagemagickURL=http://mirror.searchdaimon.com/ImageMagick/$imagemagick.tar.gz


tarurls="$ScientificPythonURL $progressbarURL $djangoURL $zlibURL $libpngURL $libgdURL $gnuplotURL $imagemagickURL"
tarballs="$ScientificPython $progressbar $django $zlib $libpng $libgd $gnuplot $imagemagick"

giturls="$parampoolURL $flaskWTFURL"

makeinstalls="$libgd $gnuplot $imagemagick"
pythonsetup="$ScientificPython $progressbar $django $flaskWTF"


cd $HOME
mkdir -p $PREFIX/src
cd $PREFIX/src

for url in $tarurls; do
    wget $url
done

for ball in $tarballs; do
    tar xzf $ball.tar.gz
done


for url in $giturls; do
    git clone $url
done

# Need to install this in the right order because of libpng's --with-zlib-prefix
cd $zlib
./configure --prefix=$PREFIX
make
make install
cd ../$libpng
./configure --prefix=$PREFIX --with-zlib-prefix=$PREFIX
make
make install
cd ..

for dir in $makeinstalls; do
    cd $dir
    ./configure --prefix=$PREFIX
     if [ $? -ne 0 ]; then
        echo "Problems with building $dir"
        exit 1
    fi
    make
    if [ $? -ne 0 ]; then
        echo "Problems with make in $dir"
        exit 1
    fi
    make install
    if [ $? -ne 0 ]; then
        echo "Problems with make install in $dir"
        exit 1
    fi
    cd ..
done

for dir in $pythonsetup; do
    cd $dir
    python setup.py install --prefix=$PREFIX
    if [ $? -ne 0 ]; then
        echo "Problems with building $dir"
        exit 1
    fi
    cd ..
done

cd $HOME
