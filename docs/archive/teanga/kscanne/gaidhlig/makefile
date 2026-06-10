INSTALL=/usr/bin/install
SHELL=/bin/sh
MAKE=/usr/bin/make
INSTALL_DATA=$(INSTALL) -m 444
GRAM=${HOME}/gaeilge/gramadoir/gr
STEMMER=${HOME}/gaeilge/ga2gd/Lingua-GA-Stemmer

all : cuardach.txt aistrigh ga2gd rialacha.txt disambig.pl ambig.txt gdfixer apertium-ga-gd.ga.dix

# Note "caighdean" package installed separately
# The dependencies listed here, plus disambig/*.dat, a README, Copyright, etc.
# are all that is needed for a ga2gd tarball
install : all
	$(INSTALL) aistrigh /usr/local/bin
	$(INSTALL) ga2gd /usr/local/bin
	$(INSTALL) gdfixer /usr/local/bin
	$(INSTALL) disambig.pl /usr/local/bin
	$(INSTALL_DATA) cuardach.txt /usr/local/share/ga2gd
	$(INSTALL_DATA) rialacha.txt /usr/local/share/ga2gd
	$(INSTALL_DATA) ambig.txt /usr/local/share/ga2gd
	rm -f /usr/local/share/ga2gd/disambig/*.dat
	cp -f ../traenail/*.dat /usr/local/share/ga2gd/disambig
	chmod 444 /usr/local/share/ga2gd/disambig/*.dat

add : FORCE
	cp -f focloir.txt focloir.txt.bak
	perl i.pl -f
	sort -t '_' -k1,1 -k2,2 focloir.txt > temp.txt
	mv -f temp.txt focloir.txt
	$(MAKE) gd2ga.po
	diff -u focloir.txt.bak focloir.txt | more
	echo "Problem redirects:"
	-cat focloir.txt | egrep '0$$' | sed 's/\t.*//' > hw-temp.txt
	-egrep -o '[^[:cntrl:]]+[^0]$$' focloir.txt | keepif -n hw-temp.txt
	-egrep '^[^_]+[0-9]_.*0$$' focloir.txt
	-rm -f hw-temp.txt

replacements.txt:
	cat ga2gd.po | tr -d "\n" | sed 's/msgid/\n&/g' | sed 's/^[^>]*>//' | sed 's/#.*//' | egrep -v 'msgstr ""' | sed 's/<\/.>"msgstr / /' | sed 's/_[a-z]*"/"/' | sed 's/^\([^ ]*\) "\([^"]*\)"$$/^\2^ \1/' | perl ${HOME}/seal/scanadh/get_repls.pl | LC_ALL=C sort | LC_ALL=C uniq -c | LC_ALL=C sort -r -n > $@

GD.txt : focloir.txt i.pl
	perl i.pl -g # writes "GD.txt"

lexicon-gd.txt : GD.txt
	cat GD.txt | sed '/^-$$/d' | LC_COLLATE=POSIX sort -u -k1,1 -k2,2n > $@
#	rest of the commands below are just informational - how much more of lextodo.txt is left?
	mv -f lextodo.txt lextodo.txt.bak
	cat lextodo.txt.bak | while read x; do TEMP=`echo $$x | sed 's/^\([^ ]*\) .*/^\1 /'`; if ! egrep "$$TEMP" lexicon-gd.txt > /dev/null; then echo $$x; fi; done > lextodo.txt
	diff -u lextodo.txt.bak lextodo.txt | more
	cat $@ | iconv -f utf8 -t iso-8859-1 > $(GRAM)/gd/$@
	(cd $(GRAM)/gd; make rebuildlex)

leabhar.pdf: sonrai.tex leabhar.tex
	pdflatex leabhar.tex
	cp $@ ${HOME}/public_html/pub/gd2ga.pdf

falsefriends.txt: sonrai.tex
	cat sonrai.tex | tr -d "\n" | sed 's/\\noindent/\n&/g' | egrep dbend | sed 's/\\setlen.*//' | sed 's/^.*hypertarget{[^}]*}//' | sed 's/^{.textbf.//' | sed 's/}}, *\\textit{/ /' | sed 's/}:/:/' | sed 's/\\markboth{[^}]*}{[^}]*}/ /' > $@

doileir.txt: sonrai.tex
	cat sonrai.tex | tr -d "\n" | sed 's/\\setlength/\n/g' | egrep bigstar | sed 's/^.*textbf{//' | sed 's/\\markboth{.*}//' | sed 's/}}, *\\textit{.*}:/: /' > $@

sonrai.tex: tolatex.pl gd2ga.po focloir.txt stemfreq.txt
	perl tolatex.pl > $@

sonrai.xml: sonrai.tex
	echo '<?xml version="1.0" encoding="UTF-8"?><text><body>' > $@
	cat sonrai.tex | egrep -v '^\\(setlength|markboth)' | egrep '[a-z]' | sed 's/^\\noindent//' | egrep -v '\\(addcontent|chapter)' | sed 's/^\\textdbend\\textdagger/\\textdagger/' | sed '/^[^\/$$]/s/\([^,.]*\)[,.] */<sense><cit type="translation" xml:lang="ga"><quote>\1<\/quote><\/cit><\/sense>/g' | sed 's/<\/sense>$$/&\n<\/entry>/' | sed '/^\$$\\rightarrow/s/^\$$\\rightarrow\$$ \\hyperlink{\([^}]*\)}.*/<xr><ptr target="#\1"\/><\/xr>\n<\/entry>/' | sed 's/^\\hypertarget{\([^}]*\)}{\\textbf{\([^}]*\)}}, \\textit{\([^}]*\)}: */<entry xml:id="\1">\n<form><orth>\2<\/orth><\/form><gramGrp><pos>\3<\/pos><\/gramGrp>/' | sed 's/^\\hypertarget{\([^}]*\)}{\\textbf{\([^}]*\)}}$$/<entry xml:id="\1">\n<form><orth>\2<\/orth><\/form>/' | sed 's/^\\textbf{\([^}]*\)}, \\textit{\([^}]*\)}$$/<entry>\n<form><orth>\1<\/orth><\/form><gramGrp><pos>\2<\/pos><\/gramGrp>/' | sed 's/^\\textdagger\\hypertarget{\([^}]*\)}{\\textbf{\([^}]*\)}}, \\textit{\([^}]*\)}: */<entry xml:id="\1">\n<form><orth>\2<\/orth><\/form><gramGrp><pos>\3<\/pos><\/gramGrp><lbl>annamh<\/lbl>/' | sed 's/^\$$\\bigstar\$$\\hypertarget{\([^}]*\)}{\\textbf{\([^}]*\)}}, \\textit{\([^}]*\)}: */<entry xml:id="\1">\n<form><orth>\2<\/orth><\/form><gramGrp><pos>\3<\/pos><\/gramGrp><lbl>doiléir<\/lbl>/' | sed 's/^\\textdbend\\hypertarget{\([^}]*\)}{\\textbf{\([^}]*\)}}, \\textit{\([^}]*\)}: */<entry xml:id="\1">\n<form><orth>\2<\/orth><\/form><gramGrp><pos>\3<\/pos><\/gramGrp><lbl>bréagchara<\/lbl>/' | sed 's/^\\textbf{\([^}]*\)}$$/<entry>\n<form><orth>\1<\/orth><\/form>/' >> $@
	echo '</body></text>' >> $@

# generated from gramadoir file, but keep it in version control here
posmap-local.pl: $(GRAM)/ga/posmap.pl
	cat $(GRAM)/ga/posmap.pl | LC_ALL=C sed '/now fix some to 127/,$$s/^s\/.* 127/#&/' > $@

GA.txt : /home/kps/math/code/data/Dictionary/IG posmap-local.pl
	Gin 18 # writes "ga.txt"
	cat ga.txt | perl -p posmap-local.pl | LC_ALL=C sed '/^xx /s/.*/xx 4/' | iconv -f iso-8859-1 -t utf8 > $@
	rm -f ga.txt

gd2ga.pot : focloir.txt
	(echo 'msgid ""'; echo 'msgstr ""'; echo '"Content-Type: text/plain; charset=UTF-8\\n"'; echo) > $@
	cat focloir.txt | egrep '0 *$$' | sed 's/^\([^_]*_[^ \t]*\).*/msgid "\1"\nmsgstr ""\n/' >> $@
	#cat focloir.txt | egrep '0 *$$' | egrep -v '^[^_]+ ' | sed 's/^\([^_]*_[^ \t]*\).*/msgid "\1"\nmsgstr ""\n/' >> $@

ga2gd.pot : GA.txt
	(echo 'msgid ""'; echo 'msgstr ""'; echo '"Content-Type: text/plain; charset=UTF-8\\n"'; echo) > $@
	cat GA.txt | tr '\n' '@' | sed 's/-@/\n/g' | sed 's/@.*//' | egrep -v '^xx' | sort -k1,1 -k2,2n | uniq | perl ./tagcvt.pl ga | tr '"' "'" | LC_ALL=C sed 's/.*/msgid "&"\nmsgstr ""\n/' >> $@

