#!/bin/sh
name=pp

function system {
  "$@"
  if [ $? -ne 0 ]; then
    echo "make.sh: unsuccessful command $@"
    echo "abort!"
    exit 1
  fi
}

system doconce format html $name --html_style=bootstrap_bluegray --html_code_style=inherit
system doconce split_html $name.html --pagination

system doconce format pdflatex $name --latex_code_style=pyg
system pdflatex -shell-escape $name
pdflatex -shell-escape $name
bibtex $name
makeindex $name
pdflatex -shell-escape $name
pdflatex -shell-escape $name

# Publish
dest=../../pub
cp -r fig-pp $name.pdf $name.html ._${name}*.html $dest
