#!/bin/bash
#  this ran in 30 minutes 2018-09-23

HERE=${HOME}/gaeilge/treocht
mkdir -p ${HERE}/aschur ${HERE}/corpas ${HERE}/freq ${HERE}/glan
cd ${HOME}/seal/irishcompleted/kildarestreet

# 2004-01 go 2017-12
echo "Adding Kildare Street stuff..."
find gaois -type f |
while read x
do
	THEDATE=`echo "${x}" | egrep -o '.{7}$'`
	cat "${x}" | egrep -v '^ainm =' >> ${HERE}/corpas/${THEDATE}
done

# 2014-10 ... lá atá inniu ann
cd ${HERE}
TUAIRISC=${HOME}/seal/irishcompleted/tuairisc.ie
echo "Adding Tuairisc.ie articles..."
find ${TUAIRISC} -name '???.html' | sort |
while read x
do
	DATA=`echo "${x}" | sed 's/^.*tuairisc.ie\///' | sed 's/\/.*$//'`
	(echo; echo; cat "${x}" | bash ${TUAIRISC}/cleaner.sh) >> corpas/$DATA
done

# 2010-03 go 2013-02
GAELSCEAL=${HOME}/gaeilge/diolaim/n/gaelsceal2
echo "Adding Gaelscéal articles..."
find ${GAELSCEAL} -name '??????' -type f | sort |
while read x
do
	DATA=`echo ${x} | egrep -o '[^/]+$' | sed 's/..$//' | sed 's/^/20/' | sed 's/\(..\)$/-\1/'`
	(echo; echo; cat "${x}") >> corpas/$DATA
done

# 2001-05 go 2014-09
CRUB=/usr/local/share/crubadan/ga
echo "Adding Beo articles..."
egrep 'http://www.beo.ie/alt-' ${CRUB}/MANIFEST | sed 's/^[^ ]* //' |
while read x
do
	DATA=`egrep '^EAGRÁN ' ${CRUB}/ciu/${x} | head -n 1 | sed 's/^EAGRÁN [0-9]* · //' | sed 's/^EANÁIR \(20[0-9][0-9]\) *$/\1-01/' | sed 's/^FEABHRA \(20[0-9][0-9]\) *$/\1-02/' | sed 's/^MÁRTA \(20[0-9][0-9]\) *$/\1-03/' | sed 's/^AIBREÁN \(20[0-9][0-9]\) *$/\1-04/' | sed 's/^BEALTAINE \(20[0-9][0-9]\) *$/\1-05/' | sed 's/^MEITHEAMH \(20[0-9][0-9]\) *$/\1-06/' | sed 's/^IÚIL \(20[0-9][0-9]\) *$/\1-07/' | sed 's/^LÚNASA \(20[0-9][0-9]\) *$/\1-08/' | sed 's/^MEÁN FÓMHAIR \(20[0-9][0-9]\) *$/\1-09/' | sed 's/^DEIREADH FÓMHAIR \(20[0-9][0-9]\) *$/\1-10/' | sed 's/^SAMHAIN \(20[0-9][0-9]\) *$/\1-11/' | sed 's/^NOLLAIG \(20[0-9][0-9]\) *$/\1-12/'`
	(echo; echo; cat ${CRUB}/ciu/${x}) >> corpas/$DATA
done

# 2003-02 go dtí an lá atá inniu ann (cúpla bearna i 2003, 2004)
echo "Adding blogspot.com blogs..."
find ${HOME}/gaeilge/crubadan/blogs/sonrai/ga/ -name '*.xml' | sort |
while read x
do
	perl appendfeed.pl "${x}"
done

# 2000-07, then 2006-11, 2006-12, 2007-01, then 2008-07 to present
echo "Adding all other RSS feeds (Nós, RTÉ, WordPress, Tumblr, ...)"
find ${HOME}/gaeilge/crubadan/rss/sonrai/ -name '*.xml' | sort |
egrep -v 'tuairisc.ie.xml' | egrep -v 'indigenoustweets.com.xml' |
while read x
do
	perl appendfeed.pl "${x}"
done

# 2007-04 go dtí an lá atá inniu ann
echo "Adding every Irish language tweet..."
cat ${HOME}/gaeilge/crubadan/twitter/sonrai/ga-tweets.txt | perl appendtweets.pl

# 2014-04 go 2017-05
echo "Adding stuff from public Facebook groups..."
cat ${HOME}/gaeilge/crubadan/fb/GA.txt | sort -k3,3 -n | perl appendfb.pl
