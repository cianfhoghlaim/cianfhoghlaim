#!/bin/bash
showtodo gv2ga.po | egrep 'msgid' | sed '1d' | sed 's/^msgid "//' | sed 's/"$//' |
while read x
do
	echo
	echo
	echo "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
	echo "SEARCHING: $x"
	gv "$x"
done | more
