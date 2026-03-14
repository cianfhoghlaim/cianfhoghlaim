
all: template.html lang/*.txt build.pl
	rm -Rf distro
	mkdir distro
	ls lang/*.txt | sed 's/^lang.//' | sed 's/\.txt//' | while read x; do cat lang/$$x.txt | perl build.pl > abhar.html; mkdir -p distro/$$x; sed '/^<body/r abhar.html' template.html | sed "s/TEANGA/`sed -n '1p' lang/$$x.txt`/" | sed "s/ACCORDIONS/`egrep -o 'acc[0-9]+' abhar.html | sort -u | wc -l`/" > distro/$$x/index.html; rm -f abhar.html; done

clean:
	rm -f index.html abhar.html
	rm -Rf distro

FORCE:
