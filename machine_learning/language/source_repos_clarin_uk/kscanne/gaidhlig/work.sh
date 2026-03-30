#!/bin/bash
#cat ${HOME}/seal/caighdean/unknown-gd.txt | sed 's/^[0-9]* //' | egrep '....' | egrep -v '_' | head -n 500 | sort | egrep -v '^[A-La-l]' | sed '1,179d'|
showtodo gd2ga.po | egrep 'msgid' | sed '1d' | sed 's/^msgid "//' | sed 's/"$//' |
while read x
do
	echo
	echo
	echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
	echo "SEARCHING: $x"
	gd "$x"
done | more
