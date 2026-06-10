#!/bin/bash
HERE=`pwd`
CC=${HOME}/gaeilge/ga2gv/cc
cd ${HOME}/seal/idirlamha/en/kjv/parsed
ls | egrep -v '^sailm$' |
while read x
do
	echo "Parsing ${x}...."
	paste ${CC}/${x}-b ${CC}/${x} ${x} > ${HERE}/3way.txt
	(cd ${HERE}/..; cat bible/3way.txt | cut -f 1 | sed 's/^[0-9]*:[0-9]*: *//' | bash parse.sh) | perl ${HERE}/addtrans.pl "${x}" > ${HERE}/parsed/${x}.conllu
done
rm -f ${HERE}/3way.txt
