GA2GV=${HOME}/gaeilge/ga2gv/ga2gv
DIST=${HOME}/seal/UD_Manx-Cadhan

dist: gv_cadhan-ud-test.conllu gv_cadhan-ud-train.conllu
	cp -f gv_cadhan-ud-test.conllu gv_cadhan-ud-train.conllu $(DIST)
	chmod 644 $(DIST)/gv_cadhan-ud-test.conllu $(DIST)/gv_cadhan-ud-train.conllu

# NEVER EDIT THIS MANUALLY; make fixes in the various input files
gv_cadhan-ud-test.conllu: gold/gold-test.conllu gold/todist.pl usage/parsed-test.conllu alice/alice_gv-test.conllu
	rm -f $@
	(cat gold/gold-test.conllu | perl gold/todist.pl; cat alice/alice_gv-test.conllu usage/parsed-test.conllu) | perl dupecheck.pl > $@
	chmod 444 $@

# NEVER EDIT THIS MANUALLY; make fixes in the various input files
gv_cadhan-ud-train.conllu: gold/gold-train.conllu gold/todist.pl usage/parsed-train.conllu alice/alice_gv-train.conllu
	rm -f $@
	(cat gold/gold-train.conllu | perl gold/todist.pl; cat alice/alice_gv-train.conllu usage/parsed-train.conllu) | perl dupecheck.pl > $@
	chmod 444 $@

# NEVER EDIT THIS MANUALLY; make fixes in the various input files
all.conllu: gold/gold.tsv gold/todist.pl usage/parsed.conllu usage/todist.pl alice/alice_gv.conllu
	rm -f $@
	#(cat gold/gold.tsv | perl gold/todist.pl) | perl dupecheck.pl > $@
	(cat gold/gold.tsv | perl gold/todist.pl; cat alice/alice_gv.conllu; cat usage/parsed.conllu | perl usage/todist.pl) | perl dupecheck.pl > $@
	chmod 444 $@

tagdict.tsv: $(GA2GV)/GV.txt tag2ud.pl moretags.tsv
	(cat $(GA2GV)/GV.txt | perl tag2ud.pl | egrep -v "^[bdm]'"; cat moretags.tsv) | sort -u | sort -k1,1 > $@

gv.udpipe: gv_cadhan-ud-test.conllu
	cat gv_cadhan-ud-test.conllu | udpipe --tokenizer "epochs=25" --train $@

gv-dict.udpipe: gv_cadhan-ud-test.conllu tagdict.tsv
	cat gv_cadhan-ud-test.conllu | udpipe --tokenizer "epochs=25" --tagger "dictionary_file=tagdict.tsv" --train $@

gv-best.udpipe: all.conllu tagdict.tsv gv.vec
	cat all.conllu | udpipe --tokenizer "epochs=50" --tagger "dictionary_file=tagdict.tsv" --parser "embedding_form_file=gv.vec" --train $@

gv.vec: ${HOME}/seal/idirlamha/gv/word2vec/gv.vec
	cp ${HOME}/seal/idirlamha/gv/word2vec/gv.vec $@

evaluate: FORCE gv.udpipe gv-dict.udpipe gv-best.udpipe gv-all.udpipe
	udpipe --accuracy --tokenize --tag --parse gv.udpipe alice/alice_gv.conllu 
	udpipe --accuracy --tokenize --tag --parse gv-dict.udpipe alice/alice_gv.conllu 
	udpipe --accuracy --tokenize --tag --parse gv-best.udpipe alice/alice_gv.conllu 

BATCH=5
corpus.txt:
	make gold-corpus.txt
	cat ${HOME}/seal/idirlamha/gv/freq/corpus.txt | shuf | keepif -n gold-corpus.txt | egrep -v '[=<>×~|`+{}_#]' | egrep -v ' (of|the|you|or|in|an|to|npl|mpl) ' | sed 's/^[0-9][0-9]*:[0-9][0-9]*: *//' | sed 's/^[0-9][0-9]*[.)]\?  *\([A-Z]\)/\1/' | egrep '^[A-ZÇ“"‘]' | egrep '[.?!”"’]$$' | head -n $(BATCH) > $@

# Always safe to run this, as long as not in the middle
# of editing edit.tsv, tagged.tsv, or pedit.tsv!
clean: 
	rm -f corpus.txt ig-output.txt draft.tsv edit.tsv tagged.tsv pedit.tsv
	rm -f gold-corpus.txt gv_cadhan-ud-test.conllu gv_cadhan-ud-dev.conllu gv_cadhan-ud-train.conllu tagdict.tsv all.conllu
	rm -f *.udpipe gv.vec

FORCE:

#####  Remainder is old stuff for bootstrapping original corpus #####
#pedit.tsv: tagged.tsv draftparse.pl renumber.pl
#	cat tagged.tsv | perl renumber.pl | perl draftparse.pl > $@
#
#tagged.tsv: edit.tsv renumber.pl stemmer.pl
#	cat edit.tsv | perl renumber.pl | perl stemmer.pl > $@
#
#append: FORCE
#	cat pedit.tsv >> gold.tsv 
#	make gold-corpus.txt
#	make gv_cadhan-ud-test.conllu
#
#gold-corpus.txt: gold.tsv
#	egrep '^# text' gold.tsv | sed 's/^# text = //' > $@
#
#edit.tsv: draft.tsv disambig.pl
#	cat draft.tsv | perl disambig.pl > $@
#
#draft.tsv: tagdict.tsv ig2draft.pl ig-output.txt
#	cat ig-output.txt | perl ig2draft.pl > $@
#
#ig-output.txt: corpus.txt
#	cat corpus.txt | sed 's/.*/<div text="&"\/>&/' | bash ${HOME}/seal/caighdean/tiomanai.sh -x > $@
#
#alts.tsv: ${GA2GV}/focloir.txt
#	cat ${GA2GV}/focloir.txt | egrep -v '0$$' | egrep -v ' ' | cut -f 1,4 | sed 's/[0-9]_/_/' | sed 's/_prep/|ADP/g; s/_v/|VERB/g; s/_n[a-z]*/|NOUN/g; s/_adv/|ADV/g; s/_a/|ADJ/g; s/_pronm/|ADP/g; s/_conj/|SCONJ/g; s/_interr/|PRON/g; s/_pn/|PRON/g; s/_card/|NUM/g; s/_excl/|INTJ/g; s/_poss/|DET/g' | egrep -v "^([A-Za-zÇç'-]+\|[A-Z]+)[^A-Z]\1$$" | sort -u | sort -k1,1 > $@
#	sed -i '/^[A-ZÇ]/s/|NOUN/|PROPN/g' $@
