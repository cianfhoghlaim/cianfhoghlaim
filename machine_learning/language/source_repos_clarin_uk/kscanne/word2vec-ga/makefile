CC = gcc
CFLAGS = -lm -pthread -Ofast -march=native -Wall -funroll-loops -Wno-unused-result

all: word2vec word2phrase distance word-analogy compute-accuracy

# trains model; see *.bin targets below
word2vec: word2vec.c
	$(CC) word2vec.c -o word2vec $(CFLAGS)

# joins common bigrams from plain text training data;
# see ga-train-phrase target below
word2phrase: word2phrase.c
	$(CC) word2phrase.c -o word2phrase $(CFLAGS)

# Usage:
# $ ./distance ga-vectors.bin
distance: distance.c
	$(CC) distance.c -o distance $(CFLAGS)

# Usage:
# $ ./word-analogy ga-vectors.bin
word-analogy: word-analogy.c
	$(CC) word-analogy.c -o word-analogy $(CFLAGS)

# Usage:
# $ ./compute-accuracy ga-vectors.bin 0 < questions-words.txt
# $ ./compute-accuracy ga-phrase2-vectors.bin 0 < questions-phrases.txt
# 0 here means no cutoff; typical value for faster eval would be ~30-50k
# See test-relations target below for example...
compute-accuracy: compute-accuracy.c
	$(CC) compute-accuracy.c -o compute-accuracy $(CFLAGS)
	chmod +x *.sh

test-relations: relations.txt expand.pl compute-accuracy ga-demutate-vectors.bin
	cat relations.txt | perl expand.pl | ./compute-accuracy ga-demutate-vectors.bin 0

clean:
	rm -f word2vec word2phrase distance word-analogy compute-accuracy

#####################################################
##### Targets below are for the maintainer only #####
#####################################################

classes.txt: word2vec ga-demutate-train
	time ./word2vec -train ga-demutate-train -output classes-temp.txt -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -iter 15 -classes 500
	sort classes-temp.txt -k 2 -n > $@
	rm -f classes-temp.txt

ga-vectors-200.bin: word2vec ga-train
	time ./word2vec -train ga-train -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15 -save-vocab ga-vocab.txt

ga-vectors-200.txt: word2vec ga-train
	time ./word2vec -train ga-train -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 0 -iter 15 -save-vocab ga-vocab.txt

ga-phrase-vectors-200.bin: word2vec ga-train-phrase
	time ./word2vec -train ga-train-phrase -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15

ga-phrase2-vectors-200.bin: word2vec ga-train-phrase2
	time ./word2vec -train ga-train-phrase2 -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15

ga-demutate-vectors-200.bin: word2vec ga-demutate-train
	time ./word2vec -train ga-demutate-train -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15 -save-vocab ga-demutate-vocab.txt

ga-demutate-vectors-200.txt: word2vec ga-demutate-train
	time ./word2vec -train ga-demutate-train -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 0 -iter 15 -save-vocab ga-demutate-vocab.txt

ga-demutate-vectors-300.bin: word2vec ga-demutate-train
	time ./word2vec -train ga-demutate-train -output $@ -cbow 1 -size 300 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15 -save-vocab ga-demutate-vocab.txt

ga-all-demutate-vectors-200.bin: word2vec ga-all-demutate-train
	time ./word2vec -train ga-all-demutate-train -output $@ -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15 -save-vocab ga-all-demutate-vocab.txt

# see https://wiki.apertium.org/wiki/UDPipe
# these settings recommended by UDPipe maintainers
# This gets copied to parsail/treebank/ga.vec
udpipe.vec: word2vec ga-train
	time ./word2vec -train ga-train -output $@ -cbow 0 -size 50 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 2

# see https://wiki.apertium.org/wiki/UDPipe
# these settings recommended by UDPipe maintainers
# Copied over to parsail/treebank/ga-sean.vec
udpipe-sean.vec: word2vec ga-sean-train
	time ./word2vec -train ga-sean-train -output $@ -cbow 0 -size 50 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 2

# Copied over to parsail/treebank/ga-uile.vec
udpipe-uile.vec: word2vec ga-uile
	time ./word2vec -train ga-uile -output $@ -cbow 0 -size 50 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 10

# for Sai/Jeff
ga-modern.vec: word2vec ga-train
	time ./word2vec -train ga-train -output $@ -cbow 0 -size 100 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 2

# min count of 40 gives vocab of about 56,000
ga-modern-common.vec: word2vec ga-train
	time ./word2vec -train ga-train -output $@ -cbow 0 -size 100 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 40

ga-older.vec: word2vec ga-sean-train
	time ./word2vec -train ga-sean-train -output $@ -cbow 0 -size 100 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 2

gd-modern.vec: word2vec gd-train
	time ./word2vec -train gd-train -output $@ -cbow 0 -size 100 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 2

# min count of 9 gives vocab of about 56,000 to match ga-modern-common
gd-modern-common.vec: word2vec gd-train
	time ./word2vec -train gd-train -output $@ -cbow 0 -size 100 -window 10 -negative 5 -hs 0 -sample 1e-1 -threads 12 -binary 0 -iter 15 -min-count 9

DIMENSION=200
WORDCOUNT=50000
projector-all: models/projector-ga-$(DIMENSION).tsv models/projector-metadata-ga.tsv

models/projector-ga-$(DIMENSION).tsv: ga-vectors-$(DIMENSION).txt
	cat ga-vectors-$(DIMENSION).txt | sed '1d' | head -n $(WORDCOUNT) | sed 's/^[^ ]* //' | tr " " "\t" > $@

models/projector-metadata-ga.tsv: ga-vocab.txt
	(echo "word freq"; cat ga-vocab.txt | head -n $(WORDCOUNT)) | tr " " "\t" > $@

ga-uile: ga-train ga-sean-train
	cat ga-train ga-sean-train > $@

ga-sean-train:
	cat ${HOME}/gaeilge/caighdean/prestandard/alltokens-order.txt | egrep -v '^\\n$$' | sed "s/^\([dbmsntl]\)'\(..*\)$$/\1'\n\2/" | tr "\n" " " > $@

ga-train:
	cat ${HOME}/seal/caighdean/model/alltokens.txt | sed "s/^\([dbmsntl]\)'\(..*\)$$/\1'\n\2/" | tr "\n" " " > $@

# should do an alltokens-order.txt target too.....
gd-train:
	cat ${HOME}/seal/idirlamha/gd/freq/alltokens-order.txt | tolow | egrep -v '^\\n$$' | sed "s/^\([adbmsntl]\|[bdt]h\)'\(..*\)$$/\1'\n\2/" | tr "\n" " " > $@

ga-train-phrase: ga-train word2phrase
	time ./word2phrase -train ga-train -output $@ -threshold 200 -debug 2

ga-train-phrase2: ga-train-phrase word2phrase
	time ./word2phrase -train ga-train-phrase -output $@ -threshold 200 -debug 2

ga-demutate-train:
	cat ${HOME}/seal/caighdean/model/alltokens-order.txt | sed "s/^\([dbmsntl]\)'\(..*\)$$/\1'\n\2/" | bash demutate.sh | tr "\n" " " > $@

ga-all-demutate-train:
	cat ${HOME}/seal/caighdean/model/alltokens-order.txt ${HOME}/gaeilge/caighdean/prestandard/alltokens-model.txt | sed "s/^\([dbmsntl]\)'\(..*\)$$/\1'\n\2/" | bash demutate.sh | tr "\n" " " > $@

relation-spelling:
	cat relations.txt | egrep -v '^:' | tr "\t" "\n" | sort -u | keepif -n ${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt

distclean:
	$(MAKE) clean
	rm -f classes.txt *.bin ga-train*

FORCE:
