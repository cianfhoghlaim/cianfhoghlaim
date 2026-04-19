GAEILGE=${HOME}/gaeilge
REPOS=${HOME}/seal
ROOTDIR=${HOME}/public_html
TMPFILE=`mktemp`
cat abhar.tsv | egrep -v '^#' | sed "s@{GAEILGE}@${GAEILGE}@g; s@{REPOS}@${REPOS}@g" |
while read x
do
	TEANGA=`echo "${x}" | cut -f 1`
	ACTIVE=`echo "${x}" | cut -f 2`
	SOURCE=`echo "${x}" | cut -f 3`
	TARGET=`echo "${x}" | cut -f 4`
	TITLE=`echo "${x}" | cut -f 5`
	CSS=`echo "${x}" | cut -f 6 | sed 's@\/@\\\/@g'`
	cp -f "${SOURCE}" "${TMPFILE}"
	if [ "${TEANGA}" = "en" ]
	then
		NAV="nav-en.html"
		AISTRIUCHAN=`echo "${TARGET}" | sed 's/-en\.html$/.html/'`
		# special case for Amhrán/Droichead; ensure English nav
		if echo "${TARGET}" | egrep '^(amhran|droichead)/' > /dev/null
		then
			cat "${SOURCE}" | sed 's/\.html/-en.html/' > ${TMPFILE}
		fi
	else
		NAV="nav.html"
		AISTRIUCHAN=`echo "${TARGET}" | sed 's/\.html$/-en.html/'`
	fi
	if [ ! -e "${SOURCE}" ]
	then
		echo "Error: source file ${SOURCE} not found..."
	else
		cat "${NAV}" | sed "s@AISTRIUCHAN@/${AISTRIUCHAN}@" | sed "s/active: false/active: ${ACTIVE}/" | sed "/^<div class=.content.>/r ${TMPFILE}" | sed "/^  <title>/s/.*/<title>${TITLE}<\/title>/" > ${ROOTDIR}/${TARGET}
		if [ ! "${CSS}" = "-" ]
		then
			sed -i "/<link.*cadhan.css/s/.*/&\n  <link rel=\"stylesheet\" href=\"\/${CSS}\">/" ${ROOTDIR}/${TARGET}
		fi
	fi
done
cp cadhan.css ${ROOTDIR}/css
cp dunaonghusa.png ${ROOTDIR}/pic
cp favicon.png ${ROOTDIR}/pic
cp by-sa-80x15.png ${ROOTDIR}/pic
cp Icon_External_Link.png ${ROOTDIR}/pic
sed -i '/<link.*favicon.png/s/.*/&\n  <script type="text\/javascript" src="https:\/\/www.gstatic.com\/charts\/loader.js"><\/script>/' ${ROOTDIR}/treochtai/*.html
rm -f $TMPFILE
