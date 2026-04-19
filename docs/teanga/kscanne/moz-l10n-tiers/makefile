SOURCELANG=ga-IE
SAMPLEFILE=browser/chrome/browser/newTab.dtd

all: pseudo/$(SAMPLEFILE)

pseudo/$(SAMPLEFILE): tiers.txt $(SOURCELANG)/$(SAMPLEFILE) pseudolocale.sh
	bash pseudolocale.sh $(SOURCELANG)

tiers-update.txt: refreshclone
	find $(SOURCELANG) -type f | egrep -v '\.hg' | sed 's/^[^\/]*\///' | LC_ALL=C sort -k1,1 | LC_ALL=C join -a 2 tiers.txt - | sed '/^[^ ]*$$/s/$$/ 5/' > $@
	diff -u tiers.txt $@

refreshclone:
	(cd $(SOURCELANG); hg up; hg pull -u)

clone:
	rm -fR $(SOURCELANG)
	hg clone http://hg.mozilla.org/releases/l10n/mozilla-aurora/$(SOURCELANG)/

clean:
	rm -Rf pseudo tiers-update.txt

distclean:
	$(MAKE) clean
	rm -Rf $(SOURCELANG)
