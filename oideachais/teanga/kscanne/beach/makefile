# TO ADD A NEW LANGUAGE:
# (1) Add words-xx.txt target to makefile, and make it.
# (2) Add puzzles-xx.* target to makefile, and make it.
# (3) Add new langcode to regex in beach.cgi on borel, make check, p2cadhan,
#     then go to cadhan, make diff, sudo make install. Then back on borel,
#     perl client.pl xx
# (4) Update deploy.sh with localization strings, and then run it
# (5) Add a line to sionc to copy .hash file to cadhan
#
# TO REBUILD PUZZLES:
# $ rm -f puzzles-xx.json
# $ make puzzles-xx.json
# Then on cadhan.com
# $ sionc
# The point is that the .hash files are in production (at least
# after they're synced to cadhan), so shouldn't be deleted.
# NB: .json files are just for easy examination; not used in production at all.
# Don't make these 444 since we want them to be overwritten by build.pl
puzzles-ga.json puzzles-ga.hash:
	perl build.pl ga

puzzles-gd.json puzzles-gd.hash:
	perl build.pl gd

puzzles-en.json puzzles-en.hash:
	perl build.pl en

words-gd.txt: ${HOME}/seal/idirlamha/gd/beach/words-gd-edited.txt
	cp ${HOME}/seal/idirlamha/gd/beach/words-gd-edited.txt $@

# not used
mywords-gd.txt: ${HOME}/gaeilge/ga2gd/ga2gd/focloir.txt
	cat ${HOME}/gaeilge/ga2gd/ga2gd/focloir.txt | egrep '0$$' | cut -f 1 | sed 's/_.*//' | egrep -v "[A-Z '-]" | egrep '....' | sort -u > $@

words-en.txt: /usr/local/share/crubadan/en/GLAN
	cat /usr/local/share/crubadan/en/GLAN | LC_ALL=C egrep '^[a-z]+$$' | egrep '....' | sort -u > $@

# headwords only — seems to work best
GAELSPELL=${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt
words-ga.txt: ${HOME}/seal/ig7
	cat ${HOME}/seal/ig7 | egrep -v ' v \((láith|caite|faist|coinn)' | egrep -v '^(mb|gc|bhf|ng|dt|[dfgm]h)' | egrep -v ' a \(comp\)' | egrep -v ' n \(ds\)' | egrep -v ' npl.? \([dg]pl\)' | sed 's/\..*//' | egrep -v ' ' | egrep -v "[A-Zjkqwxyz'-]" | egrep '....' | sort -u | egrep -v '^(bheagnach|thiarcais)$$' | keepif ${GAELSPELL} > $@

# not used
full-ga.txt: ${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt
	cat ${HOME}/gaeilge/ispell/ispell-gaeilge/gaelspell.txt | egrep -v "[A-Z'-]" > $@

# not used
demutated-ga.txt: full-ga.txt
	cat full-ga.txt | demut | keepif full-ga.txt | sort -u > $@

# totally safe
clean:
	rm -f words-*.txt full-ga.txt demutated-ga.txt

# danger! messes with production
distclean:
	$(MAKE) clean
	rm -f puzzles*.json puzzles*.hash