gd2ga.po : gd2ga.pot
	msgmerge -N -q --backup=off -U $@ gd2ga.pot > /dev/null 2>&1
	touch $@

neamhrialta.pot : GA.txt
	(echo 'msgid ""'; echo 'msgstr ""'; echo '"Content-Type: text/plain; charset=UTF-8\\n"'; echo) > $@
	cat GA.txt | tr '\n' '@' | sed 's/-@/\n/g' | egrep '^xx ' | tr '@' '\n' | egrep -v '^xx ' | egrep ' ' | sort -k1,1 -k2,2n | uniq | perl ./tagcvt.pl ga | tr '"' "'" | sed 's/.*/msgid "&"\nmsgstr ""\n/' >> $@

FOINSE=$(GRAM)/ga/comhshuite-ga.in
comhshuite.pot : $(FOINSE)
	(echo 'msgid ""'; echo 'msgstr ""'; echo '"Content-Type: text/plain; charset=UTF-8\\n"'; echo) > $@
	cat $(FOINSE) | iconv -f iso-8859-1 -t utf8 | perl ./saorog.pl | tr '"' "'" | LC_ALL=C sed 's/.*/msgid "&"\nmsgstr ""\n/' >> $@ 

ga2gd.po : ga2gd.pot
	msgmerge -N -q --backup=off -U $@ ga2gd.pot > /dev/null 2>&1
	touch $@

neamhrialta.po : neamhrialta.pot
	msgmerge -N -q --backup=off -U $@ neamhrialta.pot > /dev/null 2>&1
	touch $@

comhshuite.po : comhshuite.pot
	msgmerge -N -q --backup=off -U $@ comhshuite.pot > /dev/null 2>&1
	touch $@

stemmer.pot : neamhrialta.pot comhshuite.pot
	(cat neamhrialta.pot; egrep '[^</][A-ZÁÉÍÓÚ]' comhshuite.pot | egrep -v 'Content-Type' | LC_ALL=C sed 's/.*/&\nmsgstr ""\n/') > $@

stemmer.po : stemmer.pot
	msgmerge -N -q --backup=off -U $@ stemmer.pot > /dev/null 2>&1
	touch $@

CCGG=${HOME}/gaeilge/ga2gd/ccgg
searchable.txt: ga2gd.po
	cat ga2gd.po neamhrialta.po comhshuite.po | egrep -v '^#~' | tr -d "\n" | sed 's/msgid/\n&/g' | egrep -v 'msg(id|str) ""' | sed 's/^msgid "<[^>]*>//' | sed 's/"#.*/"/' | sed 's/^\([^<]*\)<\/.>"msgstr "\([^"]*\)"/\2\t\1/' | sed 's/_\([a-z]*\)/ (\1)/' > $@
	cat $@ | sed 's/\t.*//' | egrep -n '^' | sed 's/:/: /' > $(CCGG)/ga2gd-b
	cat $@ | sed 's/.*\t//' | egrep -n '^' | sed 's/:/: /' > $(CCGG)/ga2gd

# creates a list of ambiguous words for disambig.pl to loop over and check for
ambig.txt : ga2gd.po
	perl showambig | egrep '^msgid' | sed 's/^msgid "//; s/"$$//' | tr "'" '"' > $@

# reads GA.txt also but ga2gd.po depends on that already
cuardach.txt : comhshuite.po neamhrialta.po ga2gd.po focloir.txt i.pl
	perl i.pl -t
	sed -i '/ xx$$/d' $@
	(sed '/^#/d' comhshuite.po neamhrialta.po | sed "/^msgid/{s/='/=@/g; s/' /@ /g; s/'>/@>/}" | tr '@' '"' | tr -d '\n' | sed 's/msgid "/\n/g' | egrep '>"msgstr' | egrep -v 'msgstr ""' | sed 's/"msgstr "/ /; s/"$$//'; cat cuardach.txt | egrep -v '> x$$' | egrep -v '> xx ' | egrep -v '>xx<') | sort -t '>' -k2,2 | uniq > temp.txt
	mv -f temp.txt $@

