# Finds people in Catagóir:Daoine beo that are dead according to WD.
# Uses the full-text dump in ../olleagar which can be slightly out of date,
# so there could be a small number of false positives in problems.txt
# Usage:
# $ make clean
# $ make
all: problems.txt

daoinebeo-titles.txt: ../olleagar/ga.xml
	cat ../olleagar/ga.xml | tr "\r" " " | tr "\n" " " | tr "\t" " " | sed 's/<page>/\n&/g' | egrep -v -i '#(athsheoladh|redirect)' | egrep '[Cc]atagóir *: *Daoine beo[^A-Za-z]' | egrep -o '<title>[^<]+</title>' | sed 's/^<title>//' | sed 's/<\/title>//' > $@

dead.tsv: dead.pl
	perl dead.pl > $@

dead-titles.txt: dead.tsv
	cat dead.tsv | cut -f 3 > $@

problems.txt: dead-titles.txt daoinebeo-titles.txt
	cat daoinebeo-titles.txt | keepif dead-titles.txt > $@

clean:
	rm -f daoinebeo-titles.txt dead-titles.txt dead.tsv problems.txt
