
all:
	bash build.sh
	bash glan.sh
	find glan -name '????-??' | sort | while read x; do echo `echo $$x | sed 's/^glan.//'` `cat $$x | bash ${HOME}/seal/caighdean/alltokens.sh | egrep "^[#A-Za-z'-]+$$" | wc -l`; done > counts.txt
	bash freq.sh
	rm -f table.hash
	perl hashem.pl
	make index-en.html samplai-en.html
	make new-unknown.txt

new-unknown.txt:
	cat glan/`date --date="$$(date +%Y-%m-15) -1 month" +'%Y-%m'` | bash ${HOME}/seal/caighdean/tiomanai.sh -u | egrep '[A-Za-zÁÉÍÓÚáéíóú]' | egrep '..' | egrep -v '[@#]' | egrep -v '://' | sort | uniq -c | sort -r -n | sed 's/^ *//' > $@
	mv $@ ${HOME}

index-en.html: index.html translate.sh
	cat index.html | bash translate.sh > $@

samplai-en.html: samplai.html translate.sh
	cat samplai.html | bash translate.sh > $@

# don't kill table.hash since this gets sync'd over to cadhan.com
# periodically and is needed by the treochtai website;
# groomm process takes a couple of hours and will just overwrite
# this when it gets to the "make all" above
clean:
	rm -f aschur/*
	rm -f seenonline.txt nos-*.txt tuairisc-*.txt full-hapax.txt
	rm -f index-en.html samplai-en.html new-unknown.txt

distclean:
	make clean
	rm -Rf aschur corpas freq glan
	rm -f freq.txt counts.txt

######################################################################
#  Can ignore everything below; once off project for Nós/Tuairisc    #
######################################################################
# for Maitiú's request, words appearing in Nós or Tuairisc for first time
# online; use this file to filter out English and stuff from Gaeilge-A
seenonline.txt:
	(cat /usr/local/share/crubadan/en/GLAN; cat /usr/local/share/crubadan/ga/ciu/232052.txt | bash ${HOME}/seal/caighdean/alltokens.sh | egrep '^[A-Za-z-]+$$') | sort -u > $@

nos-hapax.txt: hapaxfeed.pl ${HOME}/gaeilge/crubadan/rss/sonrai/nos.ie.xml seenonline.txt
	perl hapaxfeed.pl ${HOME}/gaeilge/crubadan/rss/sonrai/nos.ie.xml > $@

tuairisc-hapax.txt: hapaxfeed.pl ${HOME}/gaeilge/crubadan/rss/sonrai/tuairisc.ie.xml seenonline.txt
	perl hapaxfeed.pl ${HOME}/gaeilge/crubadan/rss/sonrai/tuairisc.ie.xml > $@

full-hapax.txt: hapaxfull.sh
	bash hapaxfull.sh > $@

nos-first.txt: nos-hapax.txt full-hapax.txt
	LC_ALL=C join full-hapax.txt nos-hapax.txt | egrep ' (.+) \1$$' | egrep '^[a-záéíóú]' | sed 's/ [^ ]*$$//' | sort -k1,1 > $@

tuairisc-first.txt: tuairisc-hapax.txt full-hapax.txt
	LC_ALL=C join full-hapax.txt tuairisc-hapax.txt | egrep ' (.+) \1$$' | egrep '^[a-záéíóú]' | sed 's/ [^ ]*$$//' | sort -k1,1 > $@
