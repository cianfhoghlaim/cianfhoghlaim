#!/bin/bash
find corpas/ -name '????-??' | 
while read x
do
	FILENAME=`echo $x | sed 's/^corpas.//'`
	cat $x | abairti-dumb | tr "\000-\011" " " | tr "\013-\037" " " | egrep -v '.{500}' | egrep '.{20}' | sed "s/\([A-ZÁÉÍÓÚa-záéíóú]\)[’ʼ]\([A-ZÁÉÍÓÚa-záéíóú]\)/\1'\2/g" | sed "s/[‑‐−]/-/g" | sed 's/http[^ ]*//g' | (cd ${HOME}/seal/caighdean/model; perl gaeilgeamhain.pl) | sort -u | randomize > glan/${FILENAME}
done
