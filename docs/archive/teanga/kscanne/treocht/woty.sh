#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash woty.sh 2017"
	exit 1
fi

# filter that generates a frequency list
tofreq() {
	bash ${HOME}/seal/caighdean/alltokens.sh | sed "s/^'*//" | sed "s/'*$//" | egrep "^[A-Za-z'-]+$" | demut | sort | uniq -c | sort -r -n | sed 's/^ *//'
}

# note kills everything with freq < 10...
find glan -name "${1}-??" | xargs cat | tofreq | egrep -v '^[0-9] ' > "${1}-freq.txt" 
# note that if we run this for, say, 2017 in 2019, it will now
# correctly only include through 2016 in the "prefreq" data!
find glan -name "????-??" | sort | sed "/${1}/,\$d" | xargs cat | tofreq > "${1}-prefreq.txt"
# can also remove low freq words from 20xx-freq.txt and rerun bayes.pl
# to get better candidates; also worth filtering out capitals?
echo "0 xx" | bayes.pl -d "${1}-freq.txt" "${1}-prefreq.txt" > "${1}-innovations.txt"
