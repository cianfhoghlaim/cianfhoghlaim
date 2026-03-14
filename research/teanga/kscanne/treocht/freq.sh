#!/bin/bash

# filter; pipe in plain text
# compare ~/gaeilge/canuinti/buildtable.sh
makefreq() {
	bash ${HOME}/seal/caighdean/alltokens.sh | egrep "^([A-Za-z'-]+|#[A-Za-z0-9]+)$" | sed "s/^''*//; s/'*'$//" | demut | egrep -v "'" | tolow | egrep "[a-záéíóú]" | sort | uniq -c | sort -r -n | sed 's/^ *//'
}

find glan/ -name '????-??' | sort |
while read x
do
	FILENAME=`echo $x | sed 's/^glan.//'`
	cat $x | makefreq > freq/${FILENAME}
done
cat glan/????-?? | makefreq > freq.txt
