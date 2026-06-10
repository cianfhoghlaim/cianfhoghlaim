#!/bin/bash

# 1st arg is opp-pl, opp-py, opp-c, etc.
# 2nd arg is the .opp file to test
# 3nd arg is the correct answer string
testone() {
	COMPUTED="`./${1} ${2}`"
	if [ "${COMPUTED}" != "${3}" ]
	then
		echo "Error: ${2} with ${1}; got ${COMPUTED}, expected ${3}"
	fi
}

ANS="0 5040 0 0 0"
testone opp-pl factorial.opp "${ANS}"
testone opp-py factorial.opp "${ANS}"
testone opp-c factorial.opp "${ANS}"
ANS="0 9 0 0 0"
testone opp-pl fourplusfive.opp "${ANS}"
testone opp-py fourplusfive.opp "${ANS}"
testone opp-c fourplusfive.opp "${ANS}"
ANS="0 18 0 3 3"
testone opp-pl threetimessix.opp "${ANS}"
testone opp-py threetimessix.opp "${ANS}"
testone opp-c threetimessix.opp "${ANS}"
