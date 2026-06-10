all: frasleabhar.pdf

allusage: Usage Usage-b
	cp -f Usage ${HOME}/gaeilge/ga2gv/cc
	cp -f Usage-b ${HOME}/gaeilge/ga2gv/cc

Usage-b: pairs.txt ${HOME}/seal/caighdean/detokenize.pl
	cat pairs.txt | perl ${HOME}/seal/caighdean/detokenize.pl -s | sed 's/^<div text=".*"\/>//' | egrep -n '^' | sed 's/:/: /' > $@

Usage: pairs.txt ${HOME}/seal/caighdean/detokenize.pl
	cat pairs.txt | perl ${HOME}/seal/caighdean/detokenize.pl -t | sed 's/^<div text=".*"\/>//' | egrep -n '^' | sed 's/:/: /' > $@

# don't run again!  manually edited this output with many corrections!
#parsed.conllu: pairs.txt ${HOME}/seal/caighdean/detokenize.pl ${HOME}/gaeilge/ga2gv/ga2gv/ud/gv-all.udpipe
#	cat pairs.txt |  perl ${HOME}/seal/caighdean/detokenize.pl -s | sed 's/^<div[^>]*>/\n/' | udpipe --tokenize --tag --parse ${HOME}/gaeilge/ga2gv/ga2gv/ud/gv-all.udpipe > $@

# we do this directly in ../makefile when building all.conllu
#usage.conllu: parsed.conllu
#	cat parsed.conllu | perl todist.pl > $@

# make dist does a new split into train/test
dist: parsed-checked-test.conllu parsed-checked-train.conllu

#parsed-checked.conllu: parsed.conllu
#	cat parsed.conllu | perl todist.pl > $@

#parsed-checked-test.conllu parsed-checked-train.conllu: parsed-checked.conllu
#	perl ${HOME}/gaeilge/parsail/treebank/sample.pl parsed-checked.conllu 50 0

parsed.json: parsed.conllu conllu2json.pl ${HOME}/gaeilge/ga2gv/ga2gv/focloir.txt addenda.txt
	cat parsed.conllu | perl conllu2json.pl > $@

parsed.tex: parsed.json json2latex.pl
	perl json2latex.pl > $@

frasleabhar.pdf: frasleabhar.tex parsed.tex brollach.tex
	pdflatex frasleabhar
	cp $@ ${HOME}

# SAFE
clean:
	rm -f parsed.json Usage Usage-b frasleabhar.log frasleabhar.out frasleabhar.toc frasleabhar.pdf frasleabhar.aux parsed.tex

##########################################################################
# remainder no longer needed...                                          #
##########################################################################

# ran this once; don't do it again. manually editing this output...
#toedit.txt:
#	cat usage-gv.txt | sed 's/^\(.*\)\t/<div text="\1"\/> /' | bash ${HOME}/seal/caighdean/tiomanai.sh -x > $@

# English msgids, blank msgstrs, Manx comments
usage-gv.po:
	(cat header.po; cat usage-gv.txt | sort -u | sed 's/"/\\"/g' | sed 's/^ *\(.*\) *\t *\(.*\) *$$/msgctxt "\2"\nmsgid "\1"\nmsgstr ""\n/') > $@

# gv tokens that are unchanged when translating to Irish
# as based on manually post-edited MT of usage file
unchanged.txt:
	cat toedit.txt | egrep -v '<div' | egrep -v '^\\n' | egrep '[A-Za-z]' | egrep '^(.+) => \1$$' | egrep -v '^[A-Z]' | sed 's/ =>.*//' | sort -u > $@

exact.txt:
	cat usage-gv.txt | cut -f 1 | lensort | tac | sed 's/[^A-Za-z]/./g' | head -n 500 | while read x; do egrep -i --color=always "$$x" ${HOME}/gaeilge/diolaim/x/Ba59; done > $@

militriu.txt:
	cat toedit.txt | egrep -v '^<' | perl ~/seal/caighdean/detokenize.pl -t | perl -I ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/lib ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/scripts/gram-ga.pl --ionchod=utf-8 --litriu | sort | uniq -c | sort -r -n | sed 's/^ *//' > $@

# first run militriu.txt, clean up and add to ~/.neamhshuim
gram.txt:
	cat toedit.txt | egrep -v '^<' | perl ~/seal/caighdean/detokenize.pl -t | perl -I ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/lib ${HOME}/gaeilge/gramadoir/gr/ga/Lingua-GA-Gramadoir/scripts/gram-ga.pl --ionchod=utf-8 > $@
