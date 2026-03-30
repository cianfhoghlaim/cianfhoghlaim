DISTNAME= crubadan-web-back
VERSION=  0.1.5
EXECNAME= crbackend
FCGINAME= $(EXECNAME)-fcgi_
INITNAME= $(EXECNAME).init
DISTDIR= $(DISTNAME)-$(VERSION)
DISTFILE= $(DISTDIR).tar.gz
BINDIR= bin

all: pack

package: pack
	tar czf $(DISTFILE) $(DISTDIR)

pack: build dist_dir
	cp -r $(BINDIR) $(DISTDIR)/
	cp ../README.md $(DISTDIR)/
	cp  ./LICENSE   $(DISTDIR)/
	cp $(INITNAME)  $(DISTDIR)/$(EXECNAME)

dist_dir: clean
	mkdir $(DISTDIR)

build: sandbox shared bin_dir
	cabal install
	rm -r dist
	cp .cabal-sandbox/bin/$(FCGINAME) $(BINDIR)/
	cp $(EXECNAME) $(BINDIR)/

shared: sandbox
	rm -r ../shared/dist; exit 0;
	cabal install ../shared
	rm -r ../shared/dist

bin_dir: clean
	mkdir $(BINDIR)

sandbox: clean
	cabal sandbox init

clean:
	rm -r $(BINDIR); rm -r $(DISTDIR); rm $(DISTFILE); exit 0;
	rm -r .cabal-sandbox; rm cabal.sandbox.config; exit 0;
