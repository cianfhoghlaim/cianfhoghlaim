# logainm.tsv has placenames scraped from logainm.ie and is a maintained file
# The remainder are built from Wikidata using targets below
all: tocrawl.txt todo.csv

qids.tsv: wd.pl
	perl wd.pl | sed 's/^Q//' | sort -k1,1 -n | sed 's/^/Q/' > $@

# QIDs with more than one logainm ID attached
problems.txt: qids.tsv
	cat qids.tsv | cut -f 1 | sort | uniq -c | egrep -v ' 1 ' | sed 's/^ *[0-9]* //' | sed 's/^Q//' | sort -n | sed 's/^/Q/' > $@

scraped.txt: logainm.tsv
	cat logainm.tsv | cut -f 1 > $@

# Logainm IDs that appear in Wikidata but which I haven't added to logainm.tsv
# Build this, check it out, then:
# cat tocrawl.txt | bash LAlorg.sh
tocrawl.txt: scraped.txt qids.tsv
	cat qids.tsv | cut -f 3 | keepif -n scraped.txt | sort -n > $@

# Finds any WD items with missing Irish label that is available in logainm.tsv
# Suitable for quickstatements
todo.csv: qids.tsv problems.txt logainm.tsv
	cat qids.tsv | egrep '^Q[0-9]+[[:space:]]Q[0-9]' | cut -f 1,3 > temp1.tsv
	cat problems.txt | while read x; do sed -i "/^$${x}\t/d" temp1.tsv; done
	cat logainm.tsv | LC_ALL=C sort -k1,1 | tr "\t" "~" > temp2.txt
	echo "qid,Lga" > $@
	cat temp1.tsv | LC_ALL=C sort -k2,2 | tr "\t" "~" | LC_ALL=C join -t '~' -1 2 -2 1 - temp2.txt | tr "~" "\t" | sed '/\t-\t/d' | cut -f 2,3 | sed 's/\t\(.*\)$$/,"\1"/' >> $@
	rm -f temp1.tsv temp2.txt

clean:
	rm -f problems.txt todo.csv scraped.txt tocrawl.txt

distclean:
	make clean
	rm -f qids.tsv
