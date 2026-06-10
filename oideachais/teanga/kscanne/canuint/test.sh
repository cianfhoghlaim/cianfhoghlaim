#!/bin/bash
# this only works for kscanne

# one arg is twitter username
get_dialect() {
	bash ${HOME}/gaeilge/crubadan/twitter/twby ga "${1}" | cut -f 3 | egrep -v 'RT' | shuf | head -n 100 | bash canuint.sh
}

# first arg is twitter username, second arg is "C", "M", "U", or "N"
test_one() {
	FREAGRA=`get_dialect "${1}"`
	if [ "${FREAGRA}" != "${2}" ]
	then
		echo "Expected ${1} to be dialect ${2}, got ${FREAGRA}"
	fi
}

test_one Suilleabhanach M
test_one Marion508 C
test_one HMFerry U
