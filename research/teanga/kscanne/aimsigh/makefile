
SHELL=/bin/sh
MAKE=/usr/bin/make
INSTALL=/usr/bin/install
INSTALL_DATA=$(INSTALL) -m 444
CC=/usr/bin/gcc
prefix=/usr/local
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin
libexecdir = $(exec_prefix)/libexec
datadir = $(prefix)/share
crubadandir = $(datadir)/crubadan/ga

install :
	$(INSTALL) aimsigh.cgi /home/httpd/cgi-bin
	$(INSTALL) dockill $(bindir)/dockill
	$(INSTALL) seed $(bindir)/seed
	$(INSTALL) tgrep $(bindir)/tgrep
	$(INSTALL) ugrep $(bindir)/ugrep
	$(INSTALL) urlkill $(bindir)/urlkill
	$(INSTALL) urlsub $(bindir)/urlsub
	$(INSTALL) prsort.pl $(bindir)/prsort.pl
	$(INSTALL) swishy.pl $(bindir)/swishy.pl

# local testing only!
installhtml :
	$(INSTALL_DATA) aimsigh.css ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) aimsigh.png ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) favicon.ico ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) foirm.html ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) index.html ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) eolas.html ${HOME}/public_html/aimsigh
	$(INSTALL_DATA) cabhair.html ${HOME}/public_html/aimsigh

pillagecheck : FORCE
	(cd $(crubadandir); egrep -f PILLAGED MANIFEST | egrep -v '(http://www.waterfordcoco.ie/|https?://listserv.heanet.ie/|http://bbs\.mayo|http://www.englishirishdictionary|http://www.oireachtas.ie/|http://www.tobar.ie/vb/|http://www.peoplesrepublicofcork)')

killdupes : FORCE
	rm -f dupescr dupelog
	perl dupe.pl
	(echo; date; cat dupelog) >> DUPELOG
	rm -f dupelog
	sort -u dupescr > dupe.tmp
	mv dupe.tmp dupescr
	echo 'look at dupescr and then bash it to actually kill the dupes'

freqs : FORCE
	perl totalfreq.pl > $(crubadandir)/FREQ

clean :
	rm -f *.o
FORCE :
