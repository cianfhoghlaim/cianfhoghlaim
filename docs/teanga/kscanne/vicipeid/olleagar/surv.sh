#!/bin/bash
if [ $# -ne 2 ]
then
	echo "Usage: bash surv.sh FREQ NUM"
	echo "  Where FREQ is the frequency in bad.txt we want to survey,"
	echo "  and NUM is the number of words we want to see"
	echo "  NB FREQ is a regex, so we can use '[0-9]+' if no restriction"
	echo "  or stuff like '[0-9][0-9]+ for 10+, etc."
	exit 1
fi
egrep "^${1} " bad.txt | sed 's/^[0-9]* //' | egrep -v '[A-Z]' | keepif -n /usr/local/share/crubadan/en/GLAN | shuf | head -n "${2}" | sort |
while read x
do
	echo; echo; echo; echo "$x á lorg......"
	q "$x" | head -n 250
	echo "In WP....."
	bash cuard.sh "${x}" | head -n 250
done | more
