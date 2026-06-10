# actual deployment to public_html now handled by ../cadhan.com scripts
dist: FORCE
	perl qa.pl
	bash divvy.sh
	ls dist/?-data.html | while read x; do LETTER=`echo $$x | egrep -o '[A-Z]'`; sed "/INSERT HERE/r $$x" template.html > dist/$${LETTER}.html; done
	cp droichead.css ${HOME}/public_html/droichead/
	#cp dist/?.html ${HOME}/public_html/droichead/

triples.tsv: droichead.tsv
	cat droichead.tsv | cut -f 1,5 | sed 's/^/ga:/' | sed 's/\t/\trel:etymology\tsga:/' > $@

clean:
	rm -f triples.tsv

FORCE:
