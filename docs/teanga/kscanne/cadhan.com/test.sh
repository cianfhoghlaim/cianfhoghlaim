#!/bin/bash

# one arg is the error message
# pipe the erroneous lines through here
testout() {
    sed "s@^@Error (${1}): @"
}

TMPFILE=`mktemp`
cd ${HOME}/public_html
find . -name '*.html' | egrep -v '/amhran/' | egrep -v '/gramadoir/manual/' |
while read x
do
	cat "${x}" | sed '/^<pre>/,/^<\/pre>/d' | sed '/^<samp>/,/^<\/samp>/d' | sed 's/<i>-<\/i>//g; s/<td>-<\/td>//g' | vilistextum --charset=utf-8 --output-utf-8 - ${TMPFILE} > /dev/null 2>&1
	egrep '"' ${TMPFILE} | testout "unwanted ascii quote in ${x}"
	egrep ' -( |$)' ${TMPFILE} | testout "hyphen maybe should be em-dash in ${x}"
done
rm -f ${TMPFILE}
