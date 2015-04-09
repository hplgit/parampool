#!/bin/sh
name=pp
doconce format html $name --html_style=bootstrap_bluegray --html_code_style=inherit
doconce split_html $name.html --pagination

doconce format pdflatex $name --latex_code_style=pyg
pdflatex -shell-escape $name
pdflatex -shell-escape $name

# Publish
dest=../../pub
cp -r fig-pp $name.pdf $name.html ._${name}*.html $dest