# makes "multi-gd.txt" too
# Important to include immutable.txt since it helps evaluate coverage
# of gd2ga; those proper names, English words will now be considered "covered"
# note that the first line below (perl i.pl -s) writes pairs-gd.txt
# and the lines after that tweak it in various ways, and create multi-gd
# NB Doesn't actually copy to github repo if files are unchanged... this
# is especially important for multi-gd since when that changes we need
# to retokenize the whole test corpus... see seal/idirlamha/gd/freq
GIT=${HOME}/seal/caighdean
pairs-gd.txt: gd2ga.po focloir.txt GA.txt i.pl makefile ${HOME}/seal/idirlamha/gd/freq/immutable.txt
	perl i.pl -s
	sed -i '/ xx$$/d; /^xx\?[ _]/d' $@
	sed -i "/^d'[^ ]* d'/s/^d'\(.*\)/dh'\1\na_dh'\1\nde_dh'\1\ndo_dh'\1\n&/" $@
	sed -i "/^d'[^ ][^ ]* [BCDFGMPTbcdfgmpt][^h']/s/^d'\([^ ]*\) \(.\)\(.*\)/d'\1 do \2h\3\ndh'\1 do \2h\3\na_dh'\1 do \2h\3\nde_dh'\1 de \2h\3\ndo_dh'\1 do \2h\3/" $@
	sed -i "/^d'[^ ]* [Ss][aeiouáéíóúlnr]/s/^d'\([^ ]*\) \(.\)\(.*\)/d'\1 do \2h\3\ndh'\1 do \2h\3\na_dh'\1 do \2h\3\nde_dh'\1 de \2h\3\ndo_dh'\1 do \2h\3/" $@
	sed -i "/^d'[^ ]* [HLNRVhlnqrv]/s/^d'\([^ ]*\) \(.*\)/d'\1 do \2\ndh'\1 do \2\na_dh'\1 do \2\nde_dh'\1 de \2\ndo_dh'\1 do \2/" $@
	sed -i "/^d'[^ ]* [Ss][^haeiouáéíóúlnr]/s/^d'\([^ ]*\) \(.*\)/d'\1 do \2\ndh'\1 do \2\na_dh'\1 do \2\nde_dh'\1 de \2\ndo_dh'\1 do \2/" $@
	sed -i "/^b'[^ ][^ ]* [BCDFGMPTbcdfgmpt][^h']/s/^b'\([^ ]*\) \(.\)\(.*\)/b'\1 ba \2h\3/" $@
	sed -i "/^b'[^ ]* [Ss][aeiouáéíóúlnr]/s/^b'\([^ ]*\) \(.\)\(.*\)/b'\1 ba \2h\3/" $@
	sed -i "/^b'[^ ]* [HLNRVhlnqrv]/s/^b'\([^ ]*\) \(.*\)/b'\1 ba \2/" $@
	sed -i "/^b'[^ ]* [Ss][^haeiouáéíóúlnr]/s/^b'\([^ ]*\) \(.*\)/b'\1 ba \2/" $@
	sed -i "/^[BCDFGMPTbcdfgmpt][^h'][^ ]* b'/s/^./bu_&h/" $@
	sed -i "/^[Ss][aeiouáéíóúlnr][^h][^ ]* b'/s/^./bu_&h/" $@
	sed -i "/^[HLNRVhlnqrv][^ ]* b'/s/^/bu_/" $@
	sed -i "/^[Ss][^haeiouáéíóúlnr][^ ]* b'/s/^/bu_/" $@
	sed -i "/^m'[^ ][^ ]* [BCDFGMPTbcdfgmpt][^h']/s/^m'\([^ ]*\) \(.\)\(.*\)/m'\1 mo \2h\3/" $@
	sed -i "/^m'[^ ]* [Ss][aeiouáéíóúlnr]/s/^m'\([^ ]*\) \(.\)\(.*\)/m'\1 mo \2h\3/" $@
	sed -i "/^m'[^ ]* [HLNRVhlnqrv]/s/^m'\([^ ]*\) \(.*\)/m'\1 mo \2/" $@
	sed -i "/^m'[^ ]* [Ss][^haeiouáéíóúlnr]/s/^m'\([^ ]*\) \(.*\)/m'\1 mo \2/" $@
	sed -i "/^[BCDFGMPTbcdfgmpt][^h'][^ ]* m'/s/^./mo_&h/" $@
	sed -i "/^[Ss][aeiouáéíóúlnr][^h][^ ]* m'/s/^./mo_&h/" $@
	sed -i "/^[HLNRVhlnqrv][^ ]* m'/s/^/mo_/" $@
	sed -i "/^[Ss][^haeiouáéíóúlnr][^ ]* m'/s/^/mo_/" $@
	cat gd2ga.po | sed '/^#/d' | sed '/msgid/s/ \([^"]\)/_\1/g' | tr -d "\n" | sed 's/msgid/\n&/g' | sed '1d' | egrep -v 'msgstr ""' | sed 's/^msgid "//' | sed 's/"msgstr "/ /' | sed 's/"$$//' | bash split.sh | LC_ALL=C sort -k1,1 > po-temp-proc.txt
	(cat $@; cat po-temp-proc.txt | sed 's/_[a-z][a-z]* / /' | sed 's/_[a-z][a-z]*$$//' | sed 's/[0-9]*$$//'; egrep '[^0]$$' focloir.txt | sed 's/^\([^\t]*\)\t*[^\t]*\t*[^\t]*\t\([^\t]*\)$$/\1~\2/' | sed 's/ /_/g' | sed 's/~/ /' | LC_ALL=C sort -k2,2 | LC_ALL=C join -1 2 -2 1 - po-temp-proc.txt | sed 's/^[^ ]* //' | sed 's/[0-9]*_[a-z][a-z]* / /' | sed 's/[0-9]*_[a-z][a-z]*$$//'; cat ${HOME}/seal/idirlamha/gd/freq/immutable.txt | sed 's/.*/& &/') | LC_ALL=C sort -u | LC_ALL=C sort -k1,1 > temp.txt
	cat temp.txt | egrep -v '_' > $@
	if ! diff -q $@ $(GIT)/$@; then cp -f $@ $(GIT); fi
	(cat $(GIT)/multi-gd.txt; cat temp.txt | egrep '_') | LC_ALL=C sort -u | LC_ALL=C sort -k1,1 > multi-gd.txt
	if ! diff -q multi-gd.txt $(GIT)/multi-gd.txt; then cp -f multi-gd.txt $(GIT); fi
	rm -f po-temp-proc.txt temp.txt

