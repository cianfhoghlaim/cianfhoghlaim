#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash pseudolocale.sh XX"
	exit 1
fi
rm -Rf pseudo
mkdir pseudo
LOCALECODE=${1}
cat tiers.txt |
while read x
do
	FILENAME=`echo ${x} | sed 's/ .*//'`
	PATHTOFILE=`echo ${FILENAME} | sed 's/\/[^\/]*$//'`
	mkdir -p pseudo/${PATHTOFILE}
	TIER=`echo ${x} | egrep -o '[0-9]+$'`
	if [ ${TIER} -ne 5 ]
	then
		cat ${LOCALECODE}/${FILENAME} | sed "/^<!ENTITY [^ ]* \"[^0-9\"][^0-9\"][^0-9\"][^0-9\/]*$/s/ \"/ \"[T${TIER}]/" | sed "/^[^<# =][^<# =]* *=[^0-9][^0-9][^0-9][^0-9\/]*$/s/= */&[T${TIER}]/" > pseudo/${FILENAME}
	else
		cp -f ${LOCALECODE}/${FILENAME} pseudo/${FILENAME}
	fi
done
