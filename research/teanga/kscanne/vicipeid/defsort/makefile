
all: people-easy.txt defart-easy.txt people-irish.txt existingprobs.txt lenited.txt

allpeople.tsv: people.pl
	perl people.pl > $@

allpeople-titles.txt: allpeople.tsv
	cat allpeople.tsv | cut -f 3 > $@

all-done.txt: ../olleagar/ga-full.tsv
	egrep -i '\{\{ *DEFAULTSORT *:' ../olleagar/ga-full.tsv | cut -f 1 > $@

people-done.txt: all-done.txt allpeople-titles.txt
	cat all-done.txt | keepif allpeople-titles.txt > $@

# egrep is there b/c people with one name don't need it (Madonna, Pink)
# so everyone in this file as 2,3,4+ names
people-todo.txt: people-done.txt allpeople-titles.txt
	cat allpeople-titles.txt | keepif -n people-done.txt | egrep '^[^(]+ [A-ZÁÉÍÓÚáéíóúa-zŻ]' > $@

# apparently just first+last, with some exceptions filtered out
people-easy.txt: people-todo.txt
	cat people-todo.txt  | egrep -v ' [^(]* ' | sed 's/^\([^ ]*\) \([^ ]*\).*$$/&\t\2, \1/' > $@

# Need to decide on convention for O' names (O'Reilly, OReilly, Reilly?)
people-irish.txt: people-todo.txt
	egrep ' (Ó|Ma[cg]|Ní|Ni[cg]|Ua|Mhic) ' people-todo.txt | sed '/ Ó h/s/^\(.*\) Ó h\([^(]*\).*/&\t\2, \1 Ó h/' | sed '/ Ó [^h]/s/^\(.*\) Ó \([^(]*\).*/&\t\2, \1 Ó/' | sed '/ Ua /s/^\(.*\) Ua \([^(]*\).*/&\t\2, \1 Ua/' | sed '/ Mac /s/^\(.*\) Mac \([^(]*\).*/&\t\2, \1 Mac/' | sed '/ Ní [BbCcDdFfGgMmPpSsTt]h/s/^\(.*\) Ní \(.\)h\([^(]*\).*/&\t\2\3, \1 Ní/' | sed '/ Nic [BbCcDdFfGgMmPpSsTt]h/s/^\(.*\) Nic \(.\)h\([^(]*\).*/&\t\2\3, \1 Nic/' | sed '/ Mhic [BbCcDdFfGgMmPpSsTt]h/s/^\(.*\) Mhic \(.\)h\([^(]*\).*/&\t\2\3, \1 Mhic/' | sed '/^[^\t]* \(Ní\|Nic\|Mhic\) [^\t]*$$/s/^\([^\t]*\) \(Ní\|Nic\|Mhic\) \([^(]*\).*/&\t\3, \1 \2/' | sed 's/ ,/,/' > $@

defart-titles.txt: ../olleagar/titles.txt
	egrep '^(An|Na|The) ' ../olleagar/titles.txt > $@

defart-todo.txt: defart-titles.txt all-done.txt
	cat defart-titles.txt | keepif -n all-done.txt > $@

defart-easy.txt: defart-todo.txt
	cat defart-todo.txt | sed '/^Na h-/s/^Na h-\([^(]*\).*/&\t\1, Na h-/' | sed '/^Na h[^-]/s/^Na h\([^(]*\).*/&\t\1, Na h/' | sed '/^Na [^h]/s/^Na \([^(]*\).*/&\t\1, Na/' | sed '/^An t-/s/^An t-\([^(]*\).*/&\t\1, An t-/' | sed '/^An t[AEIOUSÁÉÍÓÚÀÈÌÒÙ]/s/^An t\([^(]*\).*/&\t\1, An t/' | sed '/^An [BbCcFfGgMmPp]h/s/^An \(.\)h\([^(]*\).*/&\t\1\2, An/' | sed '/^An [^\t]*$$/s/^An \([^(]*\).*/&\t\1, An/' | sed '/^The [^\t]*$$/s/^The \([^(]*\).*/&\t\1, The/' | sed 's/ ,/,/' > $@

existingprobs.txt: ../olleagar/ga-full.tsv
	cat ../olleagar/ga-full.tsv | sed 's/\t/~/' | egrep "^[^~]* O['‘’][A-Z].+\{\{DEFAULTSORT *: *[A-NP-Za-z]" | sed 's/^\([^~]*\)~.*\({{DEFAULTSORT[^}]*}}\)/\1\t\2/' > $@
	cat ../olleagar/ga-full.tsv | sed 's/\t/~/' | egrep "\{\{DEFAULTSORT *: *(Ó|Ua|Ma[cg]|Ni[cg]|Ní|Uí|Mhic) " | sed 's/^\([^~]*\)~.*\([{][{]DEFAULTSORT[^}]*[}][}]\)/\1\t\2/' >> $@

lenited.txt: ../olleagar/ga-full.tsv
	cat ../olleagar/ga-full.tsv | sed 's/\t/~/' | egrep "^[^~]* (Ní|Uí|Mhic) .+\{\{DEFAULTSORT *: *[BCDFGMPST]h" | sed 's/^\([^~]*\)~.*\({{DEFAULTSORT[^}]*}}\)/\1\t\2/' > $@


clean:
	rm -f all-done.txt allpeople-titles.txt people-done.txt people-easy.txt people-todo.txt defart-easy.txt defart-titles.txt defart-todo.txt existingprobs.txt people-irish.txt lenited.txt

distclean:
	make clean
	rm -f allpeople.tsv