lookup.txt : cuardach.txt i.pl
	perl i.pl -t 2>&1 | sort -t ':' -k1,1 > $@

# Using mcneir list now
#CRUB=/usr/local/share/crubadan/gd
#GLAN-update : lexicon-gd.txt FORCE
#	cat lexicon-gd.txt | sed 's/ .*//' | LC_ALL=ga_IE sort -u | iconv -f iso-8859-1 -t utf8 > $(CRUB)/GLAN
#	cp $(CRUB)/GLAN $(CRUB)/LEXICON
#	togail gd glan 20

fullstem.txt : GA.txt tagcvt.pl
	cat GA.txt | tr '\n' '@' | sed 's/-@/\n/g' | egrep -v '^xx' | perl -p -e 'chomp; ($$hd) = /([^@]+)/; s/@/ $$hd\n/g' | egrep -v '^xx' | sort -u | perl ./tagcvt.pl ga | sort -u > $@

fullstem-gd.txt : GD.txt
	cat GD.txt | tr '\n' '@' | sed 's/-@/\n/g' | egrep -v '^xx' | perl -p -e 'chomp; ($$hd) = /([^@]+)/; s/@/ $$hd\n/g' | egrep -v '^x[ x]' | sort -u | perl ./tagcvt.pl gd | sort -u > $@

juststem-gd.txt: fullstem-gd.txt
	cat fullstem-gd.txt | sed 's/<[^>]*>//g' | egrep -v ' .* ' > $@

mbm-stem.txt: juststem-gd.txt
	cat juststem-gd.txt | tolow | sed 's/^\([^ ]*\) \(.*\)$$/\2 \1/' | LC_ALL=C sort -u | LC_ALL=C sort -k1,1 | tr " " "\t" > $@

mbm-morph.txt: fullstem-gd.txt gr2ud.sed
	cat fullstem-gd.txt | sed -f gr2ud.sed | sed 's/<\/.>$$//' | sed 's/<..> <[^>]*>/\t/' | sed 's/^\([^\t]*\)\t\([^\t]*\)/\2\t\1/' | egrep -v '[<>]' | sort -u | sort -k1,1 > $@

stemfreq.txt: stemfreq.pl juststem-gd.txt ${HOME}/seal/idirlamha/gd/freq/freq.txt
	perl stemfreq.pl > $@

all-gd.txt: GD.txt
	cat GD.txt | egrep -v '^xx ' | egrep -v -- '^-$$' | sed 's/ [0-9]*$$//' | sed "/^d'/s/^d'\(.*\)/dh'\1\n&/" | LC_ALL=C sort -u > $@

