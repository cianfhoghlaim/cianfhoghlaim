#!/bin/bash
while read x
do
	GD=`echo $x | sed 's/ .*//'`
	GA=`echo $x | sed 's/^[^ ]* //'`
	echo "$GA" | sed 's/;/\n/g' |
	while read y
	do	
		echo "$GD $y"
	done
done
