#!/bin/sh
name=pp
doconce format html $name --html_style=bloodish

doconce format pdflatex $name
doconce ptex2tex $name envir=minted
pdflatex -shell-escape $name
pdflatex -shell-escape $name
