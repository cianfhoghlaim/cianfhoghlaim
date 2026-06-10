#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash buildpot.sh xx"
	exit 1
fi
TEANGA="${1}"
rm -f facebook.pot
sed "s/XXXX-XX-XX XX:XX-XXXX/`date '+%Y-%m-%d %H:%M:%S%z' | sed 's/00$$/:00/'`/" header.pot > facebook.pot
cat strings.txt | sed '/^[^#]/{s/"/\\"/g; s/.*/msgid "&"\nmsgstr ""\n/}' | sed '/^msgid ".*;.*%d/{N; s/^\([^;]*\);\([^"]*\)"\n.*/\1"\nmsgid_plural "\2"\nmsgstr[0] ""\nmsgstr[1] ""/}' >> facebook.pot
egrep "^${TEANGA}[^a-z-]" contexts.txt | sed "s/^${TEANGA}.//" | tr "\t" "~" |
while read x
do
	MSGID=`echo $x | sed "s/~.*//"`
	MSGCTXT=`echo $x | sed "s/^.*~//"`
	sed -i "/^#\./{N; s/^\(.*\)\n\(msgid \"$MSGID\"\)/&\nmsgstr \"\"\n\n\1\nmsgctxt \"$MSGCTXT\"\n\2/}" facebook.pot
done
