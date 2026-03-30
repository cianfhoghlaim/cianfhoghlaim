
# when a new file is available from https://dumps.wikimedia.org/gawiki/latest,
# just need to do:
# $ make distclean
# $ make
all: titles.txt hussey.tsv primemovers.tsv edits-processed.tsv

gawiki-latest-pages-meta-history.xml:
	bunzip2 gawiki-latest-pages-meta-history.xml.bz2

gawiki-latest-pages-meta-history.xml.bz2:
	wget https://dumps.wikimedia.org/gawiki/latest/gawiki-latest-pages-meta-history.xml.bz2

titles.txt: gawiki-latest-pages-meta-history.xml
	cat gawiki-latest-pages-meta-history.xml | egrep '<title>' | egrep -o 'title>.*</' | sed 's/^title>//' | sed 's/<\/$$//' > $@

# sorted list of the pages with the most edits by HusseyBot...
# mostly poor quality pages but also note Years and Dates are in there too
hussey.tsv: gawiki-latest-pages-meta-history.xml joiner.pl counter.pl
	cat gawiki-latest-pages-meta-history.xml | perl joiner.pl  | egrep 'HusseyBot.+HusseyBot' | perl counter.pl | tr "\t" "~" | sort -k2,2 -t'~' -r -n | tr "~" "\t" > $@

primemovers.tsv: gawiki-latest-pages-meta-history.xml parse.pl nahusaid.txt
	cat gawiki-latest-pages-meta-history.xml | perl parse.pl -p > $@

edits.json: gawiki-latest-pages-meta-history.xml parse.pl nahusaid.txt
	echo '[' > $@
	cat gawiki-latest-pages-meta-history.xml | perl parse.pl -d >> $@
	sed -i '$$ s/,$$/\n]/' $@

edits-processed.tsv: edits.json ${HOME}/seal/gaelspell/gaelspell.txt ../olleagar/OK.txt ${HOME}/seal/caighdean/pairs.txt ${HOME}/gaeilge/parsail/treebank/tagdict.tsv procedits.pl
	cat edits.json | perl procedits.pl > $@

clean:
	rm -f titles.txt hussey.tsv primemovers.tsv edits.json edits-processed.tsv

distclean:
	make clean
	rm -f gawiki-latest-pages-meta-history.xml*
