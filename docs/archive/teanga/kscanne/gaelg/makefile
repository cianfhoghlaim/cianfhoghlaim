INSTALL=/usr/bin/install
SHELL=/bin/sh
MAKE=/usr/bin/make
INSTALL_DATA=$(INSTALL) -m 444

add : FORCE
	cp -f focloir.txt focloir.txt.bak
	perl i.pl -f
	sort -t '_' -k1,1 -k2,2 focloir.txt > temp.txt
	mv -f temp.txt focloir.txt
	$(MAKE) gv2ga.po
	diff -u focloir.txt.bak focloir.txt | more
	echo "Problem redirects:"
	-cat focloir.txt | egrep '0$$' | sed 's/\t.*//' > hw-temp.txt
	-egrep -o '[^[:cntrl:]]+[^0]$$' focloir.txt | keepif -n hw-temp.txt
	-egrep '^[^_]+[0-9]_.*0$$' focloir.txt
	-rm -f hw-temp.txt

GV.txt : focloir.txt i.pl
	perl i.pl -g # writes "GV.txt"

GRAM=${HOME}/gaeilge/gramadoir/gr
GA.txt : /home/kps/math/code/data/Dictionary/IG
	Gin 18 # writes "ga.txt"
	cat ga.txt | perl -p $(GRAM)/ga/posmap.pl | LC_ALL=C sed '/^xx /s/.*/xx 4/' | iconv -f iso-8859-1 -t utf8 > $@
	rm -f ga.txt

gv2ga.pot : focloir.txt
	(echo 'msgid ""'; echo 'msgstr ""'; echo '"Content-Type: text/plain; charset=UTF-8\\n"'; echo) > $@
	cat focloir.txt | egrep '0 *$$' | sed 's/^\([^_]*_[^ \t]*\).*/msgid "\1"\nmsgstr ""\n/' >> $@
	#cat focloir.txt | egrep '0 *$$' | egrep -v '^[^_]+ ' | sed 's/^\([^_]*_[^ \t]*\).*/msgid "\1"\nmsgstr ""\n/' >> $@

gv2ga.po : gv2ga.pot
	msgmerge --no-wrap -N -q --backup=off -U $@ gv2ga.pot > /dev/null 2>&1
	touch $@

leabhar.pdf: sonrai.tex leabhar.tex
	pdflatex leabhar.tex

sonrai.xml: sonrai.tex tex2xml.sh
	cat sonrai.tex | bash tex2xml.sh > $@

sonrai.tex: tolatex.pl gv2ga.po focloir.txt stemfreq.txt stemfreq-nua.txt
	perl tolatex.pl > $@

