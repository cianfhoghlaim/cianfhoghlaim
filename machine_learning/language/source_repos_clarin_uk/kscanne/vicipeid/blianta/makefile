all: breith.tsv bas.tsv

breith.tsv:
	bash doall.sh breith > $@
	bash killdupes.sh breith.tsv

bas.tsv:
	bash doall.sh bas > $@
	bash killdupes.sh bas.tsv

clean:
	rm -f breith.tsv bas.tsv

.PRECIOUS: breith.tsv bas.tsv
