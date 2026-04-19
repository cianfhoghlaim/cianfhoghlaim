#!/bin/bash
if [ $# -ne 1 ]
then
	echo "bash cuard.sh SEARCHPATT"
	exit 1
fi
egrep "([^A-Za-z-]|^)${1}($|[^A-Za-z-])" ga-full.tsv | cut -f 2 | sed 's/^/ /' | egrep -o ".{0,25}[^A-Za-z-]${1}[^A-Za-z-].{0,25}" | egrep --color=always "${1}"
