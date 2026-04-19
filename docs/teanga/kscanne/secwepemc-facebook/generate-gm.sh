#!/bin/bash
#  Copyright 2012 Kevin Scannell
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

TEMPFILE=`mktemp /tmp/tmp.XXXXXXXXXX`
cat LINGUAS | tr "\t" "~" |
while read x
do
	LANGCODE=`echo $x | sed 's/~.*//'`
	POFILECODE=`echo ${LANGCODE} | sed 's/-x-en$//'`
	AMBIENTLANG=`echo $x | sed 's/^[^~]*~//' | sed 's/~.*//'`
	ENGLISHNAME=`echo $x | sed 's/^[^~]*~[^~]*~//' | sed 's/~.*//'`
	VERSION=`echo $x | sed 's/^.*~\([^~]*\)~[^~]*~[^~]*$/\1/'`
	TRANSLATORS=`echo $x | sed 's/^.*~\([^~]*\)$/\1/'`
	echo "Generating greasemonkey for ${LANGCODE} (using po/${POFILECODE}.po)..."
	perl po2gm.pl ${POFILECODE} ${AMBIENTLANG} > ${TEMPFILE}
	sed "/Translations go here/r ${TEMPFILE}" template.user.js | sed "s/!TEANGA!/${LANGCODE}/" | sed "s/!DATA!/`date +%Y-%m-%d`/" | sed "s/!LEAGAN!/${VERSION}/" | sed "s/!ENGLISHNAME!/${ENGLISHNAME}/" | sed "s/!TRANSLATORS!/${TRANSLATORS}/" > facebook-${LANGCODE}.user.js
	rm -Rf facebook-${LANGCODE}
	mkdir facebook-${LANGCODE}
	cat template.json | sed "s/!TEANGA!/${LANGCODE}/" | sed "s/!LEAGAN!/${VERSION}/" | sed "s/!ENGLISHNAME!/${ENGLISHNAME}/" > facebook-${LANGCODE}/manifest.json
	cp images/icon*.png facebook-${LANGCODE}
	cp facebook-${LANGCODE}.user.js facebook-${LANGCODE}
	zip -r facebook-${LANGCODE}.zip facebook-${LANGCODE}
	rm -f ${LANGCODE}-temp.js
	rm -Rf facebook-${LANGCODE}
done
rm -f ${TEMPFILE}
