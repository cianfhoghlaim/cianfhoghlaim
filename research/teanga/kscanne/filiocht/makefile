DIOLAIM=${HOME}/gaeilge/diolaim
NGRAMS=${HOME}/gaeilge/ngram
ISPELL=${HOME}/gaeilge/ispell/ispell-gaeilge
ITWEETS=${HOME}/gaeilge/crubadan/twitter
SITE=${HOME}/public_html/amhran
FOCLOIRPOCA=${HOME}/seal/irishcompleted/Focloir-Poca-GB-Original

index.html: x0 site/template.html
	cat x0 | sed 's/$$/<br\/>/' > amhran-body.html
	sed '/^<p>/r amhran-body.html' site/template.html > $@
	find . -name 'x[1-9]' | sed 's/\.\///' | while read x; do cat "$$x" | sed 's/$$/<br\/>/' > amhran-body.html; sed '/^<p>/r amhran-body.html' site/template.html > "$$x.html"; done
	for i in $$(seq 1 9); do back=$$(($$i-1)); forward=$$(($$i+1)); sed -i "/&lt;&lt;/s/x0/x$${back}/" "x$$i.html"; sed -i "/&gt;&gt;/s/x0/x$${forward}/" "x$$i.html"; sed -i "/x$$i.html/s/.*/<b>$${forward}<\/b>/" "x$$i.html"; done
	sed -i 's/^<img.*/<hr>/' x?.html
	sed -i 's/ leathrann</ leathrann (ar lean)</' x?.html
	sed -i '/&gt;&gt;/d' x9.html
	sed -i '/&lt;&lt;/s/x0/index/' x1.html
	sed -i '/&lt;&lt;/d' index.html
	sed -i '/&gt;&gt;/s/x0/x1/' index.html
	sed -i '/"index.html"/s/.*/<b>1<\/b>/' index.html
	rm -f amhran-body.html

install:
	cp -f $@ $(SITE)
	cp -f x?.html $(SITE)
	cp -f site/deighilt.png $(SITE)
	cp -f site/par.jpg $(SITE)

x0: amhran.txt
	split -d -a 1 -l `cat amhran.txt | wc -l | sed 's/.$$//'` amhran.txt

amhran.txt: corpus.txt filiocht.pl $(FOCLOIRPOCA)/FP.txt iarmhir.csv reimir.csv ipa.pl
	cat corpus.txt | randomize | perl ipa.pl $(FOCLOIRPOCA)/FP.txt | perl filiocht.pl -a > $@

foc.pdf: foc.tex sonrai.tex
	pdflatex foc
	sleep 5
	pdflatex foc

sonrai.tex: focloir.txt
	cat focloir.txt | egrep -v '^$$' | sed 's/^/\\item /' | sed 's/$$/./' > $@

focloir.txt: rawwords.txt filiocht.pl $(FOCLOIRPOCA)/FP.txt iarmhir.csv reimir.csv ipa.pl
	 cat rawwords.txt | egrep -v '^an-' | perl ipa.pl $(FOCLOIRPOCA)/FP.txt | perl filiocht.pl -f | shuf | sed 's/^/\n/' > $@

rawwords.txt: $(ISPELL)/aspell.txt
	cat $(ISPELL)/aspell.txt | demut | egrep -v '^.h' | keepif $(ISPELL)/aspell.txt | sort -u > $@

corpus.txt:
	(cat $(DIOLAIM)/l/T-* $(DIOLAIM)/l/IB-* $(DIOLAIM)/l/Hussey $(DIOLAIM)/l/WP* | togail ga makecorp | egrep '.{21}' | egrep -v '.{75}' | egrep -v '[►▼]'; cat ${ITWEETS}/sonrai/ga-tweets.txt | sed 's/^[0-9]*\t[0-9]*\t//' | de-entify | sed 's/^RT @[A-Za-z0-9_][A-Za-z0-9_]*: //' | sed 's/^RT @[A-Za-z0-9_][A-Za-z0-9_]*: //' | sort -u) | randomize > $@

corpusmor.txt:
	(cd $(NGRAMS); make corpus.txt)
	(cat $(NGRAMS)/corpus.txt | egrep '.{21}' | egrep -v '.{75}' | egrep -v '[►▼]'; cat ${ITWEETS}/sonrai/ga-tweets.txt | sed 's/^[0-9]*\t[0-9]*\t//' | de-entify | sed 's/^RT @[A-Za-z0-9_][A-Za-z0-9_]*: //' | sort -u) | randomize > $@

clean:
	rm -f x? index.html x?.html

distclean:
	make clean
	rm -f corpus.txt corpusmor.txt amhran.txt rawwords.txt focloir.txt sonrai.tex foc.pdf foc.aux foc.out
