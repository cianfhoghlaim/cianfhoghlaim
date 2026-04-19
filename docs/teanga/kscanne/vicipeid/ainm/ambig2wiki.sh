#!/bin/bash
if [ $# -ne 1 ]
then
	echo "Usage: bash ambig2wiki.sh SEARCHTERM"
	echo "Outputs wikitext that should be pastable into a new"
	echo "disambiguation page named 'Seán Ó Néill (idirdhealú)' or whatever"
	echo "Can specify search term as a regex, e.g.:"
	echo "bash ambig2wiki.sh \"M.ch..l ([A-Za-z]+ )?Ó Súilleabháin\""
	exit 1 
fi

# one arg is URL
get_title_wget() {
    TMPF=`mktemp`
    wget -O "${TMPF}" "${1}" > /dev/null 2>&1
    cat "${TMPF}" | tr -d "\n\015" | egrep -o '<title.*</title>' | head -n 1 | sed 's/<[^>]*>//g' | tr "\t" " " | sed 's/^ *//' | sed 's/ *$//' | sed 's/  */ /g' | de-entify | sed 's/|/{{!}}/g'
    rm -f "$TMPF"
}

# one arg is URL
get_title() {
    curl --silent "${1}&AspxAutoDetectCookieSupport=1" | egrep '^<title' | tr -d "\015" | sed 's/<[^>]*>//g' | de-entify | sed 's/|/{{!}}/g'
}


DATA=`date +%Y-%m-%d`
echo "Tá níos mó ná duine amháin darb ainm '''${1}''' ann:"
cat ${HOME}/gaeilge/canuinti/daoine.csv | egrep "^${1}( [0-9])?,.*[^?],[^,]+$" | cut -d ',' -f 1,4,5,10 | tr "," "\t" | sort -k2,2 -n |
while read x
do
	AINM=`echo "${x}" | cut -f 1 | sed 's/ [0-9]$//'`
	BORN=`echo "${x}" | cut -f 2`
	DIED=`echo "${x}" | cut -f 3`
	AINMID=`echo "${x}" | cut -f 4`
	TEIDEAL=`get_title_wget "https://www.ainm.ie/Bio.aspx?ID=${AINMID}"`
	echo '*' "[[${AINM} ()]] ([[${BORN}]]–[[${DIED}]]): scríbhneoir as Contae X<ref>{{Lua idirlín|url=https://www.ainm.ie/Bio.aspx?ID=${AINMID}|teideal=${TEIDEAL}|work=An Bunachar Náisiúnta Beathaisnéisí Gaeilge|dátarochtana=${DATA}}}</ref>"
done

echo
echo '== Tagairtí =='
echo '{{reflist}}'
echo
echo '{{idirdhealú}}'
