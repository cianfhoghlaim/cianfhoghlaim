#!/bin/bash
TMPOK=`mktemp`
if [ ${HOME}/math/code/data/Dictionary/IG -nt ${HOME}/seal/ig7 ]
then
	echo "Rebuilding seal/ig7..."
	(cd ${HOME}/seal; ${HOME}/clar/denartha/Gin 17; utf ig7)
fi
cat ${HOME}/seal/ig7 | sed 's/ *\[.*//' | egrep -v '^[^.]+ ' | sed 's/ *(.*//' | sed 's/[0-9]$//' | sed 's/nf$/nm/; s/nb$/nf/; s/pron$/pn/; s/\.$/. u/' | sed 's/\. /_/' > $TMPOK
egrep '^msgstr "[^"]' gv2ga.po | sed 's/^msgstr "//' | sed 's/"$//' | tr ';' '\n' | sed 's/[0-9]_/_/' | sed 's/_vcop/_v/; s/_aindec/_a/' | egrep -v ' ' | egrep '_' | keepif -n $TMPOK | sort -u
rm -f $TMPOK
