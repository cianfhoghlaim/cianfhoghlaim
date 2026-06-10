# Tools for disambiguation pages.
#
# Three useful targets:
# problems.tsv: maybe unwanted links to DAB pages
# logainm-dabneeded.txt: list of ambiguous placenames without DAB page
# daoine-dabneeded.txt: list of personal names without DAB page
#
# NB: The problems.tsv target is self-contained; no olleagar dump needed.
all: problems.tsv logainm-dabneeded.txt daoine-dabneeded.txt

problems.tsv: dab-links.tsv oklinks.tsv
	cat dab-links.tsv | egrep -v '\(idirdhealú\)$$' | tr "\t" "~" | egrep -v '^(.+), .*~\1$$' | egrep -v '^(.+) \(.*\)~\1$$' | tr "~" "\t" | keepif -n oklinks.tsv > $@

dab-links.tsv: dab-links.html
	cat dab-links.html | egrep '^<li>.+ → ' | sed 's/^<li><[^>]*>//' | sed 's/<\/a>.* → <a[^>]*>/\t/' | sed 's/<\/a><\/li>//' > $@

dab-links.html:
	wget -O $@ 'https://ga.wikipedia.org/w/index.php?title=Speisialta:DisambiguationPageLinks&limit=500&offset=0'
	wget -O temptemptemp.html 'https://ga.wikipedia.org/w/index.php?title=Speisialta:DisambiguationPageLinks&limit=500&offset=500'
	cat temptemptemp.html >> $@
	rm -f temptemptemp.html

alldab.txt: alldab.html
	egrep '^<li><a href="/wiki/' alldab.html | sed 's/^<li><a href[^>]*>//' | sed 's/<\/a>.*//' | egrep -v '^(Úsáideoir|Teimpléad):' | sort > $@

alldab.html:
	wget -O $@ 'https://ga.wikipedia.org/w/index.php?title=Speisialta:DisambiguationPages&limit=500&offset=0'
	wget -O temptemptemp.html 'https://ga.wikipedia.org/w/index.php?title=Speisialta:DisambiguationPages&limit=500&offset=500'
	cat temptemptemp.html >> $@
	rm -f temptemptemp.html

logainmneacha.txt: ../logainm/logainm.tsv
	cat ../logainm/logainm.tsv | cut -f 2 | egrep -v '^-$$' | sort | uniq -c | sort -r -n > $@

alldab-noparens.txt: alldab.txt
	cat alldab.txt | sed 's/ (idirdhealú)$$//' > $@

logainm-dabneeded.txt: ../logainm/logainm.tsv alldab-noparens.txt
	cat ../logainm/logainm.tsv | cut -f 2 | egrep -v '^-$$' | keepif -n alldab-noparens.txt | sort | uniq -c | sort -r -n  | egrep -v '^ *1 ' > $@

# could filter out anyone without QID or ainm.ie in daoine.csv?
daoine-dabneeded.txt: ${HOME}/gaeilge/canuinti/daoine.csv alldab-noparens.txt
	cat ${HOME}/gaeilge/canuinti/daoine.csv | egrep -v 'LASID' | sed 's/,.*//' | sed 's/ [0-9]$$//' | keepif -n alldab-noparens.txt | sort | uniq -c | sort -r -n | egrep -v '^ *1 ' | sed 's/^ *//' > $@

clean:
	rm -f dab-links.* alldab* logainm* problems.tsv daoine-dabneeded.txt
