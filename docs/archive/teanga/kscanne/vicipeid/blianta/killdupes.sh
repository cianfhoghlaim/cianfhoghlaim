#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash doall.sh [breith.tsv|bas.tsv]"
	exit 1
fi
cat "${1}" | cut -f 2 | sort | uniq -c | sort -r -n | egrep -v '^ *1 ' | sed 's/^ *[0-9]* //' > qids2kill.txt 
cat qids2kill.txt |
while read x
do
	sed -i "/\t${x}\t/d" "${1}"
done
echo "Killed" `cat qids2kill.txt | wc -l` "QIDs with multiple dates"
rm -f qids2kill.txt
