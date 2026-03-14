#!/bin/bash
TMPFILE=`mktemp`
cat droichead.tsv | cut -f 2,3,4,5 | sort -k1,1 > $TMPFILE
mkdir -p dist
egrep '^[AaÁá]' $TMPFILE | perl tsv2html.pl > dist/A-data.html
egrep '^[Bb]' $TMPFILE | perl tsv2html.pl > dist/B-data.html
egrep '^[Cc]' $TMPFILE | perl tsv2html.pl > dist/C-data.html
egrep '^-?[Dd]' $TMPFILE | perl tsv2html.pl > dist/D-data.html
egrep '^[EeÉé]' $TMPFILE | perl tsv2html.pl > dist/E-data.html
egrep '^[Ff]' $TMPFILE | perl tsv2html.pl > dist/F-data.html
egrep '^[Gg]' $TMPFILE | perl tsv2html.pl > dist/G-data.html
egrep '^[Hh]' $TMPFILE | perl tsv2html.pl > dist/H-data.html
egrep '^[IiÍí]' $TMPFILE | perl tsv2html.pl > dist/I-data.html
egrep '^[Ll]' $TMPFILE | perl tsv2html.pl > dist/L-data.html
egrep '^[Mm]' $TMPFILE | perl tsv2html.pl > dist/M-data.html
egrep '^-?[Nn]' $TMPFILE | perl tsv2html.pl > dist/N-data.html
egrep '^[OoÓó]' $TMPFILE | perl tsv2html.pl > dist/O-data.html
egrep '^[Pp]' $TMPFILE | perl tsv2html.pl > dist/P-data.html
egrep '^[Rr]' $TMPFILE | perl tsv2html.pl > dist/R-data.html
egrep '^-?[Ss]' $TMPFILE | perl tsv2html.pl > dist/S-data.html
egrep '^[Tt]' $TMPFILE | perl tsv2html.pl > dist/T-data.html
egrep '^[UuÚú]' $TMPFILE | perl tsv2html.pl > dist/U-data.html
egrep '^[Vv]' $TMPFILE | perl tsv2html.pl > dist/V-data.html
rm -f $TMPFILE
