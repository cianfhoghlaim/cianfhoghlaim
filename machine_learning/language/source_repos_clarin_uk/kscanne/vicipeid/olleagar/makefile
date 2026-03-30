# To update:
# Visit https://dumps.wikimedia.org/gawiki/latest/
# If there are new dumps available, then:
# $ make clean
# $ make
# Then sftp "ga-full.tsv" over to laptop's HusseyBot folder
all: bad.txt titles.txt ga-files.tsv ga-full.tsv ga-redirects.tsv corpas.txt wd-needed.txt

ga.xml:
	wget -O ga.xml.bz2 http://dumps.wikimedia.org/gawiki/latest/gawiki-latest-pages-meta-current.xml.bz2
	bunzip2 ga.xml.bz2

# like ga.tsv but keeps templates + HTML tags (except <nowiki/>)
ga-full.tsv: ga.xml
	cat ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep -v '<title>(Plé|Úsáideoir|Íomhá|Vicipéid|Module|MediaWiki|Plé .+|VP|Cabhair|Teimpléad):' | egrep -v -i '#(athsheoladh|redirect)' | egrep -o '<title>.+</text>' | sed 's/^<title>//' | sed 's/<\/title>.*<text[^>]*>/\t/' | sed 's/<\/text>$$//' | de-entify | de-entify | perl killpics.pl | bash killlinks.sh | bash killlinks.sh | sed 's/<nowiki.>//g' > $@

ga-redirects.tsv: ga.xml
	cat ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep -v '<title>(Plé|Úsáideoir|Íomhá|Vicipéid|Module|MediaWiki|Plé .+|VP|Cabhair|Teimpléad):' | egrep -i '#(athsheoladh|redirect)' | egrep -o '<title>.+</text>' | sed 's/^<title>//' | sed 's/<\/title>.*<text[^>]*>/\t/' | sed 's/<\/text>$$//' | de-entify | sed 's/\]\].*$$/]]/' | sed 's/#\(athsheoladh\|redirect\) *//gi' | sed 's/\[\[\(.*\)\]\]$$/\1/' | sed 's/\t  */\t/' | sed 's/  *$$//' > $@

ga-files.tsv: ga.xml
	cat ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep '<title>Íomhá:' | egrep -i -v '#(athsheoladh|redirect)' > $@ 

# title is first field, full text is second field (all on one line)
# NB: killtemplates.pl also wipes out SGML markup
ga.tsv: ga.xml
	cat ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep -v '<title>(Plé|Úsáideoir|Íomhá|Vicipéid|Module|MediaWiki|Plé .+|VP|Cabhair|Teimpléad):' | egrep -v -i '#(athsheoladh|redirect)' | egrep -o '<title>.+</text>' | sed 's/^<title>//' | sed 's/<\/title>.*<text[^>]*>/\t/' | sed 's/<\/text>$$//' | de-entify | de-entify | perl killtemplates.pl | bash killlinks.sh | bash killlinks.sh > $@

titles.txt: ga.xml
	cat ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep -v -i '#(athsheoladh|redirect)' | egrep -o '<title>[^<]+</title>' | sed 's/^<title>//' | sed 's/<\/title>//' > $@

# OK.txt has non-Gaelspell words from the "confident Irish speaker" model
# OK-eile.txt has other stuff that doesn't need correcting (Latin, etc.)
bad.txt: ${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt OK.txt ga.tsv OK-eile.txt
	cat ga.tsv | aspell -dga list | keepif -n ${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt | keepif -n ./OK.txt | keepif -n ./OK-eile.txt | sort | uniq -c | sort -r -n | sed 's/^ *//' > $@

# misspelled words from the "high-quality" corpus
bad-clean.txt: corpas.json
	cat corpas.json | egrep '"téacs": ' | sed 's/^ *"téacs": *//' | sed 's/^"//' | sed 's/" *$$//' | sed 's/\\"/"/g' | sed 's/\\n/ /g' | sed "s/’/'/g" | aspell -dga list | keepif -n /usr/local/share/crubadan/en/GLAN | sort | uniq -c | sort -r -n | sed 's/^ *//' > $@

# 1 hr 20 mins on 2023-08-10
# discards spelling errors since I'm going through those in bad.txt
# with the help of surv.sh, etc.
errors.xml: corpas.txt
	cat corpas.txt | perl -I ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/lib ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/scripts/gram-ga.pl --ionchod=utf-8 --api | api2old | egrep -v 'Lingua::GA::Gramadoir/(ANAITHNID|(GRAM|MOIRF|CAIGHMOIRF|COMHFHOCAL|COMHCHAIGH|MICHEART|DROCHMHOIRF|CAIGHDEAN|MIMHOIRF)[{])' > $@

# pages that might need a {{WD..}} template added
wd-needed.txt: ga-full.tsv wd-ignore.txt
	cat ga-full.tsv | egrep -v '[{]WD' | egrep -v 'Bosca.(sonraí.eipeasóid|comórtas.ceoil)' | egrep -v 'Catagóir:Idirdheal' | egrep -v '[{][Ii]dirdheal' | cut -f 1 | egrep -v '^(Catagóir):' | egrep -v '^[0-9]+' | keepif -n wd-ignore.txt > $@
	wc -l $@

corpas.json: ga-full.tsv corpas.pl
	cat ga-full.tsv | perl corpas.pl > $@

corpas.txt: corpas.json
	cat corpas.json | egrep '^ *"téacs": ' | sed 's/^ *"téacs": "/\n\n-=-=-=-=-=-=-=-=-\n\n/' | sed 's/"$$//' | sed 's/\\"/"/g' | sed 's/\\n/\n/g' | fmt -s | sed 's/^ *//' > $@
	cp -f corpas.txt ${HOME}/gaeilge/diolaim/l/WPdump

clean:
	rm -f ga.xml.bz2 ga.xml ga.tsv titles.txt wd-needed.txt corpas.json corpas.txt bad.txt ga-redirects.tsv ga-files.tsv ga-full.tsv bad-clean.txt

distclean:
	make clean
	rm -f errors.xml
