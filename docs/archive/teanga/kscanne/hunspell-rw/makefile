VERSION=0.01

all : rw_RW.aff rw_RW.dic

#all : diffs.txt

test-input.txt : test.txt
	cat test.txt | sed '/^#/d' | sed 's/[ \t].*//' > $@

test-output.txt : test.txt
	cat test.txt | sed '/^#/d' | sed 's/^[^ \t]*[ \t]*//' > $@

diffs.txt : test-input.txt test-output.txt rw.pl
	-cat test-input.txt | perl rw.pl | sed 's/ .*//' | diff -u test-output.txt - > $@
	cat $@

# what "rw.pl" script thinks all inflections of intransitive "som" are
somall.txt : rw.pl
	echo "som" | sed 's/^/PP+SM+NM+TM+NA+REFL^/' | sed 's/$$/^REV+RECIP+INSTR+NEUT+APPL+IZ+PASSIVE+AM+PS/' | perl rw.pl | sed 's/ .*//'	> $@

# which of these (presumed correct words) are not recognized by dic+affix file
somallbad.txt : somall.txt rw_RW.dic rw_RW.aff
	cp $@ somallbad-prev.txt
	cat somall.txt | hunspell -l -d ./rw_RW > $@
	wc -l somallbad*.txt

huntest : rw_RW.dic rw_RW.aff
	echo "som" | sed 's/^/PP+SM+NM+TM+NA+REFL^/' | sed 's/$$/^REV+RECIP+INSTR+NEUT+APPL+IZ+PASSIVE+AM+PS/' | perl rw.pl | sed 's/ .*//' | hunspell -l -d ./rw_RW
#	cat roots.txt | sed 's/[ \t].*//' | sed 's/^/PP+SM+NM+TM+NA+REFL^/' | sed 's/$$/^REV+RECIP+INSTR+NEUT+APPL+IZ+PASSIVE+AM+PS/' | perl rw.pl | sed 's/ .*//' | hunspell -l -d ./rw_RW

rw_RW.dic : roots.txt rw.pl
	echo `cat roots.txt | wc -l` > $@
	cat roots.txt | sed 's/[ \t].*//' | perl rw.pl | sed '/^[chfkpst]/s/ .*/\/ZA/' | sed '/^[^chfkpst]/s/ .*/\/ZP/' >> $@

#	cat prefixes1.txt | perl prefgen.pl Q >> $@
#	echo >> $@
#	cat prefixes2.txt | perl prefgen.pl R >> $@
#	echo >> $@
rw_RW.aff : dahlprefixes0.txt dahlprefixes1.txt dahlprefixes2.txt prefixes0.txt prefixes1.txt prefixes2.txt suffixes.txt affixtemplate.txt suffgen.pl prefgen.pl
	cp -f affixtemplate.txt $@
	cat dahlprefixes0.txt | perl prefgen.pl A >> $@
	echo >> $@
	cat prefixes0.txt | perl prefgen.pl P >> $@
	echo >> $@
	cat prefixes1.txt | perl prefgen.pl Q >> $@
	echo >> $@
	cat prefixes2.txt | perl prefgen.pl R >> $@
	echo >> $@
	cat suffixes.txt | perl suffgen.pl >> $@

dahlprefixes0.txt : rw.pl
	echo "PP+SM+NM+TM+NA+REFL^som^" | perl rw.pl | sed 's/som .*//' | sort -u > $@

dahlprefixes1.txt : rw.pl
	echo "PP+SM+NM+TM+NA+OM+REFL^som^" | perl rw.pl | sed 's/som .*//' | sort -u > $@

dahlprefixes2.txt : rw.pl
	echo "PP+SM+NM+TM+NA+OM+OM+REFL^som^" | perl rw.pl | sed 's/som .*//' | sort -u > $@

prefixes0.txt : rw.pl
	echo "PP+SM+NM+TM+NA+REFL^xxx^" | perl rw.pl | sed 's/xxx.*//' | sort -u > $@

prefixes1.txt : rw.pl
	echo "PP+SM+NM+TM+NA+OM+REFL^xxx^" | perl rw.pl | sed 's/xxx.*//' | sort -u > $@

prefixes2.txt : rw.pl
	echo "PP+SM+NM+TM+NA+OM+OM+REFL^xxx^" | perl rw.pl | sed 's/xxx.*//' | sort -u > $@

suffixes.txt : rw.pl
	echo "^xxx^REV+RECIP+INSTR+NEUT+APPL+IZ+PASSIVE+AM+PS" | perl rw.pl | sed 's/^xxx//' | sed 's/ .*//' | sort -u > $@

clean :
	rm -f diffs.txt test-*.txt dahlprefixes*.txt prefixes*.txt rw_RW.aff rw_RW.dic somall*.txt suffixes.txt

APPNAME=affixgen-rw-$(VERSION)
TARNAME=$(APPNAME).tar
dist : FORCE
	ln -s affixgen-rw ../$(APPNAME)
	tar cvhf $(TARNAME) -C .. $(APPNAME)/affixtemplate.txt
	tar rvhf $(TARNAME) -C .. $(APPNAME)/makefile
	tar rvhf $(TARNAME) -C .. $(APPNAME)/prefgen.pl
	tar rvhf $(TARNAME) -C .. $(APPNAME)/roots.txt
	tar rvhf $(TARNAME) -C .. $(APPNAME)/rw.pl
	tar rvhf $(TARNAME) -C .. $(APPNAME)/suffgen.pl
	tar rvhf $(TARNAME) -C .. $(APPNAME)/test.txt
	tar rvhf $(TARNAME) -C .. $(APPNAME)/COPYING
	tar rvhf $(TARNAME) -C .. $(APPNAME)/README
	gzip $(TARNAME)
	rm -f ../$(APPNAME)

FORCE:
