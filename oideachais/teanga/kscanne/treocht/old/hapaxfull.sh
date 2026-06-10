#!/bin/bash
find glan/ -name '????-??' | sort |
while read x
do
	DATA=`echo "$x" | sed 's/^glan.//'`
	cat "${x}" | bash ${HOME}/seal/caighdean/alltokens.sh | egrep '^[A-Za-z0-9-]+$' | sort -u | demut | sed "s/^/${DATA}\t/"
done | LC_ALL=C sort -k2,2 -k1,1 | uniq -f 1 | sed 's/^\(.*\)\t\(.*\)$/\2\t\1/'