fullstem-nomutate.txt : fullstem.txt
	cat fullstem.txt | sed '/ t="\(caite\|coinn\|gnáth\|foshuit\)"/s/">\(.\)h\([^Ff]\)/">\1\2/' | egrep -v '<F>' | egrep -v ">.[A-ZÁÉÍÓÚh'-]" | egrep -v '>(m[Bb]|g[Cc]|n[DdGg]|b[Pp]|t[Ss]|d[Tt])' | egrep -v 'h="y"' | egrep -v 't="ord">h.*>[aeiouáéíóú]' > $@

fullstem-nomutate-gd.txt : fullstem-gd.txt
	cat fullstem-gd.txt | egrep -v ">.[h']" | egrep -v ">[th]-" > $@

verbalnouns-gd.txt: fullstem-nomutate-gd.txt
	(echo "tighinn"; echo "toirt"; egrep '^<N.* <V' fullstem-nomutate-gd.txt | egrep -v 'gnt="y"' | egrep -v '>n-' | sed 's/^<[^>]*>//' | sed 's/<.*//') | sort -u > $@

speling-ga.txt : fullstem-nomutate.txt
	cat fullstem-nomutate.txt | perl tospeling.pl > $@

apertium-toinsert.txt : speling-ga.txt
	python ${HOME}/seal/apertium/apertium/apertium-tools/speling/speling-paradigms-py25.py speling-ga.txt > tempdic
	python ${HOME}/seal/apertium/apertium/apertium-tools/speling/paradigm-chopper.py tempdic 1line > $@
	rm -f tempdic
	sed -i '1,3d' $@
	sed -i '/^  <\/section>$$/d' $@
	sed -i '/^<\/dictionary>$$/d' $@
	sed -i '/__\(n_[mf]\|vblex\|adj\)"/s/"><i>\([aAáÁbBcCdDeEéÉfFgGiIíÍmMoOóÓpPtTuUúÚ]\)/"><par n="initial-\1"\/><i>/' $@
	sed -i '/__\(n_[mf]\|vblex\|adj\)"/s/"><i>\([sS]\)\([aeiouáéíóúlnr]\)/"><par n="initial-\1"\/><i>\2/' $@

apertium-ga-gd.ga.dix : apertium-toinsert.txt apertium-ga-gd.ga.dix.in
	sed '/Insert Here -->/r apertium-toinsert.txt' apertium-ga-gd.ga.dix.in > $@
	cp apertium-ga-gd.ga.dix ~/seal/apertium/incubator/apertium-ga-gv/apertium-ga-gv.ga.dix

speling-gd.txt : fullstem-nomutate-gd.txt
	cat fullstem-nomutate-gd.txt | perl tospeling-gd.pl > $@

stemmerupdate: GA.txt $(STEMMER)/scripts/stemmer fullstem.txt
	(sed '/^#/d' stemmer.po | sed "/^msg/{s/='/=@/g; s/' /@ /g; s/'>/@>/}" | tr '@' '"' | tr -d '\n' | sed 's/msgid "/\n/g' | egrep '>"msgstr' | egrep -v 'msgstr ""' | sed 's/"msgstr "/ /; s/"$$//'; cat fullstem.txt) | sort -u > $(STEMMER)/share/stemmer.txt
	perl -I $(STEMMER)/lib $(STEMMER)/scripts/stemmer -p $(STEMMER)/share/stemmer.txt
	(cd $(STEMMER); perl Makefile.PL; make)

triailcheck : FORCE
	cat test.txt | sed '/^#/d' | ga2gd > torthai-nua.txt
	vimdiff torthai.txt torthai-nua.txt
	rm -f torthai-nua.txt

torthai.txt-update : FORCE
	rm -f torthai.txt
	cat test.txt | sed '/^#/d' | ga2gd > torthai.txt

clean :
	rm -f GA.txt GD.txt *.bak *.pot messages.mo lookup.txt cuardach.txt lexicon-gd.txt ambig.txt fullstem.txt fullstem-gd.txt fullstem-nomutate*.txt speling*.txt apertium-toinsert.txt apertium-ga-gd.ga.dix torthai-nua.txt all-gd.txt pairs-gd.txt replacements.txt searchable.txt tempdic doileir.txt falsefriends.txt multi-gd.txt leabhar.aux leabhar.log leabhar.out leabhar.pdf sonrai.tex sonrai.xml verbalnouns-gd.txt stemfreq.txt juststem-gd.txt

distclean :
	$(MAKE) clean

.PRECIOUS : ga2gd.po

FORCE :