# makes "multi-gv.txt" too
# Important to include immutable.txt since it helps evaluate coverage
# of gv2ga; those proper names, English words will now be considered "covered"
# note that the first line below (perl i.pl -s) writes pairs-gv.txt
# and the lines after that tweak it in various ways, and create multi-gv
GIT=${HOME}/seal/caighdean
pairs-gv.txt: gv2ga.po focloir.txt GA.txt i.pl makefile ${HOME}/seal/idirlamha/gv/freq/immutable.txt
	perl i.pl -s
	sed -i '/ xx$$/d; /^xx\?[ _]/d' $@
	sed -i "/ b'/d" $@  # not generating b' forms at all on gv side...
	sed -i "/^dt'[^ ][^ ]* [BCDFGMPTbcdfgmpt][^h']/s/^dt'\([^ ]*\) \(.\)\(.*\)/dt'\1 do \2h\3/" $@
	sed -i "/^dt'[^ ]* [Ss][aeiouáéíóúlnr]/s/^dt'\([^ ]*\) \(.\)\(.*\)/dt'\1 do \2h\3/" $@
	sed -i "/^dt'[^ ]* [HLNRVhlnqrv]/s/^dt'\([^ ]*\) \(.*\)/dt'\1 do \2/" $@
	sed -i "/^dt'[^ ]* [Ss][^haeiouáéíóúlnr]/s/^dt'\([^ ]*\) \(.*\)/dt'\1 do \2/" $@
	sed -i "/^m'[^ ][^ ]* [BCDFGMPTbcdfgmpt][^h']/s/^m'\([^ ]*\) \(.\)\(.*\)/m'\1 mo \2h\3/" $@
	sed -i "/^m'[^ ]* [Ss][aeiouáéíóúlnr]/s/^m'\([^ ]*\) \(.\)\(.*\)/m'\1 mo \2h\3/" $@
	sed -i "/^m'[^ ]* [HLNRVhlnqrv]/s/^m'\([^ ]*\) \(.*\)/m'\1 mo \2/" $@
	sed -i "/^m'[^ ]* [Ss][^haeiouáéíóúlnr]/s/^m'\([^ ]*\) \(.*\)/m'\1 mo \2/" $@
	sed -i "/ym .*idh$$/s/$$/ mé/; /^[hj]em .*idh$$/s/$$/ mé/" $@
	sed "/^.[^'][^ ]* m'/s/^/my_/" $@ | perl leniter.pl > temp.txt
	mv -f temp.txt $@
	cat gv2ga.po | sed '/^#/d' | sed '/msgid/s/ \([^"]\)/_\1/g' | tr -d "\n" | sed 's/msgid/\n&/g' | sed '1d' | egrep -v 'msgstr ""' | sed 's/^msgid "//' | sed 's/"msgstr "/ /' | sed 's/"$$//' | bash split.sh | LC_ALL=C sort -k1,1 > po-temp-proc.txt
	(cat $@; cat po-temp-proc.txt | sed 's/[0-9]*_[a-z][a-z]* / /' | sed 's/_[a-z][a-z]*$$//' | sed 's/[0-9]*$$//'; egrep '[^0]$$' focloir.txt | sed 's/^\([^\t]*\)\t*[^\t]*\t*[^\t]*\t\([^\t]*\)$$/\1~\2/' | sed 's/ /_/g' | sed 's/~/ /' | LC_ALL=C sort -k2,2 | LC_ALL=C join -1 2 -2 1 - po-temp-proc.txt | sed 's/^[^ ]* //' | sed 's/[0-9]*_[a-z][a-z]* / /' | sed 's/[0-9]*_[a-z][a-z]*$$//'; cat ${HOME}/seal/idirlamha/gv/freq/immutable.txt | sed 's/.*/& &/') | LC_ALL=C sort -u | LC_ALL=C sort -k1,1 > temp.txt
	cat temp.txt | egrep -v '_' > $@
	if ! diff -q $@ $(GIT)/$@; then cp -f $@ $(GIT); fi
	(cat $(GIT)/multi-gv.txt; cat temp.txt | egrep '_') | LC_ALL=C sort -u | LC_ALL=C sort -k1,1 > multi-gv.txt
	if ! diff -q multi-gv.txt $(GIT)/multi-gv.txt; then cp -f multi-gv.txt $(GIT); fi
	rm -f po-temp-proc.txt temp.txt

all-gv.txt: GV.txt
	cat GV.txt | egrep -v '^xx ' | egrep -v -- '^-$$' | sed 's/ [0-9]*$$//' | sed "/^d'/s/^d'\(.*\)/dh'\1\n&/" | LC_ALL=C sort -u > $@

juststem-gv.txt: GV.txt
	cat GV.txt | sed 's/ [0-9]*$$//' | tr '\n' '@' | sed 's/-@/\n/g' | egrep -v '^xx' | perl -p -e 'chomp; ($$hd) = /([^@]+)/; s/@/ $$hd\n/g' | egrep -v '^x[ x]' | egrep -v ' .* ' | sort -u > $@

stemfreq.txt: stemfreq.pl juststem-gv.txt ${HOME}/seal/idirlamha/gv/freq/freq.txt
	perl stemfreq.pl ${HOME}/seal/idirlamha/gv/freq/freq.txt juststem-gv.txt > $@

# juststem-gv.txt doesn't really give what we want for gv (e.g. "feh", etc.
# get inflated counts...) so don't use it, and instead maintain the file
# freqstems.txt with the top 1000 stems
stemfreq-nua.txt: stemfreq.pl freqstems.txt ${HOME}/seal/idirlamha/gv/freq/freq-nua.txt
	perl stemfreq.pl ${HOME}/seal/idirlamha/gv/freq/freq-nua.txt freqstems.txt > $@

er-vn-cands.txt: GV.txt
	cat GV.txt | tr "\n" "~" | sed 's/~-~/\n&/g' | egrep "^~-~[^ ]+ 200~" | egrep -o '[^~ 0-9]+ [0-9][0-9]~' | sed 's/ .*//' | sort -u | sed 's/^/er /' > $@

clean :
	rm -f GA.txt GV.txt *.bak *.pot messages.mo lookup.txt cuardach.txt lexicon-gv.txt ambig.txt fullstem.txt fullstem-gv.txt fullstem-nomutate*.txt speling*.txt apertium-toinsert.txt apertium-ga-gv.ga.dix torthai-nua.txt all-gv.txt pairs-gv.txt multi-gv.txt replacements.txt searchable.txt tempdic leabhar.pdf leabhar.aux leabhar.log leabhar.out juststem-gv.txt sonrai.tex stemfreq.txt stemfreq-nua.txt sonrai.xml

distclean :
	$(MAKE) clean

FORCE :
