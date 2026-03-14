#!/bin/bash
#
# This script is ONLY to deploy the HTML/CSS/JS files for a new language
# (or update those files when they change). The database of puzzles for
# each language is built separately, in this directory, using the makefile
# (cf make puzzles-xx.json, etc.)
#
if [ $# -ne 1 ]
then
	echo "Usage: bash deploy.sh (ga|gd|...)"
	exit 1
fi

# one arg is language code
# acts as a simple filter on both .js and .html
localize() {
	if [ "${1}" = "ga" ]
	then
		sed "
s/CONGRATS/D'aimsigh tú gach uile fhocal! Comhghairdeas!/
s/NAMEOFGAME/Cíor Thuathail/
s/TOOSHORT/Róghearr/
s/GOODMSG/Maith thú!/
s/GREATMSG/Iontach!/
s/AMAZINGMSG/Dochreidte!/
s/PANGRAMMSG/Gach litir in aon iarraidh amháin!/
s/ALREADYFOUND/D'úsáid tú an focal seo cheana/
s/INVALIDWORD/Focal neamhbhailí/
s/MISSINGCENTER/Níl an litir sa lár ann/
s/ENTERBUTTON/Cuir isteach/
s/DELETEBUTTON/Scrios litir/
s/NUMFOUND/Líon focal:/
s/SCOREMSG/Scór iomlán:/
s/DISCOVEREDWORDS/Liosta focal/
s/YESTERDAYS/Na focail ón lá inné/
s/RETURNHOME/<< Abhaile/
"
	elif [ "${1}" = "en" ]
	then
		sed "
s/CONGRATS/You have found all of the possible words! Thanks for playing/
s/NAMEOFGAME/Spelling Bee Game/
s/TOOSHORT/Too Short/
s/GOODMSG/Good!/
s/GREATMSG/Great!/
s/AMAZINGMSG/Amazing!/
s/PANGRAMMSG/Pangram!/
s/ALREADYFOUND/Already Found/
s/INVALIDWORD/Invalid Word/
s/MISSINGCENTER/Missing Center Letter/
s/ENTERBUTTON/Enter/
s/DELETEBUTTON/Delete/
s/NUMFOUND/Number of words:/
s/SCOREMSG/Score:/
s/DISCOVEREDWORDS/Words Discovered/
s/YESTERDAYS/Yesterday's Words/
s/RETURNHOME/<< Home/
"
	elif [ "${1}" = "gd" ]
	then
		sed "
s/CONGRATS/Lorg thu gach facal a tha ri lorg an-diugh! Mòran taing airson cluich/
s/NAMEOFGAME/Cìr-ogham/
s/TOOSHORT/Ro ghoirid/
s/GOODMSG/Math!/
s/GREATMSG/Glè mhath!/
s/AMAZINGMSG/Air leth!/
s/PANGRAMMSG/Gach litir aon turas!/
s/ALREADYFOUND/Lorg thu seo roimhe/
s/INVALIDWORD/Chan eil am facal seo dligheach/
s/MISSINGCENTER/Tha an litir sa mheadhan a dhìth/
s/ENTERBUTTON/A-steach/
s/DELETEBUTTON/Sguab às litir/
s/NUMFOUND/Cò mheud facal:/
s/SCOREMSG/An sgòr:/
s/DISCOVEREDWORDS/Na faclan a lorg thu/
s/YESTERDAYS/Na faclan on dè/
s/RETURNHOME/<< Dhachaigh/
"
	fi
}

TEANGA="${1}"
SPRIOC=${HOME}/public_html/beach
mkdir -p ${SPRIOC}/css
cp -f spelling_bee.css ${SPRIOC}/css
mkdir -p ${SPRIOC}/${TEANGA}
cp -f shuffle_icon.png ${SPRIOC}/${TEANGA}
rm -f ${SPRIOC}/${TEANGA}/spelling_bee.js
cat spelling_bee.js | sed "s/=TEANGA/=${TEANGA}/" | localize "${TEANGA}" > ${SPRIOC}/${TEANGA}/spelling_bee.js
rm -f ${SPRIOC}/${TEANGA}/index.html
cat template.html | sed "s/TEANGA/${TEANGA}/" | localize "${TEANGA}" > ${SPRIOC}/${TEANGA}/index.html
rm -f ${SPRIOC}/${TEANGA}/solutions.html
cat solutions.html | sed "s/TEANGA/${TEANGA}/" | localize "${TEANGA}" > ${SPRIOC}/${TEANGA}/solutions.html
chmod 444 ${SPRIOC}/css/spelling_bee.css ${SPRIOC}/${TEANGA}/spelling_bee.js ${SPRIOC}/${TEANGA}/*.html

# p2cadhan suffices since everything is under public_html
p2cadhan
