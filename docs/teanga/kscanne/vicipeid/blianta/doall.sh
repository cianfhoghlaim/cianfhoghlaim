#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash doall.sh [breith|bas]"
	exit 1
fi
tac years.txt | egrep -v ' RC' | egrep '^[12][0-9]{3}$' |
while read yr
do
	perl descr.pl "$yr" "${1}" | sort
	sleep 3
done
