#!/bin/bash
# pipe a list of Logainm numerical IDs through this
# It pings logainm.ie for correct English/Irish names
# and verifies those against what's in logainm.tsv, updating if nec.
TMPF=`mktemp`
while read x
do
	LAURL="https://www.logainm.ie/ga/${x}"
	wget -O "${TMPF}" "${LAURL}" > /dev/null 2>&1
	sed -i '1,/^<div class="highNames">/d' "${TMPF}"
	sed -i '/^<div class="/,$d' "${TMPF}"
	if cat "${TMPF}" | egrep '<div class="wording"><[^<>]* lang="ga"' > /dev/null
	then
		GAEILGE=`cat "${TMPF}" | tr -d "\015" | egrep '<div class="wording"><[^<>]* lang="ga"' | sed 's/<[^>]*>//g' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//'`
	else
		GAEILGE='-'
	fi
	if cat "${TMPF}" | egrep '<div class="wording"><[^<>]* lang="en"' > /dev/null
	then
		BEARLA=`cat "${TMPF}" | tr -d "\015" | egrep '<div class="wording"><[^<>]* lang="en"' | sed 's/<[^>]*>//g' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//'`
	else
		BEARLA='-'
	fi
	IRISHENGLISH="${GAEILGE}~${BEARLA}"
	LINENUA=`echo "$x~$IRISHENGLISH" | tr "~" "\t"`
	PATT=`echo "$x~$IRISHENGLISH" | sed 's/~/[[:space:]]/g' | tr "()" ".."`
	if [ "${IRISHENGLISH}" = "-~-" ]
	then
		echo "$x not found on logainm.ie (404)..."
	else
		if egrep "^${x}[[:space:]]" logainm.tsv > /dev/null
		then
			if egrep "^${PATT}$" logainm.tsv > /dev/null
			then
				echo "$x unchanged..."
			else
				echo "Replacing..."
				egrep "^${x}[[:space:]]" logainm.tsv
				echo "with..."
				echo "$LINENUA"
				sed -i "/^${x}\t/s/.*/$LINENUA/" logainm.tsv
			fi
		else
			echo "No previous value for $x... appending new one..."
			echo "$x~$IRISHENGLISH" | tr "~" "\t" >> logainm.tsv
		fi
	fi
	sleep 5
done
cat logainm.tsv | sort -k1,1 -n > ${TMPF}
mv -f ${TMPF} logainm.tsv
