#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash ambig2wiki.sh SEARCHTERM"
	echo "Outputs wikitext that should be pastable into a new"
	echo "disambiguation page named 'Cill Chiaráin (idirdhealú)' or whatever"
	exit 1 
fi

# pipe one HTML file through this and output content ready for WP
# (but not sorted)
# The one argument is the same SEARCHTERM passed to surrounding shell script
procone() {
	tr -d "\r\n" | sed 's/<div[^>]*placelist/\n&/g' | egrep '^<div' | sed 's/^.*nameline">//' | sed 's/Tuilleadh<\/a>.*/Tuilleadh<\/a>/' | sed 's/<span.lang="en">[^<]*<\/span>//g' | sed 's/<span>..<\/span>//g' | sed 's/^\(.*\)href="\/ga\/\([0-9]*\).*$/\2<>\1>/' | sed 's/<span class="lowlight">\([^<]*\)<\/span>/\1/g' | sed 's/<[^>]*>/~/g' | sed 's/~ */~/g' | sed 's/~~*/~/g' | sed 's/[~ ]*$//' | sed 's/  */ /g' | egrep "^[0-9]+~${1}~" | egrep -v '~(gné|mionghné)~' | tr "~" "\t"
}

CUARDACH=`echo "${1}" | tr " " "+"`
#  add str=1 to include street names in search; causes problems though...
#URL="https://logainm.ie/ga/s?txt=${CUARDACH}&str=1"
URL="https://logainm.ie/ga/s?txt=${CUARDACH}"
#TMPFILE=`mktemp`
TMPFILE=./temptemp
wget --no-check-certificate -O "${TMPFILE}" "${URL}"  > /dev/null 2>&1
TMPFILE2=./temptemp2
wget --no-check-certificate -O "${TMPFILE2}" "${URL}&pag=2"  > /dev/null 2>&1
TMPFILE3=./temptemp3
wget --no-check-certificate -O "${TMPFILE3}" "${URL}&pag=3"  > /dev/null 2>&1
echo "Tá níos mó ná áit amháin in Éirinn a bhfuil an t-ainm '''${1}''' air:"
(cat "${TMPFILE}" | procone "${1}"; cat "${TMPFILE2}" | procone "${1}"; cat "${TMPFILE3}" | procone "${1}") | perl a2whelp.pl | sort
echo '== Tagairtí =='
echo '{{reflist}}'
echo
echo '{{idirdhealú}}'
echo
echo '[[Catagóir:Tíreolaíocht na hÉireann]]'
echo '[[Catagóir:Idirdhealáin]]'
rm -f "${TMPFILE}" "${TMPFILE2}" "${TMPFILE3}"
