DISTNAME=   crubadan-web-front
VERSION=    0.1.2.0
DISTDIR=    $(DISTNAME)-$(VERSION)
DISTFILE=   $(DISTDIR).tar.gz
RESDIR=     res
STYLEDIR=   style
IMGDIR=     img
JSNAME=     writing_systems.js

BUILTPATH=  .cabal-sandbox/bin/$(DISTNAME).jsexe

JQUERY=     GHCJS-JQuery
JQUERYLINK= https://github.com/GHCJS/$(JQUERY).git

all: package

prep: jquery shared_js

package: build dist_dir
	cp ../README.md $(DISTDIR)/
	cp  ./LICENSE $(DISTDIR)/
	tar czf $(DISTFILE) $(DISTDIR)

build: res_dir
	cabal install --ghcjs
	rm -r ./dist
	cp $(BUILTPATH)/out.js     $(DISTDIR)/$(RESDIR)/$(JSNAME)
	cp $(BUILTPATH)/lib.js     $(DISTDIR)/$(RESDIR)/
	cp $(BUILTPATH)/rts.js     $(DISTDIR)/$(RESDIR)/
	cp $(BUILTPATH)/runmain.js $(DISTDIR)/$(RESDIR)/
	cp $(STYLEDIR)/*.css       $(DISTDIR)/$(RESDIR)/
	cp $(IMGDIR)/*             $(DISTDIR)/$(RESDIR)/

jquery: sandbox
	git clone $(JQUERYLINK)
	cabal install --ghcjs ./$(JQUERY)
	rm -r $(JQUERY)/dist

shared_js: sandbox
	rm -r ../shared/dist; exit 0;
	cabal install --ghcjs ../shared
	rm -r ../shared/dist; exit 0;

res_dir: clean dist_dir
	mkdir $(DISTDIR)/$(RESDIR)

dist_dir: clean
	mkdir $(DISTDIR)

sandbox: fullclean
	cabal sandbox init

clean:
	rm -r $(DISTDIR)/$(RESDIR); rm -r $(DISTDIR); rm $(DISTFILE); exit 0;

fullclean: clean
	rm -rf $(JQUERY); rm -r .cabal-sandbox; rm cabal.sandbox.config; exit 0;
